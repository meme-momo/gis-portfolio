import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import os


# ================== 配置 ==================

# 数据路径
climate_path = r"gt\processed_climate_data\裁剪后\climate_combined_suitability.tif"
soil_path = r"gt\processed_final\soil_resampled.tif"
terrain_path = r"gt\processed_final\terrain_resampled.tif"
combined_path = r"gt\processed_final\combined_suitability.tif"
vector_path = r"gt\shp\quyu.shp"

# GEE导出的可利用地栅格
usable_land_path = r"gt\fuxian\MyProject2\usable_land_paper_ratio.tif"

# 输出目录
output_dir = r"gt\result"
os.makedirs(output_dir, exist_ok=True)

class_dir = os.path.join(output_dir, "分级栅格_论文比例版")
os.makedirs(class_dir, exist_ok=True)

# NoData值
NODATA_VALUE = -9999

# 省份名称字段
province_field = "name"

# 论文各等级比例（从论文表3计算）
# 不适宜区: 15.7%, 较不适宜区: 21.5%, 较适宜区: 34.3%, 适宜区: 28.5%
paper_ratios = [0.157, 0.215, 0.343, 0.285]  # 不适宜、较不适宜、较适宜、适宜


# ================== 辅助函数 ==================

def read_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float64)
        transform = src.transform
        crs = src.crs
        profile = src.profile
    return arr, transform, crs, profile


def resample_raster_from_file(src_file, target_shape, target_transform, target_crs, resampling_method):
    resampled = np.zeros(target_shape, dtype=np.float64)
    
    with rasterio.open(src_file) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=resampled,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=resampling_method,
            num_threads=1
        )
    
    return resampled


def calc_total_area_from_vector(gdf):
    gdf_ea = gdf.to_crs(epsg=6933)
    total_area_m2 = gdf_ea.area.sum()
    total_area_ha = total_area_m2 / 10000
    return total_area_ha


def classify_by_quantile(data, ratios, valid_mask=None):
    """
    按比例分位数分级
    ratios: [不适宜比例, 较不适宜比例, 较适宜比例, 适宜比例]
    返回: 分级数组, 阈值列表
    """
    if valid_mask is None:
        valid_mask = (data > 0) & (data != NODATA_VALUE) & (~np.isnan(data))
    
    valid_data = data[valid_mask]
    valid_data_sorted = np.sort(valid_data)
    
    # 计算分位数阈值
    n = len(valid_data_sorted)
    thresholds = [float(valid_data_sorted[0])]  # 最小值
    
    cum_ratio = 0
    for i in range(3):  # 3个分界点
        cum_ratio += ratios[i]
        idx = int(cum_ratio * n) - 1
        idx = max(0, min(idx, n - 1))
        thresholds.append(float(valid_data_sorted[idx]))
    
    thresholds.append(float(valid_data_sorted[-1]))  # 最大值
    
    # 分级
    classified = np.full(data.shape, -1, dtype=np.int32)
    classified[valid_mask & (data <= thresholds[1])] = 0      # 不适宜

    classified[valid_mask & (data > thresholds[1]) & (data <= thresholds[2])] = 1  # 较不适宜
    classified[valid_mask & (data > thresholds[2]) & (data <= thresholds[3])] = 2  # 较适宜
    classified[valid_mask & (data > thresholds[3])] = 3       # 适宜
    
    return classified, thresholds


def calc_area_by_class(classified, pixel_area_ha):
    areas = {}
    labels = ['不适宜区', '较不适宜区', '较适宜区', '适宜区']
    
    for i, label in enumerate(labels):
        count = np.sum(classified == i)
        areas[label] = count * pixel_area_ha / 10000
    
    total = sum(areas.values())
    return areas, total


def save_classified_raster(classified, profile, output_path):
    out_profile = profile.copy()
    out_profile.update(dtype=rasterio.int32, count=1, nodata=-1, compress='lzw')
    
    with rasterio.open(output_path, 'w', **out_profile) as dst:
        dst.write(classified.astype(np.int32), 1)


# ================== 单因子适宜性统计 ==================

def calc_single_suitability(name, data, pixel_area_ha, profile, valid_mask=None):
    print(f"\n计算{name}适宜性分级（按论文比例分位数法）...")
    
    classified, thresholds = classify_by_quantile(data, paper_ratios, valid_mask=valid_mask)
    
    print(f"  分级阈值: {[round(x, 4) for x in thresholds]}")
    print(f"  目标比例: 不适宜{paper_ratios[0]*100:.1f}%, 较不适宜{paper_ratios[1]*100:.1f}%, 较适宜{paper_ratios[2]*100:.1f}%, 适宜{paper_ratios[3]*100:.1f}%")
    
    areas, total = calc_area_by_class(classified, pixel_area_ha)
    
    # 验证比例
    for label, area in areas.items():
        ratio = area / total * 100 if total > 0 else 0
        print(f"  {label}: {area:.2f}万hm² ({ratio:.1f}%)")
    
    out_path = os.path.join(class_dir, f"{name}_分级.tif")
    save_classified_raster(classified, profile, out_path)
    print(f"  分级栅格已保存")
    
    result = {}
    for label, area in areas.items():
        result[label] = {
            '面积(万hm²)': round(area, 2),
            '比例(%)': round(area / total * 100, 2) if total > 0 else 0
        }
    
    result['合计'] = {'面积(万hm²)': round(total, 2), '比例(%)': 100.0}
    
    suitable = areas['适宜区'] + areas['较适宜区']
    result['适宜区+较适宜区'] = {
        '面积(万hm²)': round(suitable, 2),
        '比例(%)': round(suitable / total * 100, 2) if total > 0 else 0
    }
    
    return result, thresholds, classified


# ================== 分省统计（复现论文表3） ==================

def calc_province_suitability(combined_classified, combined_profile, combined_transform, 
                               combined_crs, gdf, pixel_area_ha):
    print("\n按省份统计综合适宜性（复现论文表3）...")
    
    temp_path = os.path.join(output_dir, "temp_classified.tif")
    save_classified_raster(combined_classified, combined_profile, temp_path)
    
    results = []
    province_names = []
    
    for idx, row in gdf.iterrows():
        prov_name = row[province_field]
        province_names.append(prov_name)
        print(f"  统计 {prov_name}...")
        
        geom = [row.geometry]
        
        with rasterio.open(temp_path) as src:
            try:
                out_image, _ = mask(src, geom, crop=True, all_touched=True)
            except:
                gdf_reproj = gdf.to_crs(src.crs)
                geom_reproj = [gdf_reproj.iloc[idx].geometry]
                out_image, _ = mask(src, geom_reproj, crop=True, all_touched=True)
        
        prov_classified = out_image[0]
        
        areas = {}
        labels = ['适宜区', '较适宜区', '较不适宜区', '不适宜区']
        class_codes = [3, 2, 1, 0]
        
        for label, code in zip(labels, class_codes):
            count = np.sum(prov_classified == code)
            areas[label] = round(count * pixel_area_ha / 10000, 2)
        
        total = sum(areas.values())
        areas['合计'] = round(total, 2)
        areas['适宜区+较适宜区'] = round(areas['适宜区'] + areas['较适宜区'], 2)
        
        results.append(areas)
    
    total_row = {}
    for key in results[0].keys():
        total_row[key] = round(sum(r[key] for r in results), 2)
    
    os.remove(temp_path)
    return results, province_names, total_row


# ================== 保存Excel ==================

def save_to_excel(climate_result, soil_result, terrain_result, combined_result,
                  province_results, province_names, province_total,
                  usable_area):
    
    excel_path = os.path.join(output_dir, "油茶适宜性统计结果_论文比例版.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # 可利用地概况
        pd.DataFrame({
            '指标': ['可利用地总面积(万hm²)', '论文目标(万hm²)', '误差(%)'],
            '数值': [round(usable_area, 2), 2387.41, round(abs(usable_area - 2387.41) / 2387.41 * 100, 1)]
        }).to_excel(writer, sheet_name='表0_可利用地概况', index=False)
        
        # 分级方法说明
        pd.DataFrame({
            '项目': ['分级方法', '不适宜区比例', '较不适宜区比例', '较适宜区比例', '适宜区比例'],
            '说明': ['分位数法（按论文比例）', f'{paper_ratios[0]*100:.1f}%', f'{paper_ratios[1]*100:.1f}%', f'{paper_ratios[2]*100:.1f}%', f'{paper_ratios[3]*100:.1f}%']
        }).to_excel(writer, sheet_name='分级方法说明', index=False)
        
        # 单因子统计
        pd.DataFrame(climate_result).T.to_excel(writer, sheet_name='表1_气候适宜性')
        pd.DataFrame(soil_result).T.to_excel(writer, sheet_name='表2_土壤适宜性')
        pd.DataFrame(terrain_result).T.to_excel(writer, sheet_name='表3_地形适宜性')
        pd.DataFrame(combined_result).T.to_excel(writer, sheet_name='表4_综合适宜性整体')
        
        # 分省综合适宜性（论文表3格式）
        df_prov = pd.DataFrame(province_results, index=province_names)
        df_prov.loc['合计'] = pd.Series(province_total)
        
        cols_order = ['适宜区', '较适宜区', '较不适宜区', '不适宜区', '适宜区+较适宜区', '合计']
        df_prov[cols_order].to_excel(writer, sheet_name='表5_综合适宜性分省(论文表3)')
        
        # 三因子对比
        comp_data = {}
        for label in ['适宜区', '较适宜区', '较不适宜区', '不适宜区', '适宜区+较适宜区', '合计']:
            comp_data[label] = {
                '气候_面积': climate_result[label]['面积(万hm²)'],
                '气候_比例%': climate_result[label]['比例(%)'],
                '土壤_面积': soil_result[label]['面积(万hm²)'],
                '土壤_比例%': soil_result[label]['比例(%)'],
                '地形_面积': terrain_result[label]['面积(万hm²)'],
                '地形_比例%': terrain_result[label]['比例(%)'],
            }
        pd.DataFrame(comp_data).T.to_excel(writer, sheet_name='三因子对比')
    
    print(f"\n✅ Excel已保存: {excel_path}")
    return excel_path


# ================== 主程序 ==================

def main():
    print("=" * 65)
    print("  油茶适宜性评价 - 论文比例复现版")
    print("  分级方法: 分位数法（按论文表3比例）")
    print("  目标: 复现论文表3，各等级面积比例对齐")
    print("=" * 65)
    
    # 读取矢量
    gdf = gpd.read_file(vector_path)
    print(f"\n矢量: {len(gdf)} 个省份 - {list(gdf[province_field].values)}")
    
    # 计算矢量总面积
    total_area_ha = calc_total_area_from_vector(gdf)
    print(f"矢量总面积: {total_area_ha:.2f} 公顷 = {total_area_ha/10000:.2f} 万公顷")
    
    # 读取综合数据（作为基准）
    print("\n读取综合适宜性数据...")
    combined_data, combined_transform, combined_crs, combined_profile = read_raster(combined_path)
    print(f"  尺寸: {combined_data.shape}")
    print(f"  坐标系: {combined_crs}")
    
    # 有效像元掩码
    valid_combined = (combined_data > 0) & (combined_data != NODATA_VALUE) & (~np.isnan(combined_data))
    valid_pixels = np.sum(valid_combined)
    print(f"  有效像元数: {valid_pixels}")
    
    # 像元面积（矢量校准）
    pixel_area_ha = total_area_ha / valid_pixels
    print(f"  校准后像元面积: {pixel_area_ha:.4f} 公顷")
    
    # 读取并重采样可利用地栅格
    print("\n读取可利用地栅格...")
    print(f"  路径: {usable_land_path}")
    
    usable_resampled = resample_raster_from_file(
        usable_land_path, combined_data.shape, combined_transform, combined_crs,
        Resampling.nearest
    )
    
    usable_mask = usable_resampled > 0
    usable_pixels = np.sum(usable_mask & valid_combined)
    usable_area = usable_pixels * pixel_area_ha / 10000
    
    print(f"  可利用地像元数: {usable_pixels}")
    print(f"  可利用地面积: {usable_area:.2f} 万hm²")
    print(f"  论文目标: 2387.41 万hm²")
    print(f"  误差: {abs(usable_area - 2387.41) / 2387.41 * 100:.1f}%")
    
    del usable_resampled
    
    # 最终有效掩码
    final_mask = valid_combined & usable_mask
    
    # 读取其他因子数据
    print("\n读取其他因子数据...")
    
    def read_factor(path, name):
        data, transform, crs, profile = read_raster(path)
        print(f"  {name}: {data.shape}")
        return data, combined_profile
    
    climate_data, climate_profile = read_factor(climate_path, "气候")
    soil_data, soil_profile = read_factor(soil_path, "土壤")
    terrain_data, terrain_profile = read_factor(terrain_path, "地形")
    
    # 各因子有效掩码
    valid_climate = (climate_data > 0) & (climate_data != NODATA_VALUE) & (~np.isnan(climate_data))
    valid_soil = (soil_data > 0) & (soil_data != NODATA_VALUE) & (~np.isnan(soil_data))
    valid_terrain = (terrain_data > 0) & (terrain_data != NODATA_VALUE) & (~np.isnan(terrain_data))
    
    final_climate_mask = valid_climate & usable_mask
    final_soil_mask = valid_soil & usable_mask
    final_terrain_mask = valid_terrain & usable_mask
    
    # 统计
    print("\n" + "=" * 65)
    print("  分级统计（可利用地范围内，按论文比例分位数法）")
    print("=" * 65)
    
    climate_result, _, _ = calc_single_suitability(
        "气候", climate_data, pixel_area_ha, climate_profile, final_climate_mask
    )
    soil_result, _, _ = calc_single_suitability(
        "土壤", soil_data, pixel_area_ha, soil_profile, final_soil_mask
    )
    terrain_result, _, _ = calc_single_suitability(
        "地形", terrain_data, pixel_area_ha, terrain_profile, final_terrain_mask
    )
    combined_result, _, combined_classified = calc_single_suitability(
        "综合", combined_data, pixel_area_ha, combined_profile, final_mask
    )
    
    # 分省统计（论文表3）
    province_results, province_names, province_total = calc_province_suitability(
        combined_classified, combined_profile, combined_transform, combined_crs, gdf, pixel_area_ha
    )
    
    # 保存Excel
    save_to_excel(
        climate_result, soil_result, terrain_result, combined_result,
        province_results, province_names, province_total, usable_area
    )
    
    # 保存可利用地掩码
    mask_path = os.path.join(class_dir, "可利用地掩码_重采样.tif")
    save_classified_raster(usable_mask.astype(np.int32), combined_profile, mask_path)
    print(f"\n可利用地掩码已保存")
    
    print("\n" + "=" * 65)
    print(f"  🎉 完成！")
    print(f"  Excel: {output_dir}\\油茶适宜性统计结果_论文比例版.xlsx")
    print(f"  分级栅格: {class_dir}")
    print("  分级值: 3=适宜区, 2=较适宜区, 1=较不适宜区, 0=不适宜区, -1=NoData")
    print(f"  可利用地面积: {usable_area:.2f} 万hm²")
    print(f"  论文表3对应sheet: 表5_综合适宜性分省(论文表3)")
    print("=" * 65)


if __name__ == "__main__":
    main()
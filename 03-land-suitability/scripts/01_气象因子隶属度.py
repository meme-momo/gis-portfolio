import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import os
from glob import glob

# ================== 配置参数 ==================

# 气象数据文件夹（2000-2020年，每年一个tif，每个tif有6个波段）
climate_dir = r"gt\Camellia_Climat\Camellia_Climate"

# 矢量边界路径
vector_path = r"gt\shp\quyu.shp"

# 输出文件夹
output_dir = r"gt\processed_climate_data"
os.makedirs(output_dir, exist_ok=True)

# 6个波段对应的因子名称（按波段顺序）
band_names = {
    1: "MAT",     # 年均温
    2: "TJAN",    # 1月均温
    3: "TJUL",    # 7月均温
    4: "TOND",    # 10-12月均温
    5: "MAP",     # 年降水量
    6: "GDD10",   # ≥10℃活动积温
}

# NoData 值（根据实际数据调整）
NODATA_VALUE = -9999

# ================== 隶属函数定义 ==================

def calculate_s_type(data, a, d):
    """
    S型隶属度（越大越适宜）
    小于a => 0.1；大于d => 1.0；中间线性插值
    """
    result = np.full_like(data, 0.1, dtype=np.float32)
    result[data >= d] = 1.0
    mask_valid = (data > a) & (data < d)
    result[mask_valid] = 0.9 * ((data[mask_valid] - a) / (d - a)) + 0.1
    # NoData 设为 NaN
    result[data <= NODATA_VALUE] = np.nan
    result[np.isnan(data)] = np.nan
    return result


def calculate_parabola_type(data, a, b, c, d):
    """
    抛物线型隶属度（中间最佳，两边递减）
    x<=a => 0.1；a<x<b => 上升；b<=x<=c => 1.0；c<x<d => 下降；x>=d => 0.1
    """
    result = np.full_like(data, 0.1, dtype=np.float32)
    # 上升段
    mask1 = (data > a) & (data < b)
    result[mask1] = 0.9 * ((data[mask1] - a) / (b - a)) + 0.1
    # 最佳段
    mask2 = (data >= b) & (data <= c)
    result[mask2] = 1.0
    # 下降段
    mask3 = (data > c) & (data < d)
    result[mask3] = 0.9 * ((d - data[mask3]) / (d - c)) + 0.1
    # NoData
    result[data <= NODATA_VALUE] = np.nan
    result[np.isnan(data)] = np.nan
    return result


# ================== 步骤1：计算多年平均 ==================

def compute_multiyear_mean_by_band(climate_folder):
    """
    读取文件夹下所有6波段tif，计算每个波段的多年平均
    返回: (6, H, W) 平均数组, profile
    """
    tif_files = sorted(glob(os.path.join(climate_folder, "*.tif")))
    if len(tif_files) == 0:
        tif_files = sorted(glob(os.path.join(climate_folder, "*.img")))
    
    if len(tif_files) == 0:
        raise FileNotFoundError(f"在 {climate_folder} 中未找到栅格文件")
    
    print(f"找到 {len(tif_files)} 个气象数据文件")
    
    sum_bands = None
    profile = None
    count = 0
    
    for f in tif_files:
        with rasterio.open(f) as src:
            n_bands = src.count
            if n_bands != 6:
                print(f"  ⚠️  {os.path.basename(f)} 有 {n_bands} 个波段，跳过")
                continue
            
            if sum_bands is None:
                sum_bands = np.zeros((n_bands, src.height, src.width), dtype=np.float64)
                profile = src.profile
            
            # 逐波段读取并累加
            for b in range(1, n_bands + 1):
                arr = src.read(b).astype(np.float64)
                valid_mask = arr > NODATA_VALUE
                arr[~valid_mask] = 0
                sum_bands[b - 1] += arr
            
            count += 1
            print(f"  已处理: {os.path.basename(f)}")
    
    if count == 0:
        raise RuntimeError("没有有效的6波段数据文件")
    
    mean_bands = sum_bands / count
    print(f"\n✅ 多年平均计算完成，共 {count} 年数据")
    
    return mean_bands, profile


# ================== 步骤2：用矢量裁剪 ==================

def clip_raster_by_vector(band_arrays, profile, vector_gdf, output_dir):
    """
    用矢量边界裁剪6波段多年平均栅格
    返回: {波段名: 数组}, 裁剪后的profile
    """
    print("\n正在用矢量边界裁剪...")
    
    # 先保存为临时多波段文件
    temp_path = os.path.join(output_dir, "temp_multiyear_mean.tif")
    temp_profile = profile.copy()
    temp_profile.update(dtype=rasterio.float32, count=6, compress='lzw')
    
    with rasterio.open(temp_path, 'w', **temp_profile) as dst:
        for b in range(6):
            dst.write(band_arrays[b].astype(np.float32), b + 1)
    
    # 裁剪
    with rasterio.open(temp_path) as src:
        vector_reproj = vector_gdf.to_crs(src.crs)
        geoms = vector_reproj.geometry.values
        
        out_image, out_transform = mask(src, geoms, crop=True, all_touched=True)
        
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "dtype": rasterio.float32,
            "count": 6,
            "compress": "lzw"
        })
    
    # 保存裁剪后的多年平均
    clipped_mean_path = os.path.join(output_dir, "clipped_multiyear_mean.tif")
    with rasterio.open(clipped_mean_path, 'w', **out_meta) as dst:
        dst.write(out_image)
    
    print(f"  裁剪后的多年平均已保存 -> {clipped_mean_path}")
    
    # 按波段名返回字典
    result = {}
    for b in range(1, 7):
        name = band_names[b]
        result[name] = out_image[b - 1]
    
    return result, out_meta


# ================== 步骤3：计算隶属度 ==================

def compute_membership(mean_data, ref_profile):
    """
    计算6个指标的隶属度
    """
    membership = {}
    
    # 1. MAT 年均温 - S型 (a=14, d=19)
    print("\n1. MAT 年均温 - S型 (a=14, d=19)")
    membership["MAT"] = calculate_s_type(mean_data["MAT"], a=14.0, d=19.0)
    
    # 2. TJAN 1月均温 - S型 (a=5, d=10)
    print("2. TJAN 1月均温 - S型 (a=5, d=10)")
    membership["TJAN"] = calculate_s_type(mean_data["TJAN"], a=5.0, d=10.0)
    
    # 3. TJUL 7月均温 - 抛物线型 (a=20, b=25, c=28, d=28)
    print("3. TJUL 7月均温 - 抛物线型 (a=20, b=25, c=28, d=28)")
    membership["TJUL"] = calculate_parabola_type(mean_data["TJUL"], a=20.0, b=25.0, c=28.0, d=28.0)
    
    # 4. TOND 10-12月均温 - S型 (a=10, d=14)
    print("4. TOND 10-12月均温 - S型 (a=10, d=14)")
    membership["TOND"] = calculate_s_type(mean_data["TOND"], a=10.0, d=14.0)
    
    # 5. MAP 年降水量 - S型 (a=800, d=1500)
    print("5. MAP 年降水量 - S型 (a=800, d=1500)")
    membership["MAP"] = calculate_s_type(mean_data["MAP"], a=800.0, d=1500.0)
    
    # 6. GDD10 ≥10℃活动积温 - S型 (a=4250, d=5500)
    print("6. GDD10 ≥10℃活动积温 - S型 (a=4250, d=5500)")
    membership["GDD10"] = calculate_s_type(mean_data["GDD10"], a=4250.0, d=5500.0)
    
    # 保存每个隶属度栅格
    out_profile = ref_profile.copy()
    out_profile.update(count=1, dtype=rasterio.float32, compress='lzw')
    
    for name, arr in membership.items():
        out_path = os.path.join(output_dir, f"membership_{name}.tif")
        with rasterio.open(out_path, 'w', **out_profile) as dst:
            dst.write(arr, 1)
        print(f"   保存 -> membership_{name}.tif")
    
    return membership


# ================== 步骤4：气候综合适宜性 ==================

def compute_climate_suitability(membership, ref_profile):
    """
    气候综合适宜性 = 6个隶属度连乘后开6次方（几何平均）
    """
    print("\n" + "=" * 50)
    print("计算气候综合适宜性...")
    
    mem_list = list(membership.values())
    
    # 处理NoData：NaN替换为0.1
    for i in range(len(mem_list)):
        mem_list[i] = np.nan_to_num(mem_list[i], nan=0.1)
        mem_list[i] = np.clip(mem_list[i], 0.1, 1.0)
    
    # 连乘
    product = np.ones_like(mem_list[0], dtype=np.float64)
    for mem in mem_list:
        product *= mem
    
    # 开6次方
    climate_suit = (product ** (1.0 / 6.0)).astype(np.float32)
    
    # 保存
    out_path = os.path.join(output_dir, "climate_combined_suitability.tif")
    out_profile = ref_profile.copy()
    out_profile.update(count=1, dtype=rasterio.float32, compress='lzw')
    
    with rasterio.open(out_path, 'w', **out_profile) as dst:
        dst.write(climate_suit, 1)
    
    # 统计
    valid = climate_suit[climate_suit > 0.1]
    print(f"\n✅ 气候综合适宜性计算完成！")
    print(f"   结果 -> {out_path}")
    print(f"   范围: {np.min(valid):.4f} ~ {np.max(valid):.4f}")
    print(f"   均值: {np.mean(valid):.4f}")
    print(f"   中位数: {np.median(valid):.4f}")
    
    return climate_suit


# ================== 主程序 ==================

def main():
    print("=" * 60)
    print("  油茶气候适宜性评价 - 隶属度计算")
    print("  因子: MAT, TJAN, TJUL, TOND, MAP, GDD10")
    print("=" * 60)
    
    # 步骤1：计算多年平均
    print("\n【步骤1】计算2000-2020年多年平均")
    print("-" * 50)
    mean_bands, profile = compute_multiyear_mean_by_band(climate_dir)
    
    # 打印各因子范围
    print("\n各因子多年平均范围：")
    for b in range(1, 7):
        name = band_names[b]
        arr = mean_bands[b - 1]
        valid = arr[arr > NODATA_VALUE]
        if len(valid) > 0:
            print(f"  {name}: {np.min(valid):.2f} ~ {np.max(valid):.2f}")
    
    # 步骤2：裁剪
    print("\n\n【步骤2】用研究区矢量裁剪")
    print("-" * 50)
    gdf = gpd.read_file(vector_path)
    print(f"矢量边界: {vector_path}")
    print(f"包含 {len(gdf)} 个要素")
    
    clipped_mean, clipped_profile = clip_raster_by_vector(mean_bands, profile, gdf, output_dir)
    
    # 步骤3：计算隶属度
    print("\n\n【步骤3】计算各指标隶属度")
    print("-" * 50)
    membership = compute_membership(clipped_mean, clipped_profile)
    
    # 步骤4：气候综合适宜性
    print("\n\n【步骤4】气候综合适宜性")
    print("-" * 50)
    compute_climate_suitability(membership, clipped_profile)
    
    # 删除临时文件
    temp_path = os.path.join(output_dir, "temp_multiyear_mean.tif")
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    print("\n" + "=" * 60)
    print("  🎉 全部完成！")
    print(f"  输出目录: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
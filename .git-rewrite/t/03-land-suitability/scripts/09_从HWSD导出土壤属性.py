import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd
from rasterio.mask import mask
import os

# ================== 配置参数 ==================
# 1. 数据路径
hwds_folder = r"gt\基于世界土壤数据库（HWSD）的中国土壤数据集(v1.1)（2009）\HWSD_China_Subset_v1.1"
raster_path = os.path.join(hwds_folder, "HWSD_China_Albers.img")   # 或 HWSD_China_Geo.img
mdb_path = os.path.join(hwds_folder, "HWSD.mdb")                   # 属性数据库

# 2. 矢量边界路径（用户提供的7省或研究区边界，支持 .shp / .geojson）
vector_path = r"gt\shp\quyu.shp"   # 请改为你的实际文件路径

# 3. 输出文件夹
output_dir = r"gt\processed_soil_data"
os.makedirs(output_dir, exist_ok=True)

# ================== 辅助函数 ==================
def extract_soil_properties(mdb_file, csv_output="HWSD_DATA.csv"):
    """
    从 HWSD.mdb 导出属性表为 CSV，并返回包含 MU_GLOBAL, T_OC, T_PH_H2O, REF_DEPTH 的 DataFrame
    （如果已有 CSV，可跳过导出步骤）
    """
    # 由于 Python 直接读取 MDB 较复杂，建议用户先将 mdb 中的 HWSD_DATA 表导出为 CSV
    # 这里检测是否存在导出的 CSV 文件，若不存在则提示
    if not os.path.exists(csv_output):
        print(f"⚠️ 请先在 Access 中打开 {mdb_file}，将 'HWSD_DATA' 表导出为 '{csv_output}'。")
        print("  导出后重新运行本脚本。")
        exit()
    
    # 读取 CSV
    df = pd.read_csv(csv_output)
    required_cols = ['MU_GLOBAL', 'T_OC', 'T_PH_H2O', 'REF_DEPTH']
    df = df[required_cols].drop_duplicates(subset=['MU_GLOBAL'])
    return df

def clip_raster_with_vector(raster_path, vector_gdf, output_path):
    """
    用矢量边界裁剪栅格，并统一坐标系
    """
    with rasterio.open(raster_path) as src:
        # 将矢量重投影到栅格的坐标系
        vector_reprojected = vector_gdf.to_crs(src.crs)
        geoms = vector_reprojected.geometry.values
        
        # 裁剪
        out_image, out_transform = mask(src, geoms, crop=True, all_touched=True)
        
        # 更新元数据
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "crs": src.crs
        })
        
        # 保存
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)
        print(f"✅ 裁剪完成 -> {output_path}")

# ================== 主程序 ==================
def main():
    print("=" * 50)
    print("开始处理 HWSD 土壤数据...")
    print("=" * 50)

    # 步骤1: 读取土壤属性表（假设已导出为 CSV）
    csv_file = os.path.join(hwds_folder, "HWSD_DATA.csv")
    df_soil = extract_soil_properties(mdb_path, csv_file)
    print(f"加载土壤属性表，共 {len(df_soil)} 条记录。")

    # 步骤2: 读取栅格并计算三个指标
    with rasterio.open(raster_path) as src:
        mu_arr = src.read(1)       # 土壤单元代码
        profile = src.profile
        height, width = src.shape
        crs = src.crs
        
        # 建立映射字典
        mu_to_oc = dict(zip(df_soil['MU_GLOBAL'], df_soil['T_OC']))
        mu_to_ph = dict(zip(df_soil['MU_GLOBAL'], df_soil['T_PH_H2O']))
        mu_to_depth = dict(zip(df_soil['MU_GLOBAL'], df_soil['REF_DEPTH']))
        
        # 初始化数组（设为 NaN）
        organic_arr = np.full((height, width), np.nan, dtype=np.float32)
        ph_arr = np.full((height, width), np.nan, dtype=np.float32)
        depth_arr = np.full((height, width), np.nan, dtype=np.float32)
        
        # 平坦化数组以加快循环
        flat_mu = mu_arr.flatten()
        flat_org = organic_arr.flatten()
        flat_ph = ph_arr.flatten()
        flat_depth = depth_arr.flatten()
        
        # 逐像素赋值
        for i, mu_code in enumerate(flat_mu):
            if mu_code != 0 and mu_code in mu_to_oc:   # 0 表示海洋或无效
                # 获取属性值
                oc = mu_to_oc[mu_code]          # g/kg
                ph = mu_to_ph[mu_code]
                depth = mu_to_depth[mu_code]    # cm
                
                # 计算有机质（%）：S_m = S_e * 1.724，且 S_e 单位 g/kg 转换为 %
                # 1% = 10 g/kg，所以除以10
                organic_percent = (oc * 1.724) / 10.0
                
                flat_org[i] = organic_percent
                flat_ph[i] = ph
                flat_depth[i] = depth
        
        # 还原形状
        organic_arr = flat_org.reshape(height, width)
        ph_arr = flat_ph.reshape(height, width)
        depth_arr = flat_depth.reshape(height, width)

        # 保存临时未裁剪的栅格（可选）
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        profile.update(dtype=rasterio.float32, compress='lzw')
        
        with rasterio.open(os.path.join(temp_dir, "organic_1km.tif"), 'w', **profile) as dst:
            dst.write(organic_arr, 1)
        with rasterio.open(os.path.join(temp_dir, "ph_1km.tif"), 'w', **profile) as dst:
            dst.write(ph_arr, 1)
        with rasterio.open(os.path.join(temp_dir, "depth_1km.tif"), 'w', **profile) as dst:
            dst.write(depth_arr, 1)
        print("已生成未裁剪的土壤指标栅格（临时）。")

    # 步骤3: 使用矢量边界进行裁剪
    print("\n读取矢量边界...")
    gdf = gpd.read_file(vector_path)
    print(f"矢量边界坐标系: {gdf.crs}")
    print(f"矢量包含 {len(gdf)} 个多边形。")

    # 裁剪三个栅格
    files_to_clip = [
        os.path.join(temp_dir, "organic_1km.tif"),
        os.path.join(temp_dir, "ph_1km.tif"),
        os.path.join(temp_dir, "depth_1km.tif")
    ]
    
    for src_path in files_to_clip:
        name = os.path.basename(src_path).replace("_1km.tif", "")
        out_path = os.path.join(output_dir, f"clipped_{name}_1km.tif")
        clip_raster_with_vector(src_path, gdf, out_path)

    print("\n🎉 所有土壤数据处理完成！")
    print(f"结果保存在: {output_dir}")

if __name__ == "__main__":
    main()
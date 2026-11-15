import os
import glob
import rasterio
from rasterio.mask import mask
import geopandas as gpd

# ================== 配置 ==================

# 要裁剪的栅格文件夹（里面放所有待裁剪的tif）
input_folder = r"F:\gt\processed_climate_data"

# 输出文件夹（裁剪后的结果放这里）
output_folder = r"F:\gt\processed_climate_data\裁剪后"
os.makedirs(output_folder, exist_ok=True)

# 矢量边界
vector_path = r"F:\gt\shp\quyu.shp"

# ================== 主程序 ==================

def main():
    # 读取矢量
    gdf = gpd.read_file(vector_path)
    print(f"矢量边界: {vector_path}")
    print(f"包含 {len(gdf)} 个要素\n")
    
    # 找所有tif
    tif_files = glob.glob(os.path.join(input_folder, "*.tif"))
    if len(tif_files) == 0:
        tif_files = glob.glob(os.path.join(input_folder, "*.img"))
    
    print(f"找到 {len(tif_files)} 个栅格文件\n")
    
    # 逐个裁剪
    for i, tif_path in enumerate(tif_files, 1):
        filename = os.path.basename(tif_path)
        print(f"[{i}/{len(tif_files)}] 裁剪: {filename}")
        
        with rasterio.open(tif_path) as src:
            # 矢量转成栅格的坐标系（你说坐标系一致，这步其实可以跳过，但留着保险）
            gdf_reproj = gdf.to_crs(src.crs)
            geoms = gdf_reproj.geometry.values
            
            # 裁剪，crop=True 会把外面裁掉，只保留范围内的
            out_image, out_transform = mask(
                src, geoms, 
                crop=True, 
                all_touched=True,
                nodata=-9999
            )
            
            # 更新元数据
            out_meta = src.meta.copy()
            out_meta.update({
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": -9999
            })
            
            # 保存
            out_path = os.path.join(output_folder, filename)
            with rasterio.open(out_path, 'w', **out_meta) as dst:
                dst.write(out_image)
        
        print(f"  ✓ 已保存 -> {os.path.basename(out_path)}")
    
    print("\n" + "=" * 50)
    print(f"✅ 全部裁剪完成！共 {len(tif_files)} 个文件")
    print(f"输出目录: {output_folder}")
    print("=" * 50)

if __name__ == "__main__":
    main()
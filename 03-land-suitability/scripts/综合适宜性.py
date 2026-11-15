import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import os

# ================== 配置 ==================

# 三个综合适宜性图层
climate_path = r"F:\gt\processed_climate_data\裁剪后\climate_combined_suitability.tif"
soil_path = r"F:\gt\processed_soil_data\裁剪后\soil_combined_suitability.tif"
terrain_path = r"F:\gt\processed_terrain_data\裁剪后\terrain_combined_suitability.tif"

# 输出目录
output_dir = r"F:\gt\processed_final"
os.makedirs(output_dir, exist_ok=True)

# 目标分辨率（以气候图层为参考，也可以自己设）
# 如果想统一到1km，把 target_res 改成 1000
target_res = None  # None表示用气候图层的分辨率

NODATA_VALUE = -9999

# ================== 重采样函数 ==================

def resample_to_reference(src_path, ref_profile, ref_transform, ref_width, ref_height):
    """
    将栅格重采样到参考栅格的范围和分辨率
    """
    with rasterio.open(src_path) as src:
        src_data = src.read(1).astype(np.float64)
        src_data[src_data <= NODATA_VALUE] = np.nan
        
        dst_data = np.zeros((ref_height, ref_width), dtype=np.float64)
        
        reproject(
            source=src_data,
            destination=dst_data,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=np.nan,
            dst_transform=ref_transform,
            dst_crs=ref_profile['crs'],
            dst_nodata=np.nan,
            resampling=Resampling.bilinear  # 双线性插值，适合连续数据
        )
        
        return dst_data

# ================== 主程序 ==================

def main():
    print("=" * 55)
    print("  油茶土地综合适宜性计算")
    print("=" * 55)
    
    # 读取气候图层作为参考
    print("\n读取气候图层（作为参考分辨率）...")
    with rasterio.open(climate_path) as src:
        ref_profile = src.profile
        ref_transform = src.transform
        ref_width = src.width
        ref_height = src.height
        ref_crs = src.crs
        climate = src.read(1).astype(np.float64)
    
    # 计算像元大小
    pixel_size = abs(ref_transform[0])
    print(f"  尺寸: {ref_height} × {ref_width}")
    print(f"  像元大小: {pixel_size:.2f}")
    
    # 处理气候的NoData
    climate[climate <= NODATA_VALUE] = np.nan
    
    # 重采样土壤
    print("\n重采样土壤数据...")
    soil = resample_to_reference(soil_path, ref_profile, ref_transform, ref_width, ref_height)
    print(f"  完成，尺寸: {soil.shape}")
    
    # 重采样地形
    print("\n重采样地形数据...")
    terrain = resample_to_reference(terrain_path, ref_profile, ref_transform, ref_width, ref_height)
    print(f"  完成，尺寸: {terrain.shape}")
    
    # 限制在0.1~1.0范围
    climate = np.clip(climate, 0.1, 1.0)
    soil = np.clip(soil, 0.1, 1.0)
    terrain = np.clip(terrain, 0.1, 1.0)
    
    # 用气候的有效区域做掩膜（确保三个图层的有效区域一致）
    valid_mask = ~np.isnan(climate)
    soil[~valid_mask] = np.nan
    terrain[~valid_mask] = np.nan
    
    # 计算综合适宜性
    print("\n计算综合适宜性...")
    print("  公式：(气候^6 × 土壤^3 × 地形^3) 开12次方")
    
    product_all = (np.nan_to_num(climate, nan=0.1) ** 6) * \
                  (np.nan_to_num(soil, nan=0.1) ** 3) * \
                  (np.nan_to_num(terrain, nan=0.1) ** 3)
    
    combined = product_all ** (1.0 / 12.0)
    
    # 无效区域设为NoData
    combined[~valid_mask] = NODATA_VALUE
    combined = combined.astype(np.float32)
    
    # 保存综合适宜性
    output_path = os.path.join(output_dir, "combined_suitability.tif")
    out_profile = ref_profile.copy()
    out_profile.update(dtype=rasterio.float32, count=1, nodata=NODATA_VALUE, compress='lzw')
    
    with rasterio.open(output_path, 'w', **out_profile) as dst:
        dst.write(combined, 1)
    
    # 统计
    valid = combined[combined > 0.1]
    print(f"\n✅ 综合适宜性计算完成！")
    print(f"  结果 -> {output_path}")
    print(f"  分辨率: {pixel_size:.2f}")
    print(f"  范围: {np.min(valid):.4f} ~ {np.max(valid):.4f}")
    print(f"  均值: {np.mean(valid):.4f}")
    print(f"  中位数: {np.median(valid):.4f}")
    
    # 分级统计
    total_valid = len(valid)
    print(f"\n  适宜性分级（参考）:")
    print(f"    高度适宜 (>0.7):      {np.sum(combined > 0.7) / total_valid * 100:.1f}%")
    print(f"    中度适宜 (0.5~0.7):   {np.sum((combined > 0.5) & (combined <= 0.7)) / total_valid * 100:.1f}%")
    print(f"    低度适宜 (0.3~0.5):   {np.sum((combined > 0.3) & (combined <= 0.5)) / total_valid * 100:.1f}%")
    print(f"    不适宜 (<=0.3):       {np.sum((combined > 0.1) & (combined <= 0.3)) / total_valid * 100:.1f}%")
    
    # 保存重采样后的土壤和地形（可选，方便检查）
    print("\n保存重采样后的中间文件...")
    for name, data in [("soil_resampled", soil), ("terrain_resampled", terrain)]:
        p = out_profile.copy()
        data_out = data.copy()
        data_out[np.isnan(data_out)] = NODATA_VALUE
        with rasterio.open(os.path.join(output_dir, f"{name}.tif"), 'w', **p) as dst:
            dst.write(data_out.astype(np.float32), 1)
        print(f"  {name}.tif")
    
    print("\n" + "=" * 55)
    print("  🎉 全部完成！")
    print(f"  输出目录: {output_dir}")
    print("=" * 55)

if __name__ == "__main__":
    main()
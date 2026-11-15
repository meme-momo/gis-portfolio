import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import os
import shutil

# ================== 配置参数 ==================

dem_path = r"gt\DEM_WGS84_90m.tif"
vector_path = r"gt\shp\quyu.shp"
output_dir = r"gt\processed_terrain_data"
os.makedirs(output_dir, exist_ok=True)

NODATA_VALUE = -9999

# ================== 坡度坡向计算 ==================

def calculate_slope_aspect(dem_array, transform):
    """
    从DEM计算坡度和坡向（WGS84自动转米）
    返回: 坡度（度）、坡向（度，0°=北，顺时针）
    """
    rows, cols = dem_array.shape
    dx_deg = transform[0]
    dy_deg = -transform[4]
    
    # WGS84: 度转米
    lat_mid = transform[3] - (rows * dy_deg) / 2
    dx_m = abs(dx_deg) * 111320 * np.cos(np.radians(lat_mid))
    dy_m = dy_deg * 111320
    print(f"  像元大小: {dx_m:.1f} m × {dy_m:.1f} m")
    
    dem = dem_array.astype(np.float64).copy()
    dem[dem <= NODATA_VALUE] = np.nan
    
    # x方向梯度
    dz_dx = np.zeros_like(dem)
    dz_dx[:, 1:-1] = (dem[:, 2:] - dem[:, :-2]) / (2 * dx_m)
    dz_dx[:, 0] = (dem[:, 1] - dem[:, 0]) / dx_m
    dz_dx[:, -1] = (dem[:, -1] - dem[:, -2]) / dx_m
    
    # y方向梯度
    dz_dy = np.zeros_like(dem)
    dz_dy[1:-1, :] = (dem[:-2, :] - dem[2:, :]) / (2 * dy_m)
    dz_dy[0, :] = (dem[0, :] - dem[1, :]) / dy_m
    dz_dy[-1, :] = (dem[-2, :] - dem[-1, :]) / dy_m
    
    # 坡度
    slope_deg = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
    
    # 坡向（北为0°，顺时针）
    aspect_deg = np.degrees(np.arctan2(dz_dx, dz_dy))
    aspect_deg = (aspect_deg + 360) % 360
    
    # 平地坡向设为-1
    flat_mask = slope_deg < 0.5
    aspect_deg[flat_mask] = -1
    
    # NoData
    nodata_mask = np.isnan(dem)
    slope_deg[nodata_mask] = NODATA_VALUE
    aspect_deg[nodata_mask] = NODATA_VALUE
    
    return slope_deg.astype(np.float32), aspect_deg.astype(np.float32)

# ================== 隶属函数 ==================

def parabola_type(data, a, b, c, d):
    result = np.full_like(data, 0.1, dtype=np.float32)
    result[(data > a) & (data < b)] = 0.9 * ((data[(data > a) & (data < b)] - a) / (b - a)) + 0.1
    result[(data >= b) & (data <= c)] = 1.0
    result[(data > c) & (data < d)] = 0.9 * ((d - data[(data > c) & (data < d)]) / (d - c)) + 0.1
    result[data <= NODATA_VALUE] = np.nan
    result[np.isnan(data)] = np.nan
    return result

def inverse_s_type(data, a, d):
    result = np.full_like(data, 0.1, dtype=np.float32)
    result[data <= a] = 1.0
    mask = (data > a) & (data < d)
    result[mask] = 0.9 * ((d - data[mask]) / (d - a)) + 0.1
    result[data <= NODATA_VALUE] = np.nan
    result[np.isnan(data)] = np.nan
    return result

def aspect_membership(aspect_deg):
    result = np.full_like(aspect_deg, 0.5, dtype=np.float32)
    result[aspect_deg < 0] = 1.0                                    # 平地
    result[(aspect_deg >= 337.5) | (aspect_deg < 22.5)] = 0.3       # 北坡
    result[(aspect_deg >= 22.5) & (aspect_deg < 67.5)] = 0.4        # 东北
    result[(aspect_deg >= 67.5) & (aspect_deg < 112.5)] = 0.5       # 东坡
    result[(aspect_deg >= 112.5) & (aspect_deg < 157.5)] = 0.8      # 东南
    result[(aspect_deg >= 157.5) & (aspect_deg < 202.5)] = 1.0      # 南坡
    result[(aspect_deg >= 202.5) & (aspect_deg < 247.5)] = 0.7      # 西南
    result[(aspect_deg >= 247.5) & (aspect_deg < 292.5)] = 0.5      # 西坡
    result[(aspect_deg >= 292.5) & (aspect_deg < 337.5)] = 0.2      # 西北
    result[aspect_deg <= NODATA_VALUE] = np.nan
    result[np.isnan(aspect_deg)] = np.nan
    return result

# ================== 裁剪函数 ==================

def clip_raster(input_path, output_path, gdf):
    with rasterio.open(input_path) as src:
        vec = gdf.to_crs(src.crs)
        out_img, out_trans = mask(src, vec.geometry.values, crop=True, all_touched=True)
        out_meta = src.meta.copy()
        out_meta.update(height=out_img.shape[1], width=out_img.shape[2], 
                        transform=out_trans, dtype=rasterio.float32, compress="lzw")
        with rasterio.open(output_path, 'w', **out_meta) as dst:
            dst.write(out_img)
    return out_img[0], out_meta

# ================== 主程序 ==================

def main():
    print("=" * 55)
    print("  油茶地形适宜性 - 隶属度计算")
    print("=" * 55)
    
    # 步骤1：计算坡度坡向
    print("\n【1/4】读取DEM，计算坡度和坡向")
    with rasterio.open(dem_path) as src:
        dem_arr = src.read(1)
        profile = src.profile
        transform = src.transform
    print(f"  DEM尺寸: {dem_arr.shape}")
    
    slope_arr, aspect_arr = calculate_slope_aspect(dem_arr, transform)
    
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    p = profile.copy()
    p.update(dtype=rasterio.float32, count=1, compress='lzw')
    with rasterio.open(os.path.join(temp_dir, "slope.tif"), 'w', **p) as dst:
        dst.write(slope_arr, 1)
    with rasterio.open(os.path.join(temp_dir, "aspect.tif"), 'w', **p) as dst:
        dst.write(aspect_arr, 1)
    print("  坡度坡向计算完成")
    
    # 步骤2：裁剪
    print("\n【2/4】矢量裁剪")
    gdf = gpd.read_file(vector_path)
    
    dem_clip, _ = clip_raster(dem_path, os.path.join(output_dir, "clipped_dem.tif"), gdf)
    slope_clip, clip_profile = clip_raster(os.path.join(temp_dir, "slope.tif"), 
                                            os.path.join(output_dir, "clipped_slope.tif"), gdf)
    aspect_clip, _ = clip_raster(os.path.join(temp_dir, "aspect.tif"), 
                                  os.path.join(output_dir, "clipped_aspect.tif"), gdf)
    print("  裁剪完成")
    
    # 步骤3：隶属度
    print("\n【3/4】计算隶属度")
    mem_elev = parabola_type(dem_clip, 0, 100, 500, 800)
    mem_slope = inverse_s_type(slope_clip, 15, 25)
    mem_aspect = aspect_membership(aspect_clip)
    
    out_p = clip_profile.copy()
    out_p.update(count=1)
    
    for name, arr in [("elevation", mem_elev), ("slope", mem_slope), ("aspect", mem_aspect)]:
        with rasterio.open(os.path.join(output_dir, f"membership_{name}.tif"), 'w', **out_p) as dst:
            dst.write(arr, 1)
    print("  隶属度计算完成")
    
    # 步骤4：地形综合适宜性
    print("\n【4/4】地形综合适宜性")
    m1 = np.nan_to_num(mem_elev, nan=0.1).clip(0.1, 1.0)
    m2 = np.nan_to_num(mem_slope, nan=0.1).clip(0.1, 1.0)
    m3 = np.nan_to_num(mem_aspect, nan=0.1).clip(0.1, 1.0)
    
    terrain_suit = ((m1 * m2 * m3) ** (1/3)).astype(np.float32)
    
    with rasterio.open(os.path.join(output_dir, "terrain_combined_suitability.tif"), 'w', **out_p) as dst:
        dst.write(terrain_suit, 1)
    
    valid = terrain_suit[terrain_suit > 0.1]
    print(f"  范围: {np.min(valid):.4f} ~ {np.max(valid):.4f}")
    print(f"  均值: {np.mean(valid):.4f}")
    
    # 清理临时文件
    shutil.rmtree(temp_dir)
    
    print("\n" + "=" * 55)
    print(f"  ✅ 完成！输出目录: {output_dir}")
    print("=" * 55)

if __name__ == "__main__":
    main()
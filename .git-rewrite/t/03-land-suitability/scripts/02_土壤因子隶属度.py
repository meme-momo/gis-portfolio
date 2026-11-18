import numpy as np
import rasterio
import os

# 你的三个输出文件路径
organic_path = r"gt\processed_soil_data\clipped_organic_1km.tif"
ph_path = r"gt\processed_soil_data\clipped_ph_1km.tif"
depth_path = r"gt\processed_soil_data\clipped_depth_1km.tif"

# 输出路径（存放隶属度结果）
output_dir = r"gt\processed_soil_data"
os.makedirs(output_dir, exist_ok=True)

# ================== 隶属函数定义 ==================
def calculate_s_type(data, a, d):
    """
    S型隶属度（适合有机质、厚度）
    规则：小于a => 0.1；大于d => 1.0；中间线性插值
    """
    result = np.zeros_like(data, dtype=np.float32)
    result[data <= a] = 0.1
    result[data >= d] = 1.0
    mask = (data > a) & (data < d)
    result[mask] = 0.9 * ((data[mask] - a) / (d - a)) + 0.1
    result[data <= -9999] = np.nan  # 处理 NoData
    return result

def calculate_parabola_type(data, a, b, c, d):
    """
    抛物线型隶属度（适合PH）
    规则：a~b~c~d：四段
    """
    result = np.zeros_like(data, dtype=np.float32)
    result[data <= a] = 0.1
    result[data >= d] = 0.1
    # 上升段 a < x < b
    mask1 = (data > a) & (data < b)
    result[mask1] = 0.9 * ((data[mask1] - a) / (b - a)) + 0.1
    # 最佳段 b <= x <= c
    mask2 = (data >= b) & (data <= c)
    result[mask2] = 1.0
    # 下降段 c < x < d
    mask3 = (data > c) & (data < d)
    result[mask3] = 1 - 0.9 * ((data[mask3] - c) / (d - c))
    result[data <= -9999] = np.nan
    return result

# ================== 批量处理 ==================
# 1. 有机质（S型，下限1%，上限2%）
with rasterio.open(organic_path) as src:
    arr = src.read(1)
    profile = src.profile
    membership = calculate_s_type(arr, a=1.0, d=2.0)
    out_path = os.path.join(output_dir, "membership_organic.tif")
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(membership, 1)
    print(f"1. 有机质隶属度计算完成 -> {out_path}")

# 2. 土壤PH（抛物线型：a=4.5, b=5, c=6, d=6.5）
with rasterio.open(ph_path) as src:
    arr = src.read(1)
    profile = src.profile
    membership = calculate_parabola_type(arr, a=4.5, b=5.0, c=6.0, d=6.5)
    out_path = os.path.join(output_dir, "membership_ph.tif")
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(membership, 1)
    print(f"2. PH隶属度计算完成 -> {out_path}")

# 3. 土壤厚度（S型：下限10cm，上限100cm）
with rasterio.open(depth_path) as src:
    arr = src.read(1)
    profile = src.profile
    membership = calculate_s_type(arr, a=10.0, d=100.0)
    out_path = os.path.join(output_dir, "membership_depth.tif")
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(membership, 1)
    print(f"3. 厚度隶属度计算完成 -> {out_path}")

# ================== 最终：合成土壤适宜性 ==================
# 土壤综合适宜性 = (有机质隶属度 * PH隶属度 * 厚度隶属度) 的开三次方
print("正在计算土壤综合适宜性...")
with rasterio.open(os.path.join(output_dir, "membership_organic.tif")) as src_org:
    arr_org = src_org.read(1)
    profile = src_org.profile
with rasterio.open(os.path.join(output_dir, "membership_ph.tif")) as src_ph:
    arr_ph = src_ph.read(1)
with rasterio.open(os.path.join(output_dir, "membership_depth.tif")) as src_depth:
    arr_depth = src_depth.read(1)

# 处理NoData：将NaN设为0，避免开方出错
arr_org = np.nan_to_num(arr_org, nan=0.0)
arr_ph = np.nan_to_num(arr_ph, nan=0.0)
arr_depth = np.nan_to_num(arr_depth, nan=0.0)

# 连乘开三次方
soil_combined = (arr_org * arr_ph * arr_depth) ** (1/3)
soil_combined = np.clip(soil_combined, 0.1, 1.0)  # 确保在0.1~1范围

out_path = os.path.join(output_dir, "soil_combined_suitability.tif")
with rasterio.open(out_path, 'w', **profile) as dst:
    dst.write(soil_combined, 1)
print(f"✅ 土壤综合适宜性计算完成！结果 -> {out_path}")
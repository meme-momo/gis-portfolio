import arcpy
from arcpy.sa import *
import os
import re
import traceback

arcpy.CheckOutExtension("Spatial")

# === 你需要修改这几个路径 ===
input_folder = r"F:\dasai\南太行数据\生态涵养区\FVC"           # 原始栅格文件夹
output_folder = r"F:\dasai\南太行数据\生态涵养区\FVC\新建文件夹"     # 输出文件夹
mask_raster = r"F:\dasai\ESV(1.21)\栅格分区\生态涵养区.tif"  # 参考栅格，用于保持范围和掩膜一致

# 权重数值（所有像元除以这个值）
weight_value = 0.073071 

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 设置 ArcPy 环境
arcpy.env.mask = mask_raster
arcpy.env.snapRaster = mask_raster
arcpy.env.cellSize = mask_raster
arcpy.env.extent = mask_raster
arcpy.env.outputCoordinateSystem = arcpy.Describe(mask_raster).spatialReference
arcpy.env.overwriteOutput = True

# 正则表达式提取年份
year_pattern = re.compile(r'(\d{4})')

# 收集所有 .tif 文件
tif_files = [f for f in os.listdir(input_folder) if f.endswith(".tif")]
total_files = len(tif_files)
processed_count = 0

for index, file in enumerate(tif_files, 1):
    year_match = year_pattern.search(file)
    if not year_match:
        print(f"⚠️ 跳过无法识别年份的文件：{file}")
        continue

    year = int(year_match.group(1))
    input_path = os.path.join(input_folder, file)

    # 删除 2022 年及以后的数据
    if year >= 2022:
        print(f"🚮 删除年份为 {year} 的文件：{file}")
        os.remove(input_path)
        continue

    print(f"🔄 处理第 {index} / {total_files} 个文件：{file}")

    try:
        # 读取栅格并除以权重
        raster = Raster(input_path)
        normalized = raster / weight_value

        # 限定在 0 ~ 1 之间
        normalized = Con(normalized < 0, 0, normalized)
        normalized = Con(normalized > 1, 1, normalized)

        # 输出路径
        out_name = f"norm_{file}"
        out_path = os.path.join(output_folder, out_name)
        normalized.save(out_path)

        print(f"✅ 成功保存：{out_path}")
        processed_count += 1

    except Exception as e:
        print(f"❌ 处理失败：{file}")
        traceback.print_exc()

print(f"\n🎉 完成处理，共成功处理 {processed_count} 个文件。")

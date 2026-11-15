import arcpy
from arcpy.sa import *
import os
import re

arcpy.CheckOutExtension("Spatial")

# === 你需要修改这几个路径 ===
input_folder = r"F:\dasai\南太行数据\水生态保护区\土壤保持"           # 原始栅格文件夹
output_folder = r"F:\dasai\南太行数据\水生态保护区\土壤保持\标准化"     # 输出文件夹
mask_raster = r"F:\dasai\ESV(1.21)\栅格分区\水生态保护区1.tif"  # 参考栅格，用于保持范围和掩膜一致

# 统一的权重数值（非栅格）
weight_value =0.058077

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 设置环境参数
arcpy.env.mask = mask_raster
arcpy.env.snapRaster = mask_raster
arcpy.env.cellSize = mask_raster
arcpy.env.extent = mask_raster
arcpy.env.outputCoordinateSystem = arcpy.Describe(mask_raster).spatialReference
arcpy.env.overwriteOutput = True

# 匹配文件名中的年份
year_pattern = re.compile(r'(\d{4})')

# 遍历文件夹中所有.tif文件
for file in os.listdir(input_folder):
    if file.endswith(".tif"):
        year_match = year_pattern.search(file)
        if year_match:
            year = int(year_match.group(1))
            input_path = os.path.join(input_folder, file)

            # 删除 2022 年及之后的文件
            if year >= 2022:
                print(f"🚮 删除年份为 {year} 的文件：{file}")
                os.remove(input_path)
                continue

            print(f"✅ 正在处理 {file} ...")
            raster = Raster(input_path)

            # 除以权重数值
            normalized = raster / weight_value

            # 限定结果在 0~1 之间
            normalized = Con(normalized < 0, 0, normalized)
            normalized = Con(normalized > 1, 1, normalized)

            # 输出文件
            out_name = f"{file}"
            out_path = os.path.join(output_folder, out_name)
            normalized.save(out_path)

            print(f"💾 已保存归一化栅格：{out_path}")

print("🎉 所有栅格处理完成。")

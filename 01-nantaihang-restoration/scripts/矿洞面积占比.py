import arcpy
import os
import re
import pandas as pd

arcpy.env.overwriteOutput = True

# === 参数设置 ===
mine_folder = r"dasai\矿洞矢量"  # 多年份矿洞矢量文件夹
standard_raster = r"dasai\矿山治理区\standard.tif"  # 标准栅格
output_excel = r"dasai\矿山治理区\矿洞占比.xlsx"

# 获取矿山治理区总面积（以栅格像元面积累加）
desc = arcpy.Describe(standard_raster)
cell_area = desc.meanCellHeight * desc.meanCellWidth  # 栅格像元面积
raster = arcpy.Raster(standard_raster)
raster_mask = arcpy.RasterToPolygon_conversion(raster, "in_memory\\mask", "NO_SIMPLIFY")
# 栅格转换矢量后求总面积
total_area = 0
with arcpy.da.SearchCursor(raster_mask, ["SHAPE@AREA"]) as cursor:
    for row in cursor:
        total_area += row[0]

# === 统计矿洞面积 ===
data_list = []

for shp_file in os.listdir(mine_folder):
    if not shp_file.lower().endswith(".shp"):
        continue
    shp_path = os.path.join(mine_folder, shp_file)
    
    # 提取年份
    match = re.search(r"(20\d{2})", shp_file)
    if match:
        year = match.group(1)
    else:
        year = shp_file  # 没有年份就用文件名

    # 求矿洞总面积
    total_mine_area = 0
    with arcpy.da.SearchCursor(shp_path, ["SHAPE@AREA"]) as cursor:
        for row in cursor:
            total_mine_area += row[0]

    # 计算占比
    ratio = total_mine_area / total_area if total_area > 0 else 0

    data_list.append({
        "年份": year,
        "矿洞总面积": total_mine_area,
        "矿山治理区总面积": total_area,
        "占比": ratio
    })

# === 输出到 Excel ===
df = pd.DataFrame(data_list)
df = df.sort_values("年份")
df.to_excel(output_excel, index=False)

print(f"✅ 完成！结果已保存到 {output_excel}")
# -*- coding: utf-8 -*-
import arcpy
import os
import re
from tqdm import tqdm
from arcpy.sa import ZonalStatisticsAsTable

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# === 参数设置 ===
root_folder = r"F:\dasai\南太行数据"   # 功能区总文件夹
grids = {
    "生态涵养区": r"F:\dasai\南太行渔网\生态涵养区.shp",
    "水生态保护区": r"F:\dasai\南太行渔网\水生态保护区.shp",
    "矿山治理区": r"F:\dasai\南太行渔网\矿山治理区.shp"
}
target_years = ["2013", "2019", "2024"]

# === 栅格赋值函数 ===
def process_raster_to_grid(raster_path, year, out_shp, fc_name, ind_name):
    """栅格平均值写入渔网"""
    try:
        # 字段命名 m2013
        field_name = f"m{year}"
        existing_fields = [f.name for f in arcpy.ListFields(out_shp)]
        if field_name not in existing_fields:
            arcpy.AddField_management(out_shp, field_name, "DOUBLE")

        # 临时表
        tmp_table = "in_memory\\zonal"
        if arcpy.Exists(tmp_table):
            arcpy.Delete_management(tmp_table)

        # zonal统计
        ZonalStatisticsAsTable(
            in_zone_data=out_shp,
            zone_field="FID",
            in_value_raster=raster_path,
            out_table=tmp_table,
            statistics_type="MEAN",
            ignore_nodata="DATA",
        )

        # 写入字段，如果没有数据赋 0.00001
        stats = {row[0]: row[1] for row in arcpy.da.SearchCursor(tmp_table, ["FID", "MEAN"])}
        with arcpy.da.UpdateCursor(out_shp, ["FID", field_name]) as cursor:
            for fid, val in cursor:
                value = stats.get(fid, 0.00001)
                if value is None:
                    value = 0.00001
                cursor.updateRow([fid, value])

        arcpy.Delete_management(tmp_table)

    except Exception as e:
        print(f"❌ 失败: 功能区={fc_name}, 指标={ind_name}, 年份={year}, 错误={e}")


# === 主循环 ===
for fc_name in tqdm(os.listdir(root_folder), desc="功能区", unit="区"):
    fc_path = os.path.join(root_folder, fc_name)
    if not os.path.isdir(fc_path) or fc_name not in grids:
        continue

    grid_shp = grids[fc_name]

    for ind_name in tqdm(os.listdir(fc_path), desc=f"{fc_name} 指标", unit="指标", leave=False):
        ind_path = os.path.join(fc_path, ind_name)
        if not os.path.isdir(ind_path):
            continue

        weight_path = os.path.join(ind_path, "权重")
        if not os.path.exists(weight_path):
            continue

        # 输出到 "可视化" 文件夹
        vis_folder = os.path.join(ind_path, "可视化")
        os.makedirs(vis_folder, exist_ok=True)

        # 安全化指标名：替换非法字符，并截取前10个字符# -*- coding: utf-8 -*-
import arcpy
import os
import re
import pandas as pd

arcpy.env.overwriteOutput = True

# === 参数设置 ===
mine_folder = r"F:\dasai\矿洞矢量"  # 多年份矿洞矢量文件夹
standard_raster = r"F:\dasai\矿山治理区\standard.tif"  # 标准栅格
output_excel = r"F:\dasai\矿山治理区\矿洞占比.xlsx"

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

        safe_ind_name = re.sub(r'[\\/:*?"<>|.]', '_', ind_name)[:10]
        out_shp = os.path.join(vis_folder, f"{safe_ind_name}_grid.shp")

        # 只复制一次渔网
        if not arcpy.Exists(out_shp):
            try:
                arcpy.CopyFeatures_management(grid_shp, out_shp)
            except Exception as e:
                print(f"❌ 复制渔网失败: 功能区={fc_name}, 指标={ind_name}, 错误={e}")
                continue

        # 遍历权重文件夹的栅格
        raster_files = [f for f in os.listdir(weight_path) if f.lower().endswith(".tif")]
        if not raster_files:
            continue  # 没有栅格 → 跳过

        for tif_name in tqdm(raster_files, desc=f"{ind_name} 年份", unit="年", leave=False):
            year_match = re.search(r"(20\d{2})", tif_name)
            if not year_match:
                continue
            year = year_match.group(1)
            if year not in target_years:
                continue

            tif_path = os.path.join(weight_path, tif_name)
            process_raster_to_grid(tif_path, year, out_shp, fc_name, ind_name)

print("\n🎉 全部功能区指标处理完成！")

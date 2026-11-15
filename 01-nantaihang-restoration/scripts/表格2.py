# -*- coding: utf-8 -*-
import arcpy
import os
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

arcpy.env.overwriteOutput = True

# 根目录
root_folder = r"F:\dasai\南太行数据"

# 特殊功能区矢量指标路径（渔网矢量）
special_vector_indicators = {
    "地面沉降率": r"F:\dasai\南太行数据\矿山治理区\地面沉降率\渔网结果.shp",
    "适生林地占比": r"F:\dasai\南太行数据\矿山治理区\适生林地占比\渔网结果.shp"
}

# 存储结果
results = {}

# --------- 函数：处理单个指标 ---------
def process_indicator(area_name, indicator, indicator_path):
    indicator_result = {}

    raw_path = os.path.join(indicator_path, "原始")
    # 特殊矢量指标
    if indicator in special_vector_indicators and os.path.exists(special_vector_indicators[indicator]):
        vec_path = special_vector_indicators[indicator]
        fields = [f.name for f in arcpy.ListFields(vec_path) if re.match(r"a\d{4}", f.name)]
        for year_field in fields:
            year = year_field[1:]  # 去掉前缀 a
            total, count = 0, 0
            with arcpy.da.SearchCursor(vec_path, [year_field]) as cursor:
                for val in cursor:
                    if val[0] is not None:
                        total += val[0]
                        count += 1
            indicator_result[year] = total / count if count > 0 else None

    # 功能区栅格指标
    elif os.path.exists(raw_path) and os.path.isdir(raw_path):
        file_list = [f for f in os.listdir(raw_path) if f.lower().endswith(".tif")]
        for file_name in file_list:
            file_path = os.path.join(raw_path, file_name)
            match = re.search(r"(\d{4})", file_name)
            if not match:
                continue
            year = match.group(1)
            try:
                arcpy.CalculateStatistics_management(file_path)
                mean_val = float(arcpy.GetRasterProperties_management(file_path, "MEAN").getOutput(0))
                indicator_result[year] = mean_val
            except:
                continue

    # 总体文件夹处理
    else:
        file_list = [f for f in os.listdir(indicator_path) if f.lower().endswith(".tif")]
        for file_name in file_list:
            file_path = os.path.join(indicator_path, file_name)
            match = re.search(r"(\d{4})", file_name)
            if not match:
                continue
            year = match.group(1)
            try:
                arcpy.CalculateStatistics_management(file_path)
                mean_val = float(arcpy.GetRasterProperties_management(file_path, "MEAN").getOutput(0))
                indicator_result[year] = mean_val
            except:
                continue

    return indicator, indicator_result


# --------- 遍历功能区/总体文件夹 ---------
area_list = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]
for area_name in area_list:
    area_path = os.path.join(root_folder, area_name)
    results[area_name] = {}

    indicator_list = [f for f in os.listdir(area_path) if os.path.isdir(os.path.join(area_path, f))]

    # 使用线程池并行处理指标
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_indicator = {
            executor.submit(process_indicator, area_name, indicator, os.path.join(area_path, indicator)): indicator
            for indicator in indicator_list
        }
        for future in as_completed(future_to_indicator):
            indicator, indicator_result = future.result()
            results[area_name][indicator] = indicator_result

# --------- 输出 Excel ---------
excel_output = os.path.join(root_folder, "统计结果.xlsx")
with pd.ExcelWriter(excel_output) as writer:
    for area_name, indicators in results.items():
        df = pd.DataFrame(indicators).T
        df = df[sorted(df.columns)] if df.columns.any() else df
        df.to_excel(writer, sheet_name=area_name)

print(f"✅ 已导出统计结果到：{excel_output}")

# -*- coding: utf-8 -*-
import arcpy
import os
import re
import pandas as pd
from tqdm import tqdm  # 进度条

arcpy.env.overwriteOutput = True

# 根目录
root_folder = r"dasai\南太行数据"

# 特殊功能区矢量指标路径（渔网矢量）
special_vector_indicators = {
    "地面沉降率": r"dasai\南太行数据\矿山治理区\地面沉降率\渔网结果.shp",
    "适生林地占比": r"dasai\南太行数据\矿山治理区\适生林地占比\渔网结果.shp"
}

# 存储结果
results = {}

# --------- 函数：处理单个指标 ---------
def process_indicator(indicator, indicator_path):
    indicator_result = {}

    # 1) 特殊矢量指标
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

    # 2) 功能区标准化栅格
    else:
        std_path = os.path.join(indicator_path, "标准化")
        if os.path.exists(std_path):
            file_list = [f for f in os.listdir(std_path) if f.lower().endswith(".tif")]
            for file_name in file_list:
                match = re.search(r"(\d{4})", file_name)
                if not match:
                    continue
                year = match.group(1)
                file_path = os.path.join(std_path, file_name)
                try:
                    arcpy.CalculateStatistics_management(file_path)
                    mean_val = float(arcpy.GetRasterProperties_management(file_path, "MEAN").getOutput(0))
                    indicator_result[year] = mean_val
                except:
                    indicator_result[year] = None  # 出错时写 None

    return indicator_result


# --------- 遍历功能区文件夹 ---------
area_list = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]

for area_name in tqdm(area_list, desc="处理功能区"):  # 外层进度条
    area_path = os.path.join(root_folder, area_name)
    results[area_name] = {}

    indicator_list = [f for f in os.listdir(area_path) if os.path.isdir(os.path.join(area_path, f))]

    for indicator in tqdm(indicator_list, desc=f"{area_name} - 指标", leave=False):  # 内层进度条
        indicator_path = os.path.join(area_path, indicator)
        results[area_name][indicator] = process_indicator(indicator, indicator_path)


# --------- 输出 Excel ---------
excel_output = os.path.join(root_folder, "标准化统计结果.xlsx")
with pd.ExcelWriter(excel_output) as writer:
    for area_name, indicators in results.items():
        df = pd.DataFrame(indicators).T
        # 按年份排序
        if not df.empty:
            df = df[sorted(df.columns)]
        df.to_excel(writer, sheet_name=area_name)

print(f"✅ 已导出标准化统计结果到：{excel_output}")

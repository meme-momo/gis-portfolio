# -*- coding: utf-8 -*-
import arcpy
import os
import re
import pandas as pd
from tqdm import tqdm

# 特殊矢量指标路径
special_vector_indicators = {
    "地面沉降率": r"dasai\南太行数据\矿山治理区\地面沉降率\渔网结果.shp",
    "适生林地占比": r"dasai\南太行数据\矿山治理区\适生林地占比\渔网结果.shp"
}

# 存储结果
results = {}

for indicator, shp_path in tqdm(special_vector_indicators.items(), desc="处理特殊矢量指标"):
    if not os.path.exists(shp_path):
        print(f"⚠ 矢量文件不存在: {shp_path}")
        continue

    results[indicator] = {}
    # 获取所有年份字段，假设字段名为 a2012, a2013 ...
    year_fields = [f.name for f in arcpy.ListFields(shp_path) if re.match(r"a\d{4}", f.name)]

    for field in year_fields:
        year = field[1:]  # 去掉前缀 a
        total, count = 0, 0
        with arcpy.da.SearchCursor(shp_path, [field]) as cursor:
            for val in cursor:
                if val[0] is not None:
                    total += val[0]
                    count += 1
        avg_value = total / count if count > 0 else None
        results[indicator][year] = avg_value

# 输出 Excel
excel_output = r"dasai\南太行数据\特殊矢量指标平均值.xlsx"
with pd.ExcelWriter(excel_output) as writer:
    for indicator, year_dict in results.items():
        df = pd.DataFrame([year_dict])
        df = df[sorted(df.columns)]
        df.to_excel(writer, sheet_name=indicator, index=False)

print(f"✅ 已导出特殊矢量指标平均值到：{excel_output}")

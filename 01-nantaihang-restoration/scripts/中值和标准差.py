# -*- coding: utf-8 -*-
import os
import re
import numpy as np
import rasterio
import pandas as pd

def extract_year(filename):
    """从文件名提取年份 (1900-2099)，匹配不到就返回None"""
    match = re.search(r"(19|20)\d{2}", filename)
    return match.group(0) if match else None

def calc_stats_from_raster(raster_path):
    """计算单个栅格的中值和标准差"""
    with rasterio.open(raster_path) as src:
        arr = src.read(1).astype(float)
        # 去除 nodata
        if src.nodata is not None:
            arr = arr[arr != src.nodata]
        arr = arr[~np.isnan(arr)]  # 去掉NaN
        if arr.size == 0:
            return np.nan, np.nan
        return np.median(arr), np.std(arr)

def process_folder(folder_path):
    """处理一个总权重文件夹，返回 {year: (median, std)}"""
    results = {}
    for file in os.listdir(folder_path):
        if file.lower().endswith(".tif"):
            year = extract_year(file)
            if not year:
                continue  # 跳过没有年份的文件
            raster_path = os.path.join(folder_path, file)
            median, std = calc_stats_from_raster(raster_path)
            results[year] = (median, std)
    return results

def results_to_dataframe(results):
    """转换为 DataFrame，行头=中值/标准差，列头=年份（升序排序）"""
    # 保证年份按数值排序
    years = sorted(results.keys(), key=lambda y: int(y))
    data = {
        year: {"中值": results[year][0], "标准差": results[year][1]}
        for year in years
    }
    df = pd.DataFrame(data).T  # 年份为行
    df = df.T  # 转置：行头=中值/标准差
    return df

def main():
    root_folder = r"F:\dasai\南太行数据"  # 修改为你的路径
    output_excel = os.path.join(root_folder, "统计结果.xlsx")

    folders = {
        "总权重": os.path.join(root_folder, "总权重"),
        "矿山治理区": os.path.join(root_folder, "矿山治理区", "总权重"),
        "生态涵养区": os.path.join(root_folder, "生态涵养区", "总权重"),
        "水生态保护区": os.path.join(root_folder, "水生态保护区", "总权重"),
    }

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for name, path in folders.items():
            results = process_folder(path)
            if not results:
                print(f"⚠️ {name} 没有识别到年份数据，跳过")
                continue
            df = results_to_dataframe(results)
            df.to_excel(writer, sheet_name=name)

    print("✅ 统计完成，结果已保存到：", output_excel)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
import re
import numpy as np
from arcpy.sa import Raster, Con
from arcpy.ia import ZonalStatisticsAsTable
import pandas as pd

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# ========= 参数 =========
root_folder = r"F:\dasai\南太行数据"

# 新权重表（不包含特殊指标）
indicators = {
    "植被覆盖率": {"weight": 0.138182},
    "碳储量": {"weight": 0.258156},
    "食物生产": {"weight": 0.09105},
    "原材料生产": {"weight": 0.073434},
    "pm2.5": {"weight": 0.118373},
    "气候调节": {"weight": 0.064304},
    "生态联通度": {"weight": 0.127521},
    "生物多样性": {"weight": 0.063574},
    "美学景观": {"weight": 0.065408},
    "废物处理": {"weight": 0.304793},
    "生境指数": {"weight": 0.268118},
    "水源涵养": {"weight": 0.465274},
    "土壤保持": {"weight": 0.091811},
    "水文调节": {"weight": 0.261479},
    "氮负荷": {"weight": 0.091046},
    "磷负荷": {"weight": 0.09039}
}
special_indicators = ["适生林地占比", "地面沉降率"]

# 需要计算增长率的指标
growth_indicators = ["食物生产", "原材料生产", "气候调节", "生物多样性", 
                    "美学景观", "废物处理", "土壤保持", "水文调节"]

# ========= 函数 =========
def clear_folder(path):
    """清空文件夹"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def extract_year_from_filename(filename):
    """从文件名中提取年份"""
    # 尝试匹配4位数字的年份
    match = re.search(r'(\d{4})', filename)
    if match:
        return int(match.group(1))
    return None

def min_max_normalize(raster):
    """Min-Max标准化"""
    # 获取栅格统计信息
    min_val = raster.minimum
    max_val = raster.maximum
    
    # 如果最大值等于最小值，则返回全零栅格
    if max_val == min_val:
        return Con(raster >= 0, 0)
    
    # 应用Min-Max标准化公式: (x - min) / (max - min)
    normalized = (raster - min_val) / (max_val - min_val)
    return normalized

def process_general(ind_path, weight):
    """处理一般指标（绝对值×权重）"""
    std_folder = os.path.join(ind_path, "标准化")
    if not os.path.exists(std_folder):
        print(f"⚠️ {ind_path} 缺少标准化文件夹")
        return

    out_folder = os.path.join(ind_path, "权重")
    clear_folder(out_folder)

    for file in os.listdir(std_folder):
        if not file.lower().endswith(".tif"):
            continue
        in_path = os.path.join(std_folder, file)
        try:
            ras = Raster(in_path)
            # 乘权重
            out_ras = ras * weight
            # 输出文件名改成年份.tif
            year = extract_year_from_filename(file)
            if year:
                out_path = os.path.join(out_folder, f"{year}.tif")
                out_ras.save(out_path)
                print(f"✅ {year}年 输出完成")
            else:
                print(f"⚠️ 无法从文件名 {file} 中提取年份")
        except Exception as e:
            print(f"❌ {file} 处理出错: {e}")

def calculate_and_normalize_growth_rate(ind_path):
    """计算增长率并进行标准化处理"""
    raw_folder = os.path.join(ind_path, "原始")
    if not os.path.exists(raw_folder):
        print(f"⚠️ {ind_path} 缺少原始文件夹")
        return
    
    # 清空并创建标准化文件夹
    std_folder = os.path.join(ind_path, "标准化")
    clear_folder(std_folder)
    
    # 获取所有年份文件并排序
    year_files = []
    for file in os.listdir(raw_folder):
        if file.lower().endswith(".tif"):
            year = extract_year_from_filename(file)
            if year:
                year_files.append((year, file))
            else:
                print(f"⚠️ 无法从文件名 {file} 中提取年份")
    
    if not year_files:
        print(f"⚠️ {ind_path} 没有找到有效的年份文件")
        return
    
    # 按年份排序
    year_files.sort(key=lambda x: x[0])
    
    # 存储所有增长率栅格，用于后续的标准化
    growth_rasters = []
    growth_years = []
    
    # 处理每个年份（从第二年开始）
    for i in range(1, len(year_files)):
        current_year, current_file = year_files[i]
        prev_year, prev_file = year_files[i-1]
        
        # 确保年份连续
        if current_year - prev_year != 1:
            print(f"⚠️ 年份不连续: {prev_year} -> {current_year}，跳过计算增长率")
            continue
            
        try:
            # 读取当前年和前一年的栅格
            current_ras = Raster(os.path.join(raw_folder, current_file))
            prev_ras = Raster(os.path.join(raw_folder, prev_file))
            
            # 计算增长率：当前年/前一年
            # 避免除零错误，将小于1e-6的值设为1e-6
            prev_ras = Con(prev_ras < 1e-6, 1e-6, prev_ras)
            growth_ras = current_ras / prev_ras
            
            # 存储增长率栅格和对应年份
            growth_rasters.append(growth_ras)
            growth_years.append(current_year)
            
            print(f"✅ {current_year}年增长率计算完成")
            
        except Exception as e:
            print(f"❌ 处理 {current_year}年增长率时出错: {e}")
    
    # 如果有增长率数据，进行标准化处理
    if growth_rasters:
        # 合并所有增长率栅格以计算全局最小最大值
        combined_ras = growth_rasters[0]
        for ras in growth_rasters[1:]:
            combined_ras = arcpy.sa.CompositeBand([combined_ras, ras])
        
        # 计算全局最小最大值
        min_val = combined_ras.minimum
        max_val = combined_ras.maximum
        
        # 对每个增长率栅格进行Min-Max标准化
        for i, (ras, year) in enumerate(zip(growth_rasters, growth_years)):
            # Min-Max标准化: (x - min) / (max - min)
            normalized_ras = (ras - min_val) / (max_val - min_val)
            
            # 保存标准化后的结果
            out_path = os.path.join(std_folder, f"{year}.tif")
            normalized_ras.save(out_path)
            print(f"✅ {year}年增长率标准化完成")

# ========= 主程序 =========
for zone in os.listdir(root_folder):
    zone_path = os.path.join(root_folder, zone)
    if not os.path.isdir(zone_path):
        continue
    if zone == "整体":
        print(f"⚠️ 跳过整体文件夹: {zone_path}")
        continue

    print(f"\n📂 功能区: {zone}")

    # 首先处理需要计算增长率的指标
    for ind_name in growth_indicators:
        if ind_name in special_indicators:
            continue  # 跳过特殊指标
        
        ind_path = os.path.join(zone_path, ind_name)
        if not os.path.exists(ind_path):
            print(f"⚠️ {zone} - {ind_name} 文件夹不存在，跳过")
            continue

        try:
            # 计算增长率并进行标准化处理
            calculate_and_normalize_growth_rate(ind_path)
        except Exception as e:
            print(f"❌ {zone} - {ind_name} 计算增长率时出错: {e}")

    # 然后处理所有指标（包括刚刚计算了增长率的指标）
    for ind_name, cfg in indicators.items():
        if ind_name in special_indicators:
            continue  # 跳过特殊指标
        
        ind_path = os.path.join(zone_path, ind_name)
        if not os.path.exists(ind_path):
            print(f"⚠️ {zone} - {ind_name} 文件夹不存在，跳过")
            continue

        try:
            # 处理一般指标（包括刚刚计算了增长率的指标）
            process_general(ind_path, cfg["weight"])
        except Exception as e:
            print(f"❌ {zone} - {ind_name} 处理出错: {e}")

print("\n🎉 所有指标处理完成！")

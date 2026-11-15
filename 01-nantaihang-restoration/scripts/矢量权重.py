# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
import re
from arcpy.sa import Raster
import numpy as np

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# 设置环境编码
os.environ["PYTHONIOENCODING"] = "utf-8"

# 输入参数
shp_paths = {
    "适生林地占比": r"dasai\南太行数据\矿山治理区\适生林地占比\渔网结果.shp",
    "地面沉降率": r"dasai\南太行数据\矿山治理区\地面沉降率\渔网结果.shp"
}

weights = {
    "适生林地占比":0.234329 ,
    "地面沉降率": 0.192761
}

standard_raster = r"dasai\ESV(1.21)\栅格分区\矿山治理区.tif"

output_folders = {
    "适生林地占比": r"dasai\南太行数据\矿山治理区\适生林地占比\权重",
    "地面沉降率": r"dasai\南太行数据\矿山治理区\地面沉降率\权重"
}

def clear_folder(path):
    """清空并创建文件夹"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def standardize_field_values(values):
    """标准化字段值 (Min-Max标准化)"""
    min_val = min(values)
    max_val = max(values)
    
    if max_val == min_val:  # 防止除零错误
        return [0.0] * len(values)
    
    return [(v - min_val) / (max_val - min_val) for v in values]

def process_vector(shp_path, weight, out_folder):
    """处理矢量数据并生成加权栅格"""
    if not os.path.exists(shp_path):
        print(f"⚠️ {shp_path} 不存在")
        return

    # 创建临时文件夹
    tmp_folder = os.path.join(os.path.dirname(out_folder), "temp_process")
    clear_folder(tmp_folder)
    
    # 创建临时副本
    base_name = os.path.basename(shp_path)
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name.split('.')[0])[:8] + '.shp'
    tmp_shp = os.path.join(tmp_folder, safe_name)
    
    try:
        arcpy.FeatureClassToFeatureClass_conversion(shp_path, tmp_folder, safe_name.replace('.shp', ''))
        print(f"✅ 创建临时副本: {safe_name}")
    except Exception as e:
        print(f"❌ 复制文件失败: {e}")
        shutil.rmtree(tmp_folder)
        return

    # 设置环境参数
    std_ras = Raster(standard_raster)
    arcpy.env.snapRaster = std_ras
    arcpy.env.extent = std_ras.extent
    arcpy.env.cellSize = std_ras.meanCellHeight

    # 获取所有以'a'开头的字段
    fields = []
    for f in arcpy.ListFields(tmp_shp):
        try:
            field_name = f.name
            if field_name.startswith('a') and field_name[1:].isdigit() and len(field_name) == 5:
                fields.append(field_name)
        except:
            continue

    if not fields:
        print(f"⚠️ {tmp_shp} 没有找到符合条件的年份字段")
        shutil.rmtree(tmp_folder)
        return

    print(f"找到字段: {', '.join(fields)}")
    
    # 处理每个年份字段
    for field in fields:
        year = field[1:]  # 提取年份部分
        output_field = f"q{year}"  # 输出字段名
        
        # 添加输出字段
        try:
            arcpy.AddField_management(tmp_shp, output_field, "DOUBLE")
        except:
            # 字段可能已存在
            pass
        
        # 读取原始值并标准化
        values = []
        with arcpy.da.SearchCursor(tmp_shp, [field]) as cursor:
            for row in cursor:
                values.append(row[0] if row[0] is not None else 0)
        
        # 标准化处理
        standardized_values = standardize_field_values(values)
        
        # 计算加权值并写入字段
        with arcpy.da.UpdateCursor(tmp_shp, [output_field]) as cursor:
            for i, row in enumerate(cursor):
                weighted_value = standardized_values[i] * weight
                cursor.updateRow([weighted_value])
        
        # 输出栅格
        output_raster = os.path.join(out_folder, f"q{year}.tif")
        try:
            arcpy.FeatureToRaster_conversion(tmp_shp, output_field, output_raster, std_ras.meanCellHeight)
            print(f"✅ q{year}.tif 输出完成")
        except Exception as e:
            print(f"❌ q{year} 转栅格失败: {e}")
    
    # 清理临时文件夹
    try:
        shutil.rmtree(tmp_folder)
        print("临时文件夹已清理")
    except Exception as e:
        print(f"清理临时文件夹失败: {e}")

# ========= 主程序 =========
# 先清空所有输出文件夹
for out_folder in output_folders.values():
    clear_folder(out_folder)

for name, shp_path in shp_paths.items():
    print(f"\n📂 处理 {name}")
    out_folder = output_folders[name]
    process_vector(shp_path, weights[name], out_folder)

print("\n🎉 所有指标处理完成！")

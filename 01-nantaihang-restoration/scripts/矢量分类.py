import arcpy
import os
import pandas as pd
import numpy as np
import jenkspy
import time
from arcpy.sa import *
from tqdm import tqdm  # 用于显示进度条

# 设置工作环境
arcpy.env.workspace = r"F:\dasai\南太行数据\总权重\矢量"
arcpy.env.overwriteOutput = True  # 允许覆盖现有输出

# 定义输入和输出路径
input_folder = r"F:\dasai\南太行数据\总权重\矢量"
output_folder = r"F:\dasai\南太行数据\总权重\矢量\功能区"
mask_rasters = [
    r"F:\dasai\ESV(1.21)\栅格分区\矿山治理区.tif",
    r"F:\dasai\ESV(1.21)\栅格分区\生态涵养区.tif",
    r"F:\dasai\ESV(1.21)\栅格分区\水生态保护区1.tif"
]
zone_names = ["矿山治理区", "生态涵养区", "水生态保护区"]

# 创建输出文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
# 创建功能区子文件夹
for zone in zone_names:
    zone_folder = os.path.join(output_folder, zone)
    if not os.path.exists(zone_folder):
        os.makedirs(zone_folder)

# 获取所有矢量文件
feature_classes = []
for file in os.listdir(input_folder):
    if file.endswith(".shp") and "总权重" in file:
        feature_classes.append(os.path.join(input_folder, file))

# 存储分类范围和统计结果的字典
classification_ranges = {}
overall_stats = {}
zone_stats = {zone: {} for zone in zone_names}

# 处理每个矢量文件
print("开始处理矢量文件...")
for fc in tqdm(feature_classes, desc="处理矢量文件"):
    try:
        # 提取年份
        fc_name = os.path.basename(fc)
        year = fc_name.split("_")[-1].split(".")[0]
        
        # 添加字段
        d_field = f"d_{year}"
        z_field = f"z_{year}"
        
        # 检查字段是否已存在，避免重复添加
        field_names = [field.name for field in arcpy.ListFields(fc)]
        if d_field not in field_names:
            # 尝试多次添加字段，避免锁定问题
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    arcpy.AddField_management(fc, d_field, "SHORT")
                    break
                except:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2)  # 等待2秒后重试
                    
        if z_field not in field_names:
            # 尝试多次添加字段，避免锁定问题
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    arcpy.AddField_management(fc, z_field, "TEXT", field_length=10)
                    break
                except:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2)  # 等待2秒后重试
        
        # 获取b1字段值
        b1_field = f"b1_{year}"
        values = []
        with arcpy.da.SearchCursor(fc, [b1_field]) as cursor:
            for row in cursor:
                if row[0] is not None:
                    values.append(row[0])
        
        # 使用Jenks自然间断点分类法分为5类
        if len(values) >= 5:  # 确保有足够的数据点进行分类
            try:
                # 使用jenkspy计算自然间断点
                breaks = jenkspy.jenks_breaks(values, n_classes=5)
                
                # 存储分类范围
                classification_ranges[year] = {
                    "差": (breaks[0], breaks[1]),
                    "低": (breaks[1], breaks[2]),
                    "中": (breaks[2], breaks[3]),
                    "良": (breaks[3], breaks[4]),
                    "优": (breaks[4], breaks[5])
                }
                
                # 更新字段值
                with arcpy.da.UpdateCursor(fc, [b1_field, d_field, z_field]) as cursor:
                    for row in cursor:
                        if row[0] is not None:
                            if row[0] <= breaks[1]:
                                row[1], row[2] = 1, "差"
                            elif row[0] <= breaks[2]:
                                row[1], row[2] = 2, "低"
                            elif row[0] <= breaks[3]:
                                row[1], row[2] = 3, "中"
                            elif row[0] <= breaks[4]:
                                row[1], row[2] = 4, "良"
                            else:
                                row[1], row[2] = 5, "优"
                            cursor.updateRow(row)
                
                # 统计整体区域
                overall_stats[year] = {"差": 0, "低": 0, "中": 0, "良": 0, "优": 0}
                with arcpy.da.SearchCursor(fc, [z_field]) as cursor:
                    for row in cursor:
                        if row[0] in overall_stats[year]:
                            overall_stats[year][row[0]] += 1
                
                # 对每个功能区进行裁剪和统计
                for i, mask_raster in enumerate(mask_rasters):
                    zone_name = zone_names[i]
                    output_fc = os.path.join(output_folder, zone_name, f"{zone_name}_{year}.shp")
                    
                    # 如果输出文件已存在，先删除
                    if arcpy.Exists(output_fc):
                        arcpy.Delete_management(output_fc)
                    
                    # 使用栅格作为掩膜提取矢量
                    # 首先将栅格转换为多边形，然后进行裁剪
                    temp_polygon = os.path.join("in_memory", f"temp_mask_{zone_name}_{year}")
                    
                    # 如果临时多边形已存在，先删除
                    if arcpy.Exists(temp_polygon):
                        arcpy.Delete_management(temp_polygon)
                    
                    try:
                        # 将栅格转换为多边形
                        arcpy.conversion.RasterToPolygon(
                            mask_raster, temp_polygon, "NO_SIMPLIFY", "VALUE"
                        )
                        
                        # 裁剪矢量
                        arcpy.analysis.Clip(fc, temp_polygon, output_fc)
                        
                        # 统计功能区
                        zone_stats[zone_name][year] = {"差": 0, "低": 0, "中": 0, "良": 0, "优": 0}
                        with arcpy.da.SearchCursor(output_fc, [z_field]) as cursor:
                            for row in cursor:
                                if row[0] in zone_stats[zone_name][year]:
                                    zone_stats[zone_name][year][row[0]] += 1
                                    
                    except Exception as e:
                        print(f"裁剪{fc}到{zone_name}时出错: {str(e)}")
                    finally:
                        # 删除临时文件
                        if arcpy.Exists(temp_polygon):
                            arcpy.Delete_management(temp_polygon)
                            
            except Exception as e:
                print(f"处理{fc}时出错: {str(e)}")
        else:
            print(f"数据点不足，无法对{fc}进行自然间断分类")
            
    except Exception as e:
        print(f"处理{fc}时发生严重错误: {str(e)}")
        # 继续处理下一个文件
        continue

print("处理完成，正在生成Excel报告...")

# 创建Excel文件
excel_path = os.path.join(output_folder, "统计分析结果.xlsx")

# 第一个sheet：分类范围
class_ranges_data = []
for year, ranges in classification_ranges.items():
    row = [year]
    for category in ["差", "低", "中", "良", "优"]:
        row.append(f"{ranges[category][0]:.4f} - {ranges[category][1]:.4f}")
    class_ranges_data.append(row)

class_ranges_df = pd.DataFrame(
    class_ranges_data, 
    columns=["年份", "差", "低", "中", "良", "优"]
)

# 第二个sheet：整体区域统计
overall_data = []
for year, stats in overall_stats.items():
    row = [year]
    for category in ["差", "低", "中", "良", "优"]:
        row.append(stats[category])
    overall_data.append(row)

overall_df = pd.DataFrame(
    overall_data,
    columns=["年份", "差", "低", "中", "良", "优"]
)

# 后三个sheet：功能区统计
zone_dfs = {}
for zone in zone_names:
    zone_data = []
    for year, stats in zone_stats[zone].items():
        row = [year]
        for category in ["差", "低", "中", "良", "优"]:
            row.append(stats[category])
        zone_data.append(row)
    
    zone_dfs[zone] = pd.DataFrame(
        zone_data,
        columns=["年份", "差", "低", "中", "良", "优"]
    )

# 使用ExcelWriter保存所有sheet
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    class_ranges_df.to_excel(writer, sheet_name="分类范围", index=False)
    overall_df.to_excel(writer, sheet_name="整体区域统计", index=False)
    for zone, df in zone_dfs.items():
        df.to_excel(writer, sheet_name=f"{zone}统计", index=False)

print(f"处理完成！结果已保存到: {excel_path}")

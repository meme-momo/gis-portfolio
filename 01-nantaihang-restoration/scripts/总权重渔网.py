# -*- coding: utf-8 -*-
import arcpy
import os
import glob
import re
from arcpy.sa import *
import shutil
import numpy as np

# 检查并启用Spatial扩展
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# ========== 配置参数 ==========
# 全区渔网数据路径
fishnet_path = r"F:\dasai\南太行渔网\fish1.shp"  # 请替换为实际路径

# 全区栅格数据文件夹路径
raster_folder = r"F:\dasai\南太行数据\总权重"  # 请替换为实际路径

# 输出矢量文件夹名称
output_vector_folder = "矢量"

# ========== 函数定义 ==========
def extract_years_from_files(folder_path):
    """从文件夹中的文件名提取所有年份"""
    years = set()
    for file in glob.glob(os.path.join(folder_path, "*.tif")):
        # 使用正则表达式查找4位数字的年份
        match = re.search(r'(\d{4})', os.path.basename(file))
        if match:
            years.add(match.group(1))
    return sorted(list(years))

def create_vector_folder(base_path):
    """创建矢量文件夹，如果已存在则先删除"""
    vector_path = os.path.join(base_path, output_vector_folder)
    
    # 如果文件夹已存在，则删除其内容
    if os.path.exists(vector_path):
        try:
            shutil.rmtree(vector_path)
            print(f"已删除旧矢量文件夹: {vector_path}")
        except Exception as e:
            print(f"删除文件夹时出错: {e}")
            return None
    
    # 创建新文件夹
    os.makedirs(vector_path)
    print(f"已创建矢量文件夹: {vector_path}")
    return vector_path

def get_oid_field_name(feature_class):
    """获取要素类的主键字段名"""
    desc = arcpy.Describe(feature_class)
    return desc.OIDFieldName

def calculate_normalization_values(values):
    """计算标准化所需的统计值"""
    # 移除空值
    valid_values = [v for v in values if v is not None]
    
    if not valid_values:
        return None, None, None, None
    
    # 计算基本统计值
    min_val = min(valid_values)
    max_val = max(valid_values)
    mean_val = np.mean(valid_values)
    std_val = np.std(valid_values)
    
    return min_val, max_val, mean_val, std_val

def process_year_raster(fishnet, raster_path, year, output_vector_folder):
    """处理单年份栅格数据"""
    print(f"处理 {year} 年栅格数据...")
    
    # 提取栅格文件名（不含扩展名）
    raster_name = os.path.splitext(os.path.basename(raster_path))[0]
    
    # 输出矢量文件名
    output_name = f"渔网_{raster_name}.shp"
    output_path = os.path.join(output_vector_folder, output_name)
    
    # 复制渔网数据
    arcpy.CopyFeatures_management(fishnet, output_path)
    print(f"已复制渔网数据到: {output_path}")
    
    # 获取渔网数据的主键字段名
    oid_field = get_oid_field_name(output_path)
    print(f"渔网数据的主键字段: {oid_field}")
    
    # 添加新字段用于存储平均值
    field_name = f"q{year}"
    
    # 检查字段是否已存在
    field_names = [field.name for field in arcpy.ListFields(output_path)]
    if field_name not in field_names:
        arcpy.AddField_management(output_path, field_name, "DOUBLE")
        print(f"已添加字段: {field_name}")
    
    # 添加标准化字段
    b1_field = f"b1_{year}"  # min-max标准化
    b2_field = f"b2_{year}"  # z-score标准化
    
    if b1_field not in field_names:
        arcpy.AddField_management(output_path, b1_field, "DOUBLE")
        print(f"已添加字段: {b1_field}")
    
    if b2_field not in field_names:
        arcpy.AddField_management(output_path, b2_field, "DOUBLE")
        print(f"已添加字段: {b2_field}")
    
    # 使用Zonal Statistics计算每个格网的平均值
    try:
        # 创建临时表
        temp_table = "in_memory\\zonal_stats"
        
        # 使用ZonalStatisticsAsTable计算统计数据
        out_zonal_table = ZonalStatisticsAsTable(
            output_path,  # 输入区域数据
            oid_field,    # 区域字段
            raster_path,  # 输入栅格数据
            temp_table,   # 输出表
            "DATA",       # 统计类型
            "MEAN"        # 统计方法
        )
        
        # 检查临时表中的字段
        temp_fields = [field.name for field in arcpy.ListFields(temp_table)]
        print(f"临时表字段: {temp_fields}")
        
        # 查找包含区域ID的字段
        zone_field = None
        for field in temp_fields:
            if field.endswith("_" + oid_field) or field == oid_field + "_":
                zone_field = field
                break
        
        if not zone_field:
            # 如果没有找到匹配的字段，尝试使用第一个字段
            zone_field = temp_fields[1]  # 跳过第一个OBJECTID字段
        
        print(f"使用区域字段: {zone_field}")
        
        # 将结果连接到渔网数据
        arcpy.JoinField_management(
            output_path,  # 输入表
            oid_field,    # 输入连接字段
            temp_table,   # 连接表
            zone_field,   # 连接表字段
            ["MEAN"]      # 要连接的字段
        )
        
        # 更新字段值
        with arcpy.da.UpdateCursor(output_path, [field_name, "MEAN"]) as cursor:
            for row in cursor:
                row[0] = row[1]  # 将MEAN值赋给新字段
                cursor.updateRow(row)
        
        # 删除临时字段
        arcpy.DeleteField_management(output_path, "MEAN")
        
        # 删除临时表
        arcpy.Delete_management(temp_table)
        
        # 计算标准化值
        print(f"计算 {year} 年数据的标准化值...")
        
        # 获取所有值
        values = []
        with arcpy.da.SearchCursor(output_path, [field_name]) as cursor:
            for row in cursor:
                values.append(row[0])
        
        # 计算标准化参数
        min_val, max_val, mean_val, std_val = calculate_normalization_values(values)
        
        if min_val is not None:
            # 计算标准化值
            with arcpy.da.UpdateCursor(output_path, [field_name, b1_field, b2_field]) as cursor:
                for row in cursor:
                    if row[0] is not None:
                        # Min-Max 标准化: (x - min) / (max - min)
                        if max_val != min_val:  # 避免除以零
                            row[1] = (row[0] - min_val) / (max_val - min_val)
                        else:
                            row[1] = 0  # 如果所有值相同，设为0
                        
                        # Z-Score 标准化: (x - mean) / std
                        if std_val != 0:  # 避免除以零
                            row[2] = (row[0] - mean_val) / std_val
                        else:
                            row[2] = 0  # 如果标准差为0，设为0
                    
                    cursor.updateRow(row)
        
        print(f"已完成 {year} 年数据处理")
        
    except Exception as e:
        print(f"处理 {year} 年数据时出错: {e}")
        # 打印详细的错误信息
        import traceback
        print(traceback.format_exc())
    
    return output_path

def main():
    """主函数"""
    print("开始处理全区渔网和栅格数据...")
    
    # 检查渔网数据是否存在
    if not arcpy.Exists(fishnet_path):
        print(f"错误: 渔网数据不存在: {fishnet_path}")
        return
    
    # 检查栅格文件夹是否存在
    if not os.path.exists(raster_folder):
        print(f"错误: 栅格文件夹不存在: {raster_folder}")
        return
    
    # 创建矢量文件夹（会先删除已存在的文件夹）
    vector_folder = create_vector_folder(raster_folder)
    if vector_folder is None:
        print("创建矢量文件夹失败，程序终止")
        return
    
    # 获取所有年份
    years = extract_years_from_files(raster_folder)
    if not years:
        print("未找到任何栅格数据文件")
        return
    
    print(f"找到以下年份的数据: {', '.join(years)}")
    
    # 处理每个年份的栅格数据
    for year in years:
        # 查找该年份的栅格文件
        year_files = [f for f in glob.glob(os.path.join(raster_folder, "*.tif")) if year in os.path.basename(f)]
        
        if not year_files:
            print(f"警告: 未找到 {year} 年的栅格文件")
            continue
        
        # 处理该年份的第一个文件（如果有多个，取第一个）
        raster_path = year_files[0]
        process_year_raster(fishnet_path, raster_path, year, vector_folder)
    
    print("\n处理完成！")
    print(f"结果保存在: {vector_folder}")

if __name__ == "__main__":
    main()

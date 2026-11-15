# -*- coding: utf-8 -*-
import arcpy
import os
import glob
import re
from arcpy.sa import *
import shutil

# 检查并启用Spatial扩展
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# ========== 配置参数 ==========
# 基础路径
base_dir = r"F:\dasai\南太行数据"

# 功能区列表
functional_areas = ["矿山治理区", "生态涵养区", "水生态保护区"]

# 标准栅格路径 - 请根据实际情况修改这些路径
standard_rasters = {
    "矿山治理区": r"F:\dasai\ESV(1.21)\栅格分区\矿山治理区.tif",
    "生态涵养区": r"F:\dasai\ESV(1.21)\栅格分区\生态涵养区.tif", 
    "水生态保护区": r"F:\dasai\ESV(1.21)\栅格分区\水生态保护区1.tif",
    "总体": r"F:\dasai\ESV(1.21)\南太行CLCD\Reclass_tudi_2015.tif"
}

# 输出目录
output_dir = os.path.join(base_dir, "总权重")

# 临时文件夹列表，用于最后清理
temp_folders = []

# ========== 函数定义 ==========
def clear_folder(path):
    """清空文件夹"""
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"已清空文件夹: {path}")
    os.makedirs(path, exist_ok=True)

def replace_nodata_with_zero(input_raster_path, output_raster_path):
    """将栅格中的NoData值替换为0"""
    try:
        input_raster = Raster(input_raster_path)
        output_raster = Con(IsNull(input_raster), 0, input_raster)
        output_raster.save(output_raster_path)
        return output_raster_path
    except Exception as e:
        print(f"替换NoData失败: {e}")
        return None

def create_zero_raster(template_raster, output_path):
    """创建与模板相同大小的零值栅格"""
    try:
        template = Raster(template_raster)
        zero_raster = Con(IsNull(template), 0, 0)
        zero_raster.save(output_path)
        return output_path
    except Exception as e:
        print(f"创建零值栅格失败: {e}")
        return None

def normalize_raster(input_raster_path, output_raster_path):
    """将栅格数据标准化到0-1范围"""
    try:
        raster = Raster(input_raster_path)
        
        # 获取最小最大值
        min_result = arcpy.GetRasterProperties_management(raster, "MINIMUM")
        max_result = arcpy.GetRasterProperties_management(raster, "MAXIMUM")
        min_val = float(min_result.getOutput(0))
        max_val = float(max_result.getOutput(0))
        
        print(f"  原始数据范围: {min_val} - {max_val}")
        
        # 如果所有值相同，则全部设为0.5
        if min_val == max_val:
            normalized_raster = 0.5
            print(f"  警告: 所有值相同({min_val})，标准化为0.5")
        else:
            # 标准化公式: (value - min) / (max - min)
            normalized_raster = (raster - min_val) / (max_val - min_val)
        
        # 保存标准化后的栅格
        normalized_raster.save(output_raster_path)
        
        # 验证标准化结果
        normalized_raster_check = Raster(output_raster_path)
        min_norm = arcpy.GetRasterProperties_management(normalized_raster_check, "MINIMUM")
        max_norm = arcpy.GetRasterProperties_management(normalized_raster_check, "MAXIMUM")
        print(f"  标准化后范围: {float(min_norm.getOutput(0))} - {float(max_norm.getOutput(0))}")
        
        return output_raster_path
    except Exception as e:
        print(f"标准化栅格失败: {e}")
        return None

def extract_years_from_files(folder_path):
    """从文件夹中的文件名提取所有年份"""
    years = set()
    for file in glob.glob(os.path.join(folder_path, "*.tif")):
        # 使用正则表达式查找4位数字的年份
        match = re.search(r'(\d{4})', os.path.basename(file))
        if match:
            years.add(match.group(1))
    return sorted(list(years))

def get_all_years():
    """获取所有功能区中所有指标的所有年份"""
    all_years = set()
    
    for area in functional_areas:
        area_path = os.path.join(base_dir, area)
        if not os.path.exists(area_path):
            continue
            
        indicator_folders = [f for f in os.listdir(area_path) 
                             if os.path.isdir(os.path.join(area_path, f)) and f not in ["总权重", "标准栅格", "temp"]]
        
        for indicator in indicator_folders:
            weight_dir = os.path.join(area_path, indicator, "权重")
            if os.path.exists(weight_dir):
                years = extract_years_from_files(weight_dir)
                all_years.update(years)
    
    return sorted(list(all_years))

def process_functional_area(area_name, target_year):
    """处理单个功能区的特定年份"""
    print(f"\n开始处理 {area_name} {target_year}年数据...")

    area_output_dir = os.path.join(base_dir, area_name, "总权重")
    os.makedirs(area_output_dir, exist_ok=True)

    temp_dir = os.path.join(base_dir, area_name, "temp", target_year)
    clear_folder(temp_dir)
    temp_folders.append(temp_dir)

    if area_name not in standard_rasters or not os.path.exists(standard_rasters[area_name]):
        print(f"错误: {area_name} 的标准栅格不存在: {standard_rasters.get(area_name, '未指定')}")
        return None

    area_path = os.path.join(base_dir, area_name)
    indicator_folders = [f for f in os.listdir(area_path) 
                         if os.path.isdir(os.path.join(area_path, f)) and f not in ["总权重", "标准栅格", "temp"]]

    print(f"找到指标文件夹: {indicator_folders}")

    area_standard_raster = Raster(standard_rasters[area_name])
    year_sum_raster = None

    for indicator in indicator_folders:
        weight_dir = os.path.join(area_path, indicator, "权重")
        if not os.path.exists(weight_dir):
            print(f"  {indicator} 缺少权重文件夹")
            continue

        year_files = [f for f in glob.glob(os.path.join(weight_dir, "*.tif")) if target_year in os.path.basename(f)]

        if not year_files:
            print(f"  {indicator} 缺少 {target_year} 年数据，使用零值替代")
            zero_raster_path = os.path.join(temp_dir, f"zero_{target_year}.tif")
            zero_raster = create_zero_raster(area_standard_raster, zero_raster_path)
            if zero_raster:
                indicator_raster = Raster(zero_raster)
            else:
                continue
        else:
            try:
                processed_raster_path = os.path.join(temp_dir, f"processed_{indicator}_{target_year}.tif")
                processed_raster = replace_nodata_with_zero(year_files[0], processed_raster_path)
                if processed_raster:
                    indicator_raster = Raster(processed_raster)
                    print(f"  使用 {indicator} 数据: {os.path.basename(year_files[0])} (已处理NoData)")
                else:
                    continue
            except Exception as e:
                print(f"  无法读取栅格文件 {year_files[0]}: {e}")
                continue

        try:
            masked_raster = ExtractByMask(indicator_raster, area_standard_raster)
        except Exception as e:
            print(f"  掩膜提取失败: {e}")
            continue

        if year_sum_raster is None:
            year_sum_raster = masked_raster
        else:
            year_sum_raster = year_sum_raster + masked_raster

    if year_sum_raster is not None:
        # 保存原始总和到功能区输出目录
        output_path = os.path.join(area_output_dir, f"{area_name}_总权重2_{target_year}.tif")
        try:
            year_sum_raster.save(output_path)
            print(f"  {area_name} {target_year}年总权重已保存: {output_path}")
            
            # 标准化处理并保存到临时文件夹
            normalized_path = os.path.join(temp_dir, f"{area_name}_normalized_{target_year}.tif")
            normalized_raster = normalize_raster(output_path, normalized_path)
            
            if normalized_raster:
                return normalized_raster  # 返回标准化后的路径用于拼接
            else:
                print(f"  标准化失败，使用原始数据进行拼接")
                return output_path
        except Exception as e:
            print(f"  保存失败: {e}")
            return None
    else:
        print(f"  警告: {area_name} {target_year}年无有效数据")
        return None

def combine_all_areas(target_year, normalized_rasters):
    """拼接所有功能区的特定年份总权重栅格"""
    print(f"\n开始拼接所有功能区 {target_year} 年数据...")

    # 准备拼接的栅格
    mosaic_rasters = []
    for area, raster_path in normalized_rasters.items():
        if raster_path and os.path.exists(raster_path):
            print(f"  已准备 {area} 标准化数据: {raster_path}")
            mosaic_rasters.append(raster_path)
        else:
            print(f"  ⚠️ 缺少 {area} 的 {target_year} 标准化数据，跳过")

    if not mosaic_rasters:
        print(f"❌ 没有找到任何功能区的 {target_year} 标准化数据，拼接终止")
        return

    # 输出路径
    output_path = os.path.join(output_dir, f"总体_总权重2_{target_year}.tif")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 调用 MosaicToNewRaster
    try:
        arcpy.MosaicToNewRaster_management(
            mosaic_rasters,                                    # 输入栅格列表
            os.path.dirname(output_path),                      # 输出目录
            os.path.basename(output_path),                     # 输出文件名
            Raster(standard_rasters["总体"]).spatialReference, # 坐标系
            "32_BIT_FLOAT",                                    # 像元类型
            Raster(standard_rasters["总体"]).meanCellWidth,    # 像元大小
            1,                                                 # 波段数
            "MAXIMUM",                                         # 拼接方法
            "FIRST"                                            # 色彩表
        )
        print(f"✅ 所有功能区 {target_year} 年总权重已拼接完成: {output_path}")
    except Exception as e:
        print(f"❌ 拼接失败: {e}")

def clean_temp_folders():
    """清理所有临时文件夹"""
    print("\n清理临时文件夹...")
    for temp_dir in temp_folders:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"已清理临时文件夹: {temp_dir}")
        except Exception as e:
            print(f"清理临时文件夹失败 {temp_dir}: {e}")

def main():
    """主函数"""
    global temp_folders

    print(f"开始处理南太行数据所有年份权重栅格...")
    print(f"基础目录: {base_dir}")

    # 获取所有可用的年份
    all_years = get_all_years()
    if not all_years:
        print("❌ 没有找到任何年份的数据")
        return
    
    print(f"找到以下年份的数据: {', '.join(all_years)}")

    # 清空输出目录
    clear_folder(output_dir)

    # 清理上次的临时文件夹
    print("清理上次的临时文件夹...")
    for area in functional_areas:
        temp_area_dir = os.path.join(base_dir, area, "temp")
        if os.path.exists(temp_area_dir):
            shutil.rmtree(temp_area_dir)
            print(f"已清理临时文件夹: {temp_area_dir}")

    temp_folders = []

    print("检查标准栅格...")
    for area, path in standard_rasters.items():
        if os.path.exists(path):
            print(f"  {area}: 存在 ({path})")
        else:
            print(f"  {area}: 不存在 ({path})")

    try:
        # 处理每个年份
        for year in all_years:
            print(f"\n{'='*50}")
            print(f"开始处理 {year} 年数据")
            print(f"{'='*50}")
            
            # 处理每个功能区，收集标准化后的栅格路径
            normalized_rasters = {}
            for area in functional_areas:
                normalized_path = process_functional_area(area, year)
                normalized_rasters[area] = normalized_path

            # 拼接所有功能区（使用标准化后的数据）
            combine_all_areas(year, normalized_rasters)

        print(f"\n所有年份处理完成！结果保存在:")
        print(f"各功能区总权重（原始值）: {base_dir}\\各功能区名称\\总权重\\")
        print(f"总体总权重（标准化后拼接）: {output_dir}\\")
    finally:
        # 确保最后清理临时文件夹
        clean_temp_folders()

if __name__ == "__main__":
    main()

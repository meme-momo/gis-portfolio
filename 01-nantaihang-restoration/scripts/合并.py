import arcpy
import os
import shutil
import importlib.util

# ================== 参数设置 ==================
root_folder = r"dasai\南太行数据"
exclude_folder = "适生林地占比"  # 不动
overall_raster = r"dasai\ESV(1.21)\南太行CLCD\Reclass_tudi_2013.tif"  # 整体区域栅格

arcpy.env.overwriteOutput = True

# ================== 遍历功能区和指标 ==================
def process_folder(base_path, output_type="原始", input_raster=None):
    """
    base_path: 功能区或总文件夹
    output_type: '原始'
    input_raster: 如果给定，则用整体栅格
    """
    for func_area in os.listdir(base_path):
        func_area_path = os.path.join(base_path, func_area)
        if not os.path.isdir(func_area_path) or func_area == exclude_folder:
            continue

        for indicator in os.listdir(func_area_path):
            indicator_path = os.path.join(func_area_path, indicator)
            if not os.path.isdir(indicator_path):
                continue

            py_files = [f for f in os.listdir(indicator_path) if f.endswith(".py")]
            if not py_files:
                continue

            # 创建输出文件夹
            raw_folder = os.path.join(indicator_path, output_type)
            os.makedirs(raw_folder, exist_ok=True)

            for py_file in py_files:
                py_path = os.path.join(indicator_path, py_file)

                # 动态导入脚本模块
                spec = importlib.util.spec_from_file_location("module.name", py_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 执行脚本主函数
                # 假设原脚本支持传入 output_folder, standardize=False, input_raster
                if hasattr(module, "main"):
                    kwargs = {"output_folder": raw_folder, "standardize": False}
                    if input_raster:
                        kwargs["input_raster"] = input_raster
                    module.main(**kwargs)
                elif hasattr(module, "process_raster"):
                    kwargs = {"output_folder": raw_folder, "standardize": False}
                    if input_raster:
                        kwargs["input_raster"] = input_raster
                    module.process_raster(**kwargs)

# ================== 处理各功能区原始数据 ==================
print("🗂 处理各功能区原始数据...")
process_folder(root_folder, output_type="原始")

# ================== 处理整体区域 ==================
print("🌐 处理整体区域...")
overall_folder = os.path.join(root_folder, "整体")
os.makedirs(overall_folder, exist_ok=True)

for func_area in os.listdir(root_folder):
    func_area_path = os.path.join(root_folder, func_area)
    if not os.path.isdir(func_area_path) or func_area == exclude_folder:
        continue

    for indicator in os.listdir(func_area_path):
        indicator_path = os.path.join(func_area_path, indicator)
        if not os.path.isdir(indicator_path):
            continue

        overall_indicator_folder = os.path.join(overall_folder, indicator, "原始")
        os.makedirs(overall_indicator_folder, exist_ok=True)

        py_files = [f for f in os.listdir(indicator_path) if f.endswith(".py")]
        for py_file in py_files:
            py_path = os.path.join(indicator_path, py_file)

            spec = importlib.util.spec_from_file_location("module.name", py_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 执行脚本，但用整体栅格
            if hasattr(module, "main"):
                module.main(input_raster=overall_raster,
                            output_folder=overall_indicator_folder,
                            standardize=False)
            elif hasattr(module, "process_raster"):
                module.process_raster(input_raster=overall_raster,
                                      output_folder=overall_indicator_folder,
                                      standardize=False)

print("🎉 全部原始数据处理完成")

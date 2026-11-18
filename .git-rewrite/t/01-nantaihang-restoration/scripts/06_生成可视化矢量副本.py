# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
import re
from tqdm import tqdm

# === 参数设置 ===
root_folder = r"dasai\南太行数据"  # 功能区总文件夹
unified_folder = r"dasai\南太行数据\统一可视化"  # 统一输出文件夹
os.makedirs(unified_folder, exist_ok=True)

# 遍历功能区和指标
for fc_name in tqdm(os.listdir(root_folder), desc="功能区", unit="区"):
    fc_path = os.path.join(root_folder, fc_name)
    if not os.path.isdir(fc_path):
        continue

    for ind_name in tqdm(os.listdir(fc_path), desc=f"{fc_name} 指标", unit="指标", leave=False):
        ind_path = os.path.join(fc_path, ind_name)
        vis_folder = os.path.join(ind_path, "可视化")
        if not os.path.exists(vis_folder):
            continue

        # 遍历可视化文件夹中的所有 .shp 文件及关联文件
        for file_name in os.listdir(vis_folder):
            if not file_name.lower().endswith(".shp"):
                continue
            base_name = os.path.splitext(file_name)[0]

            # 构造输出路径
            fc_ind_folder = os.path.join(unified_folder, f"{fc_name}_{ind_name}")
            os.makedirs(fc_ind_folder, exist_ok=True)
            src_shp = os.path.join(vis_folder, file_name)
            dst_shp = os.path.join(fc_ind_folder, file_name)

            try:
                # 复制 .shp 及其关联文件（.shx, .dbf, .prj, .cpg 等）
                extensions = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".cpg", ".xml"]
                for ext in extensions:
                    src_file = os.path.join(vis_folder, base_name + ext)
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, fc_ind_folder)
            except Exception as e:
                print(f"❌ 复制失败: 功能区={fc_name}, 指标={ind_name}, 文件={file_name}, 错误={e}")

print("🎉 所有可视化矢量已复制到统一文件夹！")

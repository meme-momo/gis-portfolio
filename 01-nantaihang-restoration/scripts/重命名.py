# -*- coding: utf-8 -*-
import os
import re
import shutil

# ✅ 顶层目录
top_folder = r"dasai\南太行数据"

# ✅ 匹配年份（4位数字）
year_pattern = re.compile(r"(\d{4})")

# ✅ 特殊扩展名（优先匹配）
special_exts = [
    ".tif.vat.dbf", ".tif.vat.cpg", ".tif.xml",  # 栅格附属
    ".shp", ".shx", ".dbf", ".prj", ".cpg"       # 矢量附属
]

def get_special_ext(filename):
    """返回文件的特殊扩展名，如果没有则返回普通扩展名"""
    for ext in special_exts:
        if filename.lower().endswith(ext):
            return ext
    return os.path.splitext(filename)[1]

# ✅ 遍历所有文件
for root, dirs, files in os.walk(top_folder):
    parts = os.path.normpath(root).split(os.sep)

    # 至少要有两级：...\\指标名\\子文件夹（不限更深）
    if len(parts) < 3:
        continue

    indicator_name = parts[-2]   # 倒数第二层作为指标名
    subfolder_name = parts[-1]   # 最后一层作为子目录名

    for filename in files:
        if filename.lower().endswith(".py"):  # 跳过脚本
            continue

        old_path = os.path.join(root, filename)

        # 已符合命名规则，跳过
        if f"{indicator_name}_{subfolder_name}_" in filename:
            print(f"⏭ 已符合命名规则，跳过：{filename}")
            continue

        # 查找年份
        match = year_pattern.search(filename)
        if not match:
            print(f"⚠ 无年份匹配，跳过：{filename}")
            continue

        year = match.group(1)

        # 处理扩展名（支持多重）
        ext = get_special_ext(filename)

        # 生成新文件名
        new_filename = f"{indicator_name}_{subfolder_name}_{year}{ext}"
        new_path = os.path.join(root, new_filename)

        # 目标存在就跳过
        if os.path.exists(new_path):
            print(f"⏭ 目标文件已存在，跳过：{new_filename}")
            continue

        try:
            os.rename(old_path, new_path)
            print(f"✅ 重命名：{filename} -> {new_filename}")
        except Exception as e:
            print(f"❌ 重命名失败：{filename} -> {new_filename}，原因：{e}")

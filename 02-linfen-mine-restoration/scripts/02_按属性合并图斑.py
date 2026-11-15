import arcpy
import os
import re

# ------------------- 文件名合法化函数 -------------------

def clean_filename_for_shp(name, prefix="m_"):
    """为合并文件生成合法 shp 名称，保留中文、数字、字母"""
    name = re.sub(r'[\\/:*?"<>|]', "_", str(name))
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) == 0:
        name = prefix + "unknown"
    return name[:50]

def clean_name(name, prefix="fc_"):
    """生成 ArcGIS 合法 shp 名称（仅 ASCII），用于 BSM shp"""
    name = re.sub(r'[^A-Za-z0-9_]+', "_", str(name))
    if re.match(r'^[0-9]', name):
        name = prefix + name
    name = re.sub(r'_+', "_", name).strip("_")
    if len(name) == 0:
        name = prefix + "unknown"
    return name[:50]

def clean_group_name(name):
    """为组文件夹和合并文件生成合法名称"""
    name = re.sub(r'[\\/:*?"<>|]', "_", str(name))
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) == 0:
        name = "unknown_group"
    return name[:50]

# ------------------- 主函数 -------------------

def split_and_project_shp(input_fc, output_root):
    arcpy.env.overwriteOutput = True

    target_sr = arcpy.SpatialReference(4547)
    ZXMMC_field = "ziname"  # 分组字段
    BSM_field = "zibianhao"           # 单条 shp 字段

    # 临时投影文件夹
    temp_folder = os.path.join(output_root, "temp")
    os.makedirs(temp_folder, exist_ok=True)
    projected_fc = os.path.join(temp_folder, "projected.shp")

    print("正在投影到 CGCS2000 GK CM 111E (EPSG:4547)...")
    arcpy.Project_management(input_fc, projected_fc, target_sr)

    print("读取 ZXMMC 分组值...")
    ZXMMC_values = sorted(set(r[0] for r in arcpy.da.SearchCursor(projected_fc, [ZXMMC_field])))
    oid_field = arcpy.Describe(projected_fc).OIDFieldName
    print("发现 OID 字段：", oid_field)

    merge_root = os.path.join(output_root, "合并")
    os.makedirs(merge_root, exist_ok=True)

    # ------------------- 按组处理 -------------------
    for value in ZXMMC_values:
        print(f"\n=== 正在处理：{value} ===")

        safe_value = clean_group_name(str(value))
        group_folder = os.path.join(output_root, safe_value)
        os.makedirs(group_folder, exist_ok=True)

        where = f"{ZXMMC_field} = '{value}'"

        # ------------------- 收集同一 BSM 的 OID -------------------
        bsm_to_oids = {}
        with arcpy.da.SearchCursor(projected_fc, [oid_field, BSM_field], where_clause=where) as cursor:
            for oid, bsm in cursor:
                bsm_to_oids.setdefault(str(bsm), []).append(oid)

        shp_list = []

        for bsm, oid_list in bsm_to_oids.items():
            safe_bsm = clean_name(str(bsm), prefix="BSM_")
            out_shp = os.path.join(group_folder, f"{safe_bsm}.shp")

            # 构建 OR 表达式导出多个 OID
            if len(oid_list) == 1:
                where_clause = f"{oid_field} = {oid_list[0]}"
            else:
                where_clause = " OR ".join([f"{oid_field} = {oid}" for oid in oid_list])

            print(f"  → 导出 BSM {safe_bsm}.shp (共 {len(oid_list)} 条记录)")
            arcpy.Select_analysis(projected_fc, out_shp, where_clause)
            shp_list.append(out_shp)

        # ------------------- 合并组内所有 shp -------------------
        merge_shp_name = clean_filename_for_shp(str(value)) + ".shp"
        merge_shp_path = os.path.join(merge_root, merge_shp_name)

        if len(shp_list) > 1:
            print(f"  → 合并输出：{merge_shp_path}")
            arcpy.Merge_management(shp_list, merge_shp_path)
        elif len(shp_list) == 1:
            print(f"  → 仅一个 shp，直接复制到合并：{merge_shp_path}")
            arcpy.CopyFeatures_management(shp_list[0], merge_shp_path)

    print("\n全部完成！每条 shp 已按组输出，并生成合并文件。")

# ------------------- 执行 -------------------

input_fc = r"linfen\patch\shp.gdb\patch2"
output_root = r"linfen\patch\矿山子项目"

split_and_project_shp(input_fc, output_root)

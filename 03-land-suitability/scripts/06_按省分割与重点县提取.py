# -*- coding: utf-8 -*-
"""
油茶适宜性栅格分割与重点县提取工具
功能：
1. 按7个省分割土地综合适宜性栅格
2. 从全国区县中筛选出7个省的区县矢量
3. 提取158个油茶生产重点县矢量
4. 可选：按每个重点县裁剪栅格

依赖：pip install rasterio geopandas shapely
"""

import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping

# ==================== 路径配置 ====================
RASTER_PATH = r"gt\result\tudisy1.tif"              # 土地综合适宜性栅格
COUNTY_SHP = r"学习用\审图号：GS(2024)0650\quxian.shp"  # 全国区县矢量
PROVINCE_SHP = r"gt\shp\quyu.shp"                   # 7个省的省矢量

OUTPUT_DIR = r"gt\result\分省"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 字段名配置
PROV_NAME_FIELD = "name"      # 省矢量的省名字段
COUNTY_NAME_FIELD = "name"    # 区县矢量的县名字段

# ==================== 158个重点县名单 ====================
KEY_COUNTIES = [
    # ===== 湖南省（63个）=====
    "鼎城区", "汉寿县", "临澧县", "桃源县",
    "安仁县", "桂阳县", "临武县", "苏仙区", "宜章县", "永兴县", "资兴市",
    "常宁市", "衡东县", "衡南县", "衡山县", "衡阳县", "耒阳市", "祁东县",
    "辰溪县", "洪江市", "会同县", "通道侗族自治县", "溆浦县", "沅陵县", "中方县",
    "涟源市", "双峰县", "新化县",
    "洞口县", "隆回县", "邵东市", "邵阳县", "绥宁县", "武冈市", "新邵县",
    "湘潭县", "湘乡市",
    "凤凰县", "古丈县", "花垣县", "龙山县", "泸溪县", "永顺县",
    "安化县",
    "道县", "东安县", "江华瑶族自治县", "冷水滩区", "零陵区", "宁远县", "祁阳市",
    "临湘市", "汨罗市", "平江县", "岳阳县",
    "桑植县",
    "浏阳市", "宁乡市",
    "茶陵县", "醴陵市", "渌口区", "炎陵县", "攸县",

    # ===== 江西省（35个）=====
    "赣县区", "瑞金市", "上犹县", "信丰县", "兴国县", "于都县",
    "上栗县",
    "广信区", "横峰县", "鄱阳县", "铅山县", "婺源县", "玉山县",
    "丰城市", "高安市", "宜丰县", "袁州区",
    "崇仁县", "广昌县", "乐安县", "临川区",
    "吉安县", "吉水县", "遂川县", "泰和县", "永丰县", "永新县", "万安县",
    "武宁县", "修水县",
    "分宜县", "渝水区",
    "进贤县",
    "德兴市", "贵溪市",

    # ===== 广西壮族自治区（27个）=====
    "乐业县", "凌云县", "隆林各族自治县",
    "平南县",
    "田东县", "田林县", "田阳区", "西林县", "右江区",
    "龙胜各族自治县",
    "巴马瑶族自治县", "东兰县", "凤山县", "环江毛南族自治县",
    "金城江区", "罗城仫佬族自治县", "天峨县", "宜州区",
    "八步区", "平桂区", "昭平县",
    "金秀县",
    "鹿寨县", "融安县", "融水苗族自治县", "三江侗族自治县",
    "藤县",

    # ===== 湖北省（22个）=====
    "黄陂区",
    "红安县", "罗田县", "麻城市", "蕲春县", "浠水县", "英山县",
    "通城县", "通山县", "崇阳县",
    "团风县",
    "钟祥市", "松滋市", "京山市",
    "广水市", "随县",
    "咸丰县", "来凤县",
    "阳新县",
    "南漳县", "谷城县",
    "大悟县",

    # ===== 广东省（5个）=====
    "东源县", "和平县", "龙川县",
    "高州市",
    "兴宁市",

    # ===== 浙江省（4个）=====
    "常山县", "淳安县",
    "莲都区", "青田县",

    # ===== 福建省（2个）=====
    "福安市", "尤溪县",
]


# ==================== 功能1：按省分割栅格 ====================
def clip_raster_by_province():
    """用省矢量裁剪栅格，每个省输出一个tif"""
    print("=" * 50)
    print("【功能1】按省分割适宜性栅格")
    print("=" * 50)

    prov_gdf = gpd.read_file(PROVINCE_SHP)
    print(f"省矢量共 {len(prov_gdf)} 个要素")

    with rasterio.open(RASTER_PATH) as src:
        print(f"栅格信息：{src.width} x {src.height}, CRS: {src.crs}")

        if src.crs != prov_gdf.crs:
            print(f"坐标系不一致，正在转换矢量坐标系...")
            prov_gdf = prov_gdf.to_crs(src.crs)

        for idx, row in prov_gdf.iterrows():
            prov_name = row[PROV_NAME_FIELD]
            print(f"\n正在裁剪: {prov_name} ...")

            geoms = [mapping(row.geometry)]

            try:
                out_image, out_transform = mask(
                    src, geoms, crop=True, nodata=src.nodata
                )

                out_meta = src.meta.copy()
                out_meta.update({
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })

                safe_name = str(prov_name).replace(" ", "").replace("/", "_")
                out_path = os.path.join(OUTPUT_DIR, f"{safe_name}_适宜性.tif")

                with rasterio.open(out_path, "w", **out_meta) as dest:
                    dest.write(out_image)

                print(f"  ✅ 输出完成: {out_path}")
                print(f"     尺寸: {out_image.shape[2]} x {out_image.shape[1]}")

            except Exception as e:
                print(f"  ❌ 裁剪失败: {e}")

    print("\n" + "=" * 50)
    print("✅ 按省分割栅格完成！")
    print("=" * 50 + "\n")


# ==================== 功能2：提取7个省的区县矢量 ====================
def extract_7provinces_counties():
    """从全国区县中筛选7个省的区县，输出shp"""
    print("=" * 50)
    print("【功能2】提取7个省的区县矢量")
    print("=" * 50)

    county_gdf = gpd.read_file(COUNTY_SHP)
    prov_gdf = gpd.read_file(PROVINCE_SHP)

    print(f"全国区县共 {len(county_gdf)} 个")

    # ===== 修复：先把省矢量的name字段改名为"所属省"，避免join后字段名冲突 =====
    prov_gdf = prov_gdf.rename(columns={PROV_NAME_FIELD: "所属省"})
    # 只保留省名和几何，减少冗余字段
    prov_gdf = prov_gdf[["所属省", "geometry"]]

    # 统一坐标系
    if county_gdf.crs != prov_gdf.crs:
        county_gdf = county_gdf.to_crs(prov_gdf.crs)

    # 空间join：每个区县匹配所在的省
    counties_with_prov = gpd.sjoin(
        county_gdf,
        prov_gdf,
        how="inner",
        predicate="within"
    )

    # 删除sjoin自动生成的index_right字段
    if "index_right" in counties_with_prov.columns:
        counties_with_prov = counties_with_prov.drop(columns=["index_right"])

    print(f"7个省共匹配到 {len(counties_with_prov)} 个区县")

    # 按省统计
    prov_count = counties_with_prov["所属省"].value_counts()
    print("\n各省区县数量：")
    for prov, cnt in prov_count.items():
        print(f"  {prov}: {cnt} 个")

    # 输出
    out_shp = os.path.join(OUTPUT_DIR, "7个省_区县矢量.shp")
    counties_with_prov.to_file(out_shp, encoding="utf-8")
    print(f"\n✅ 7个省区县矢量已输出: {out_shp}")

    return counties_with_prov


# ==================== 功能3：提取158个重点县矢量 ====================
def extract_key_counties(counties_7prov=None):
    """从7个省区县中筛选158个重点县"""
    print("\n" + "=" * 50)
    print("【功能3】提取158个油茶生产重点县")
    print("=" * 50)

    if counties_7prov is None:
        counties_7prov = extract_7provinces_counties()

    # 筛选重点县
    key_counties_gdf = counties_7prov[
        counties_7prov[COUNTY_NAME_FIELD].isin(KEY_COUNTIES)
    ].copy()

    matched_count = len(key_counties_gdf)
    print(f"\n匹配到 {matched_count} / {len(KEY_COUNTIES)} 个重点县")

    # 检查未匹配的县
    matched_names = set(key_counties_gdf[COUNTY_NAME_FIELD].tolist())
    unmatched = [c for c in KEY_COUNTIES if c not in matched_names]

    if unmatched:
        print(f"\n⚠️  未匹配到的县（{len(unmatched)}个）：")
        for name in unmatched:
            print(f"   - {name}")
        print("   提示：可能是区县名称写法不同，可在属性表中确认后手动补充")
    else:
        print("✅ 全部158个重点县匹配成功！")

    # 按省统计
    prov_count = key_counties_gdf["所属省"].value_counts()
    print("\n各省重点县数量：")
    for prov, cnt in prov_count.items():
        print(f"  {prov}: {cnt} 个")

    # 输出重点县矢量
    out_shp = os.path.join(OUTPUT_DIR, "油茶重点县_158个.shp")
    key_counties_gdf.to_file(out_shp, encoding="utf-8")
    print(f"\n✅ 重点县矢量已输出: {out_shp}")

    return key_counties_gdf


# ==================== 功能4：按重点县分割栅格（可选）====================
def clip_raster_by_key_counties(key_counties_gdf=None):
    """按每个重点县裁剪栅格"""
    print("\n" + "=" * 50)
    print("【功能4】按重点县分割栅格（可选）")
    print("=" * 50)

    if key_counties_gdf is None:
        key_counties_gdf = extract_key_counties()

    county_dir = os.path.join(OUTPUT_DIR, "分县栅格")
    os.makedirs(county_dir, exist_ok=True)

    with rasterio.open(RASTER_PATH) as src:
        if src.crs != key_counties_gdf.crs:
            key_counties_gdf = key_counties_gdf.to_crs(src.crs)

        total = len(key_counties_gdf)
        for i, (idx, row) in enumerate(key_counties_gdf.iterrows(), 1):
            county_name = row[COUNTY_NAME_FIELD]
            prov_name = row["所属省"]
            safe_name = f"{prov_name}_{county_name}".replace(" ", "")

            print(f"[{i}/{total}] 正在裁剪: {prov_name} - {county_name}")

            geoms = [mapping(row.geometry)]

            try:
                out_image, out_transform = mask(
                    src, geoms, crop=True, nodata=src.nodata
                )

                out_meta = src.meta.copy()
                out_meta.update({
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })

                out_path = os.path.join(county_dir, f"{safe_name}_适宜性.tif")
                with rasterio.open(out_path, "w", **out_meta) as dest:
                    dest.write(out_image)

            except Exception as e:
                print(f"  ❌ 失败: {e}")

    print(f"\n✅ 按重点县分割栅格完成！共 {total} 个县")
    print(f"   输出目录: {county_dir}")


# ==================== 主程序 ====================
if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("  油茶适宜性栅格分割与重点县提取工具")
    print("=" * 50 + "\n")

    # 功能1：按省分割栅格（核心需求）
    clip_raster_by_province()

    # 功能2：提取7个省的区县矢量
    counties_7prov = extract_7provinces_counties()

    # 功能3：提取158个重点县矢量
    key_counties = extract_key_counties(counties_7prov)

    # 功能4：按重点县分割栅格（需要时取消注释）
    # clip_raster_by_key_counties(key_counties)

    print("\n" + "=" * 50)
    print("🎉 全部处理完成！")
    print(f"📂 输出目录: {OUTPUT_DIR}")
    print("=" * 50 + "\n")
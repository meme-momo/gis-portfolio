import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict

# ================= 配置 =================
base_dir = r"年鉴"
years = [2023, 2024]
base_urls = {
    2023: "https://oss.henan.gov.cn/sbgt-wztipt/attachment/hntjj/hntj/lib/tjnj/2023nj/zk/lefte.htm",
    2024: "https://oss.henan.gov.cn/sbgt-wztipt/attachment/hntjj/hntj/lib/tjnj/2024nj/zk/indexce.htm"
}

# ================= 工具函数 =================
def get_excel_links(url, year):
    """解析页面，返回所有 Excel 文件的完整 URL 列表"""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        resp.encoding = 'gb2312'
    except Exception as e:
        print(f"[ERROR] 获取网页失败: {url} ({e})")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith(('.xls', '.xlsx')):
            if href.startswith("http"):
                links.append(href)
            else:
                base = f"https://oss.henan.gov.cn/sbgt-wztipt/attachment/hntjj/hntj/lib/tjnj/{year}nj/zk/"
                links.append(base + href.lstrip('./'))
    return links

def download_file(url, save_path):
    """下载文件，如果已存在则跳过"""
    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
        print(f"[SKIP] 已存在: {save_path}")
        return
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(resp.content)
        print(f"[OK] 下载成功: {save_path}")
    except Exception as e:
        print(f"[ERROR] 下载失败: {save_path} ({e})")

# ================= 整合函数 =================
def clean_and_merge_by_category(year_folder, output_dir):
    """
    按大类整合 Excel 文件到一个 Excel，多 sheet：
    - 大类: 文件名前两位 -> 生成一个 Excel
    - 二级分类: 文件名后两位 -> sheet 名
    - 保留所有 sheet，不过滤中文或英文
    """
    excel_files = [f for f in os.listdir(year_folder) if f.lower().endswith(('.xls', '.xlsx'))]
    if not excel_files:
        print(f"[INFO] 没有 Excel 文件可整合: {year_folder}")
        return

    category_dict = defaultdict(list)
    for f in excel_files:
        match = re.match(r'(\d{2})(\d{2})', f)
        if not match:
            print(f"[WARN] 文件名不符合规则，跳过: {f}")
            continue
        main_cat, sub_cat = match.groups()
        category_dict[main_cat].append((f, sub_cat))

    os.makedirs(output_dir, exist_ok=True)

    for main_cat, files in category_dict.items():
        sheets_to_write = []

        for fname, sub_cat in files:
            path = os.path.join(year_folder, fname)
            try:
                with pd.ExcelFile(path) as xl:
                    for sheet_name in xl.sheet_names:
                        df = xl.parse(sheet_name, header=None)
                        if df.empty:
                            continue
                        # 不过滤中文或英文
                        sheet_name_clean = re.sub(r'[\\/*?:[\]]', '', sub_cat)[:31]
                        sheets_to_write.append((df, sheet_name_clean))
            except Exception as e:
                print(f"[ERROR] 处理 {path} 失败 ({e})")

        # 如果没有有效 sheet，则写入占位 sheet 避免 openpyxl 报错
        if not sheets_to_write:
            sheets_to_write.append((pd.DataFrame({"提示": ["此大类下无有效数据"]}), "占位"))

        output_file = os.path.join(output_dir, f"{main_cat}_年鉴.xlsx")
        # 删除已存在文件，确保写入不会报错
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception as e:
                print(f"[ERROR] 无法删除已有文件 {output_file} ({e})")
                continue

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for df, sheet_name_clean in sheets_to_write:
                df.to_excel(writer, sheet_name=sheet_name_clean, index=False, header=False)

        print(f"[OK] {main_cat}_年鉴.xlsx 已生成，包含 {len(sheets_to_write)} 个 sheet")

# ================= 主流程 =================
for year in years:
    print(f"\n[INFO] {year} 年抓取 Excel 链接...")
    url = base_urls[year]
    links = get_excel_links(url, year)
    print(f"[INFO] {year} 年发现 {len(links)} 个 Excel 文件")

    year_folder = os.path.join(base_dir, str(year), "excel")
    os.makedirs(year_folder, exist_ok=True)

    for link in links:
        fname = os.path.basename(link)
        save_path = os.path.join(year_folder, fname)
        download_file(link, save_path)

    # 按大类整合
    output_dir = os.path.join(base_dir, str(year))
    clean_and_merge_by_category(year_folder, output_dir)

print("\n[INFO] 所有年份下载与整合完成！")

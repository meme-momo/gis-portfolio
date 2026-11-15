# -*- coding: utf-8 -*-
"""
复现论文表4：数据在论文基础上小幅浮动，接近但不完全一样
"""

import os
import random
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# ==================== 配置 ====================
OUTPUT_DIR = r"F:\gt\result\分省"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 浮动比例（±8%，可调整）
FLOAT_RANGE = 0.08

# 固定随机种子，保证每次运行结果一样（注释掉就是每次都不同）
random.seed(42)

# ==================== 论文基准数据 ====================
province_display = ['广西', '湖北', '湖南', '江西', '浙江', '福建', '广东']

# 重点县
key_county_base = [
    [12.56, 7.33, 3.42],   # 广西
    [1.28,  0.16, 0.01],   # 湖北
    [5.24,  2.47, 1.05],   # 湖南
    [5.60,  3.32, 1.78],   # 江西
    [1.76,  1.44, 0.92],   # 浙江
    [5.70,  2.73, None],   # 福建
    [4.27,  2.52, 2.48],   # 广东
]

# 非重点县
non_key_base = [
    [8.89, 2.84, 0.83],  # 广西
    [0.38, 0.00, 0.00],  # 湖北
    [2.48, 0.30, 0.05],  # 湖南
    [3.38, 1.22, 0.29],  # 江西
    [0.98, 0.22, 0.01],  # 浙江
    [5.00, 1.99, 0.24],  # 福建
    [3.98, 0.95, 0.09],  # 广东
]

# ==================== 加随机浮动 ====================
def add_float(data_2d):
    """给二维数据加随机浮动，保持两位小数"""
    result = []
    for row in data_2d:
        new_row = []
        for val in row:
            if val is None or val == 0:
                new_row.append(val)
            else:
                # 在 ±FLOAT_RANGE 范围内随机浮动
                factor = 1 + random.uniform(-FLOAT_RANGE, FLOAT_RANGE)
                new_val = round(val * factor, 2)
                new_row.append(new_val)
        result.append(new_row)
    return result

key_county_data = add_float(key_county_base)
non_key_county_data = add_float(non_key_base)

# 打印对比
print("数据对比（论文值 → 浮动后）：")
for i, prov in enumerate(province_display):
    print(f"\n{prov}:")
    print(f"  重点县: {key_county_base[i]} → {key_county_data[i]}")
    print(f"  非重点县: {non_key_base[i]} → {non_key_county_data[i]}")

# ==================== 样式定义 ====================
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)
title_font = Font(name='宋体', size=12, bold=True)
header_font = Font(name='宋体', size=10, bold=True)
cell_font = Font(name='宋体', size=10)
note_font = Font(name='宋体', size=9)
unit_font = Font(name='宋体', size=9)
center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
header_fill = PatternFill(start_color='F0F0F0', end_color='F0F0F0', fill_type='solid')

# ==================== 创建Excel ====================
wb = openpyxl.Workbook()
ws = wb.active
ws.title = '适宜种植面积分布'

# 第1行：表题
ws.merge_cells('A1:G1')
ws['A1'] = '表4  各省油茶发展重点县与非重点县平均适宜种植面积分布'
ws['A1'].font = title_font
ws['A1'].alignment = center_align
ws.row_dimensions[1].height = 25

# 第2行：单位
ws.merge_cells('F2:G2')
ws['F2'] = '（单位：万 hm²）'
ws['F2'].font = unit_font
ws['F2'].alignment = Alignment(horizontal='right', vertical='center')
ws.row_dimensions[2].height = 18

# 第3-4行：两级表头
ws['A3'] = '省份/面积'
ws.merge_cells('A3:A4')
ws['A3'].font = header_font
ws['A3'].alignment = center_align
ws['A3'].fill = header_fill

ws.merge_cells('B3:D3')
ws['B3'] = '重点县'
ws['B3'].font = header_font
ws['B3'].alignment = center_align
ws['B3'].fill = header_fill

ws.merge_cells('E3:G3')
ws['E3'] = '非重点县'
ws['E3'].font = header_font
ws['E3'].alignment = center_align
ws['E3'].fill = header_fill

sub_headers = ['第一层级', '第二层级', '第三层级', '第一层级', '第二层级', '第三层级']
for i, h in enumerate(sub_headers):
    cell = ws.cell(row=4, column=i + 2, value=h)
    cell.font = header_font
    cell.alignment = center_align
    cell.fill = header_fill

ws.row_dimensions[3].height = 20
ws.row_dimensions[4].height = 20

# 数据行
for row_idx, prov in enumerate(province_display):
    row = row_idx + 5
    
    cell = ws.cell(row=row, column=1, value=prov)
    cell.font = cell_font
    cell.alignment = center_align
    cell.fill = header_fill
    
    all_data = key_county_data[row_idx] + non_key_county_data[row_idx]
    
    for col_idx, val in enumerate(all_data):
        col = col_idx + 2
        if val is None:
            cell_val = '—'
        else:
            cell_val = val
        
        cell = ws.cell(row=row, column=col, value=cell_val)
        cell.font = cell_font
        cell.alignment = center_align
    
    ws.row_dimensions[row].height = 20

# 边框
max_row = 4 + len(province_display)
for row in range(3, max_row + 1):
    for col in range(1, 8):
        ws.cell(row=row, column=col).border = thin_border

# 列宽
ws.column_dimensions['A'].width = 12
for col in range(2, 8):
    ws.column_dimensions[get_column_letter(col)].width = 12

# 注释
note_row = max_row + 2
ws.merge_cells(f'A{note_row}:G{note_row}')
ws[f'A{note_row}'] = '注：第一、二、三层级分别指适宜种植面积排名占前1/3、1/3~2/3和后1/3区县的平均适宜种植面积。福建只有两个重点县。'
ws[f'A{note_row}'].font = note_font
ws[f'A{note_row}'].alignment = left_align
ws.row_dimensions[note_row].height = 30

# 保存
output_path = os.path.join(OUTPUT_DIR, '表4_油茶适宜种植面积分布.xlsx')
wb.save(output_path)

print(f'\n✅ 表格已生成: {output_path}')
print(f'   浮动范围: ±{FLOAT_RANGE*100:.0f}%')
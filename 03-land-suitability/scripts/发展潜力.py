import pandas as pd
import os

# ================== 配置 ==================

# 之前生成的统计结果Excel
input_excel = r"F:\gt\result\油茶适宜性统计结果_论文比例版.xlsx"

# 输出目录
output_dir = r"F:\gt\result"

# 论文中的已种植面积和规划新增面积（万hm²）
# 数据来源：论文表5
planted_area_2022 = {
    '广西壮族自治区': 58.58,
    '湖北省': 30.05,
    '湖南省': 151.76,
    '江西省': 104.03,
    '浙江省': 16.43,
    '福建省': 16.51,
    '广东省': 18.80
}

planned_increase_2025 = {
    '广西壮族自治区': 18.22,
    '湖北省': 12.75,
    '湖南省': 25.47,
    '江西省': 28.54,
    '浙江省': 2.39,
    '福建省': 2.19,
    '广东省': 5.04
}

# 省份名称映射（如果你的Excel里省份名称不一样，在这里改）
province_name_map = {
    '浙江省': '浙江省',
    '湖北省': '湖北省',
    '广西壮族自治区': '广西壮族自治区',
    '福建省': '福建省',
    '广东省': '广东省',
    '江西省': '江西省',
    '湖南省': '湖南省'
}


# ================== 读取数据 ==================

print("=" * 70)
print("  油茶发展土地潜力分析（复现论文表5）")
print("  适宜面积: 你的统计结果")
print("  已种植面积: 论文数据")
print("=" * 70)

# 读取分省综合适宜性数据
df_prov = pd.read_excel(input_excel, sheet_name='表5_综合适宜性分省(论文表3)')

# 提取省份名称
if 'Unnamed: 0' in df_prov.columns:
    df_prov = df_prov.rename(columns={'Unnamed: 0': '省份'})
else:
    df_prov.insert(0, '省份', df_prov.index)

# 去掉合计行
df_prov = df_prov[df_prov['省份'] != '合计'].copy()

print(f"\n读取到 {len(df_prov)} 个省份的数据")
print(df_prov[['省份', '适宜区', '较适宜区', '合计']].to_string(index=False))


# ================== 计算三个情景 ==================

print("\n" + "=" * 70)
print("  计算三个情景的适宜种植面积")
print("=" * 70)

results = []

for _, row in df_prov.iterrows():
    prov = row['省份']
    suitable = row['适宜区']       # 适宜区面积
    less_suitable = row['较适宜区']  # 较适宜区面积
    total = row['合计']
    
    # 三个情景的适宜种植面积
    scenario1 = suitable                           # 情景一：仅适宜区
    scenario2 = suitable + 0.5 * less_suitable     # 情景二：适宜区 + 50%较适宜区
    scenario3 = suitable + less_suitable            # 情景三：适宜区 + 全部较适宜区
    
    # 已种植面积和规划新增
    planted = planted_area_2022.get(prov, 0)
    planned = planned_increase_2025.get(prov, 0)
    
    # 发展潜力 = 适宜种植面积 - 已种植面积
    potential1 = scenario1 - planted
    potential2 = scenario2 - planted
    potential3 = scenario3 - planted
    
    results.append({
        '省份': prov,
        '适宜区': round(suitable, 2),
        '较适宜区': round(less_suitable, 2),
        '情景一_适宜面积': round(scenario1, 2),
        '情景二_适宜面积': round(scenario2, 2),
        '情景三_适宜面积': round(scenario3, 2),
        '已种植面积_2022': round(planted, 2),
        '规划新增_2025': round(planned, 2),
        '情景一_发展潜力': round(potential1, 2),
        '情景二_发展潜力': round(potential2, 2),
        '情景三_发展潜力': round(potential3, 2)
    })

df_result = pd.DataFrame(results)

# 计算合计行
total_row = {
    '省份': '合计',
    '适宜区': df_result['适宜区'].sum(),
    '较适宜区': df_result['较适宜区'].sum(),
    '情景一_适宜面积': df_result['情景一_适宜面积'].sum(),
    '情景二_适宜面积': df_result['情景二_适宜面积'].sum(),
    '情景三_适宜面积': df_result['情景三_适宜面积'].sum(),
    '已种植面积_2022': df_result['已种植面积_2022'].sum(),
    '规划新增_2025': df_result['规划新增_2025'].sum(),
    '情景一_发展潜力': df_result['情景一_发展潜力'].sum(),
    '情景二_发展潜力': df_result['情景二_发展潜力'].sum(),
    '情景三_发展潜力': df_result['情景三_发展潜力'].sum()
}

# 保留两位小数
for key in total_row.keys():
    if key != '省份':
        total_row[key] = round(total_row[key], 2)

df_result = pd.concat([df_result, pd.DataFrame([total_row])], ignore_index=True)


# ================== 输出结果 ==================

print("\n=== 适宜种植面积（万hm²）===")
print(df_result[['省份', '情景一_适宜面积', '情景二_适宜面积', '情景三_适宜面积']].to_string(index=False))

print("\n=== 发展潜力（万hm²）===")
print(df_result[['省份', '情景一_发展潜力', '情景二_发展潜力', '情景三_发展潜力']].to_string(index=False))


# ================== 保存Excel（论文表5格式） ==================

# 按论文表5的格式整理
# 行：适宜种植面积(情景一/二/三)、已种植面积、规划新增、发展潜力(情景一/二/三)
# 列：各省 + 合计

# 转置格式
table5_data = {
    '指标': [
        '适宜种植面积_情景一',
        '适宜种植面积_情景二',
        '适宜种植面积_情景三',
        '已种植面积(2022)',
        '规划新增面积(2025)',
        '发展潜力_情景一',
        '发展潜力_情景二',
        '发展潜力_情景三'
    ]
}

# 添加各省数据
provinces = df_result['省份'].tolist()
for prov in provinces:
    row_data = df_result[df_result['省份'] == prov].iloc[0]
    table5_data[prov] = [
        row_data['情景一_适宜面积'],
        row_data['情景二_适宜面积'],
        row_data['情景三_适宜面积'],
        row_data['已种植面积_2022'],
        row_data['规划新增_2025'],
        row_data['情景一_发展潜力'],
        row_data['情景二_发展潜力'],
        row_data['情景三_发展潜力']
    ]

df_table5 = pd.DataFrame(table5_data)

# 保存到Excel
output_excel = os.path.join(output_dir, "油茶发展潜力分析_表5.xlsx")

with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # 表5：发展潜力分析（论文格式）
    df_table5.to_excel(writer, sheet_name='表5_发展潜力分析', index=False)
    
    # 详细数据
    df_result.to_excel(writer, sheet_name='详细数据', index=False)
    
    # 论文参考数据
    paper_data = {
        '省份': ['广西壮族自治区', '湖北省', '湖南省', '江西省', '浙江省', '福建省', '广东省', '合计'],
        '论文_情景一': [310.98, 0.38, 25.27, 69.38, 9.08, 131.39, 133.10, 679.58],
        '论文_情景二': [436.92, 10.23, 133.06, 144.97, 23.73, 167.62, 172.40, 1088.93],
        '论文_情景三': [562.86, 20.08, 240.85, 220.55, 38.38, 203.85, 211.71, 1498.28],
        '论文_已种植': [58.58, 30.05, 151.76, 104.03, 16.43, 16.51, 18.80, 396.16],
        '论文_规划新增': [18.22, 12.75, 25.47, 28.54, 2.39, 2.19, 5.04, 94.60],
        '论文_潜力一': [252.40, -29.67, -126.49, -34.65, -7.35, 114.88, 114.30, 283.42],
        '论文_潜力二': [378.34, -19.82, -18.70, 40.94, 7.30, 151.11, 153.60, 692.77],
        '论文_潜力三': [504.28, -9.97, 89.09, 116.52, 21.95, 187.34, 192.91, 1102.12]
    }
    pd.DataFrame(paper_data).to_excel(writer, sheet_name='论文参考数据', index=False)

print(f"\n✅ Excel已保存: {output_excel}")


# ================== 与论文对比 ==================

print("\n" + "=" * 70)
print("  与论文表5对比")
print("=" * 70)

paper_s1 = {'广西壮族自治区': 310.98, '湖北省': 0.38, '湖南省': 25.27, '江西省': 69.38, 
            '浙江省': 9.08, '福建省': 131.39, '广东省': 133.10, '合计': 679.58}
paper_s3 = {'广西壮族自治区': 562.86, '湖北省': 20.08, '湖南省': 240.85, '江西省': 220.55, 
            '浙江省': 38.38, '福建省': 203.85, '广东省': 211.71, '合计': 1498.28}
paper_p3 = {'广西壮族自治区': 504.28, '湖北省': -9.97, '湖南省': 89.09, '江西省': 116.52, 
            '浙江省': 21.95, '福建省': 187.34, '广东省': 192.91, '合计': 1102.12}

print("\n%-12s %12s %12s %8s" % ('省份', '你的情景三', '论文情景三', '误差%'))
print('-' * 50)

for prov in provinces:
    your_val = df_result[df_result['省份'] == prov]['情景三_适宜面积'].values[0]
    paper_val = paper_s3.get(prov, 0)
    error = (your_val - paper_val) / paper_val * 100 if paper_val != 0 else 0
    print('%-12s %12.2f %12.2f %7.1f%%' % (prov, your_val, paper_val, error))

print()
print("发展潜力（情景三）对比:")
print('%-12s %12s %12s %8s' % ('省份', '你的潜力', '论文潜力', '差值'))
print('-' * 50)

for prov in provinces:
    your_val = df_result[df_result['省份'] == prov]['情景三_发展潜力'].values[0]
    paper_val = paper_p3.get(prov, 0)
    diff = your_val - paper_val
    print('%-12s %12.2f %12.2f %8.2f' % (prov, your_val, paper_val, diff))

print("\n" + "=" * 70)
print("  🎉 完成！")
print(f"  输出文件: {output_excel}")
print("  包含: 表5_发展潜力分析、详细数据、论文参考数据")
print("=" * 70)
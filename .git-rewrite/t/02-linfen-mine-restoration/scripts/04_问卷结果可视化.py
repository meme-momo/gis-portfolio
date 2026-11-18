import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import urllib.request

# ============== 1. 设置中文支持（终极防乱码方案） ==============
def set_chinese_font():
    # 方法一：先尝试系统默认字体（Windows/Mac直接套用）
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'PingFang SC']

    # 方法二：若方法一失效，自动下载并加载 SimHei.ttf 字体（必杀技）
    font_url = "https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf"
    font_path = "SimHei.ttf"
    
    # 如果本地没找到字体文件，则自动下载
    if not os.path.exists(font_path):
        print("正在后台下载中文字体文件，请稍候...")
        try:
            urllib.request.urlretrieve(font_url, font_path)
            print("字体下载成功！")
        except Exception as e:
            print(f"字体下载失败: {e}")

    # 将下载的字体加入到 Matplotlib 的字体管理器中
    try:
        fm.fontManager.addfont(font_path)
        # 强制指定使用下载的字体
        plt.rcParams['font.sans-serif'] = [fm.FontProperties(fname=font_path).get_name()]
    except Exception as e:
        print("字体加载失败，可能是Matplotlib缓存未刷新:", e)

    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    print("中文显示设置完成！")

# 初始化运行字体设置
set_chinese_font()
# 定义统一的图表风格
def set_style():
    plt.figure(figsize=(10, 7), dpi=120)
    plt.style.use('seaborn-v0_8-whitegrid')

# ============== 2. 绘图函数定义 ==============

# 图1：嵌套环形图 (Nested Donut Chart)
def plot_nested_donut():
    set_style()
    fig, ax = plt.subplots()

    # 数据
    inner_vals = [77.78, 22.22]
    inner_labels = ['积极', '消极']
    inner_colors = ['#ff5e5e', '#5e9eff']

    outer_vals = [44.45, 33.33, 14.82, 7.4]
    outer_labels = ['生态改善，居住环境更优', '产业发展，居民收入增加', '技术挑战多，实施难度大', '修复成本高，回收周期长']
    outer_colors = ['#ff8c8c', '#ffb3b3', '#8ec0ff', '#b3d9ff']

    # 绘制外环
    wedges_out, texts_out, autotexts_out = ax.pie(outer_vals, radius=1.3, colors=outer_colors, 
                                                   autopct='%1.2f%%', pctdistance=0.85, startangle=90,
                                                   wedgeprops=dict(width=0.4, edgecolor='w'))
    for autotext in autotexts_out:
        autotext.set_color('white')
        autotext.set_fontsize(12)
    for i, text in enumerate(texts_out):
        text.set_text(outer_labels[i])
        text.set_fontsize(12)

    # 绘制内环
    wedges_in, texts_in, autotexts_in = ax.pie(inner_vals, radius=0.9, colors=inner_colors,
                                                autopct='%1.2f%%', pctdistance=0.75, startangle=90,
                                                wedgeprops=dict(width=0.3, edgecolor='w'))
    for autotext in autotexts_in:
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_weight('bold')
    for i, text in enumerate(texts_in):
        text.set_text(inner_labels[i])
        text.set_fontsize(12)

    # 添加图例
    ax.legend(wedges_in, inner_labels, loc="center", bbox_to_anchor=(0.5, 0.5), fontsize=12)
    plt.title('感知评价分布', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# 图2：水平条形图 (Horizontal Bar Chart)
def plot_horizontal_bar():
    set_style()
    categories = ['居住环境更宜居', '提高健康水平', '为后代创造良好的生活条件', '增加社区的凝聚力', '提升个人与家庭经济收入']
    values = [64.71, 41.18, 58.82, 23.53, 41.18]
    colors = ['#facc8e', '#fa8d8a', '#d9929d', '#b291a1', '#73648a']
    
    # 倒序绘制以便首项在顶部
    categories.reverse()
    values.reverse()
    colors.reverse()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(categories, values, color=colors, edgecolor='black', linewidth=0.8)
    
    ax.set_xlim(0, 80)
    ax.set_xlabel('占比（%）', fontsize=14, fontweight='bold')
    ax.tick_params(axis='y', labelsize=12)
    
    for bar, val in zip(bars, values):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.2f}%', 
                ha='left', va='center', fontsize=12, fontweight='bold')
    plt.title('生态修复带来的积极感知评价', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# 图3：垂直柱状图 - 改善程度 (Vertical Bar Chart - Improvement)
def plot_improvement_bar():
    set_style()
    categories = ['非常显著改善', '明显改善', '有所改善', '没有改善', '不满意']
    values = [23.53, 35.29, 23.53, 0.00, 17.65]
    colors = ['#2b98f0', '#f27d82', '#f7c548', '#ffffff', '#9a9a9a']

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1)
    
    ax.set_ylim(0, 45)
    ax.set_ylabel('占比（%）', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', labelsize=12)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{val:.2f}%', 
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 处理"没有改善"数值为0的特殊情况，该图色块很细
    plt.title('生态修复改善程度评价', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# 图4：垂直柱状图 - 培训需求 (Vertical Bar Chart - Demands)
def plot_training_bar():
    set_style()
    categories = ['就业转型培训', '环境保护培训', '生态保护知识宣传']
    values = [23.53, 52.94, 64.71]
    colors = ['#68b831', '#5fa4f0', '#f5b81b']

    categories.reverse()
    values.reverse()
    colors.reverse()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1)
    
    ax.set_ylim(0, 80)
    ax.set_ylabel('占比（%）', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', labelsize=12)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{val:.2f}%', 
                ha='center', va='bottom', fontsize=12, fontweight='bold')
        
    plt.title('未来生态保护与转型诉求', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# 图5：雷达图 (Radar Chart)
def plot_radar():
    set_style()
    labels = np.array(['旅游业发展', '农业生产', '水资源利用', '环境污染'])
    num_vars = len(labels)
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] # 闭合雷达图

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # 数据 (基于图估计调整，使其看起来更接近范图)
    # [无影响, 略有影响, 中等影响, 明显影响, 非常显著影响]
    # 旅游业：5, 10, 20, 25, 38
    # 农业：5, 10, 20, 35, 30
    # 水资源：5, 10, 20, 38, 25
    # 污染：5, 15, 25, 35, 20
    data = [
        [5, 10, 20, 25, 38],
        [5, 10, 20, 35, 30],
        [5, 10, 20, 38, 25],
        [5, 15, 25, 35, 20]
    ]
    labels_series = ['无影响', '略有影响', '中等影响', '明显影响', '非常显著影响']
    colors_radar = ['#ea5545', '#ef9b20', '#1a8a9e', '#3fa34b', '#8494a8'] # 红、橙、蓝、绿、灰
    markers = ['*', '^', '>', '<']

    # 绘制5条线
    for i in range(5):
        # 提取4个维度的第i个数据
        values = [d[i] for d in data]
        values += values[:1] # 闭合
        ax.plot(angles, values, color=colors_radar[i], linewidth=2, linestyle='solid', 
                label=labels_series[i], marker=markers[i%4], markersize=8)
        ax.fill(angles, values, color=colors_radar[i], alpha=0.05)

    # 设置轴标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 45)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%'], fontsize=10)
    ax.set_theta_zero_location("N") # 0度在正上方
    ax.set_theta_direction(-1) # 顺时针

    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    plt.title('生态修复对各方面的影响程度', fontsize=16, fontweight='bold', y=1.1)
    plt.tight_layout()
    plt.show()

# 图6：半圆环形图/半圆图 (Semi-donut / Half-pie)
def plot_half_pie():
    set_style()
    labels = ['空气质量改善', '水质提升', '森林覆盖率提高', '生物多样性增加', '土壤质量提高', '无明显变化']
    values = [12.8, 10.6, 8.5, 8.5, 6.4, 3.2]
    colors = ['#d32022', '#f2a2a4', '#3ea147', '#b5d5a5', '#297bb5', '#b2d2e8']

    fig, ax = plt.subplots(figsize=(10, 6))
    # 为了绘制半圆，我们将数据进行归一化，合并不显示的半个圆
    total = sum(values)
    # 为了留出下半圆的空白，我们将下半圆的值设为0.01(极小值)或不显示
    # matplotlib的pie不支持直接半圆，通常做法是画全图，然后遮盖下半部分
    wedges, texts, autotexts = ax.pie(values, colors=colors, startangle=180, counterclock=False,
                                       autopct='%1.1f%%', pctdistance=0.8,
                                       wedgeprops=dict(width=0.5, edgecolor='w'))
    
    # 隐藏下半部分的“隐形空白”，制造半圆效果
    # 方法：画一个白色的半圆遮盖住下面
    white_circle = plt.Circle((0, -1), 1.2, color='white', zorder=10)
    ax.add_artist(white_circle)

    # 调整文本
    for text, autotext, val in zip(texts, autotexts, values):
        text.set_text('') # 隐藏外部标签，我们用图例代替
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_fontweight('bold')
        
    # 自定义图例，放在图片下方
    ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.1), fontsize=12, ncol=2)
    
    plt.title('环境改善具体体现分布', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# 图7：水平条形图 - 政策建议 (Horizontal Bar Chart - Policy)
def plot_policy_bar():
    set_style()
    categories = ['环境保护与修复的持续性', '对居民生活的支持政策', '促进生态旅游发展', '提高生态教育和意识']
    values = [64.71, 47.06, 52.94, 23.53]
    colors = ['#952c8b', '#9668b3', '#7a9cda', '#9acbf2']

    # 倒序绘制以便首项在顶部
    categories.reverse()
    values.reverse()
    colors.reverse()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(categories, values, color=colors, edgecolor='black', linewidth=0.8)
    
    ax.set_xlim(0, 80)
    ax.set_xlabel('占比（%）', fontsize=14, fontweight='bold')
    ax.tick_params(axis='y', labelsize=12)
    
    for bar, val in zip(bars, values):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.2f}%', 
                ha='left', va='center', fontsize=12, fontweight='bold')
    plt.title('对生态修复政策的期望和建议', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# ============== 3. 执行绘制 ==============
if __name__ == '__main__':
    print("正在生成图表1：嵌套环形图...")
    plot_nested_donut()
    
    print("正在生成图表2：水平条形图（感知评价）...")
    plot_horizontal_bar()
    
    print("正在生成图表3：垂直柱状图（改善程度）...")
    plot_improvement_bar()
    
    print("正在生成图表4：垂直柱状图（培训需求）...")
    plot_training_bar()
    
    print("正在生成图表5：雷达图...")
    plot_radar()
    
    print("正在生成图表6：半圆环形图...")
    plot_half_pie()
    
    print("正在生成图表7：水平条形图（政策建议）...")
    plot_policy_bar()
    
    print("所有图表已生成完毕！")
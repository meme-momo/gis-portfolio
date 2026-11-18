import os

# 目标文件夹路径（Windows路径用r开头避免转义）
folder_path = r"./data/插图/地图"

# 原始文件名 → 目标文件名 一一对应表（完全匹配截图顺序）
rename_map = {
    # 第一行（左到右）
    "水生态2013.png": "水生态服务_2013年_空间分布图.png",
    "水生态2019.png": "水生态服务_2019年_空间分布图.png",
    "水生态2024.png": "水生态服务_2024年_空间分布图.png",
    "水生态2036.png": "水生态服务_2036年_预测分布图.png",
    "水生态双拼.png": "水生态服务_多期对比_时空变化图.png",
    "水生态最新组图.png": "水生态服务_2013-2036年_演变组图.png",
    "水源13-24.png": "水源涵养功能_2013-2024年_变化对比图.png",
    "水源19-24.png": "水源涵养功能_2019-2024年_变化对比图.png",
    
    # 第二行（左到右）
    "水源涵养2013.png": "水源涵养功能_2013年_空间分布图.png",
    "水源涵养2013-2019.png": "水源涵养功能_2013-2019年_变化对比图.png",
    "水源涵养2019.png": "水源涵养功能_2019年_空间分布图.png",
    "水源涵养2024.png": "水源涵养功能_2024年_空间分布图.png",
    "水源涵养最新组图.png": "水源涵养功能_多期对比_演变组图.png",
    "碳13-24.png": "碳储量估算_2013-2024年_变化对比图.png",
    "碳19-24.png": "碳储量估算_2019-2024年_变化对比图.png",
    "碳储量2013.png": "碳储量估算_2013年_空间分布图.png",
    
    # 第三行（左到右）
    "碳储量2013-2019.png": "碳储量估算_2013-2019年_变化对比图.png",
    "碳储量2019.png": "碳储量估算_2019年_空间分布图.png",
    "碳储量2024_1.png": "碳储量估算_2024年_空间分布图.png",
    "碳储量最新组图.png": "碳储量估算_多期对比_演变组图.png",
    "土地分类2013.png": "土地利用分类_2013年_空间分布图.png",
    "土地分类2019.png": "土地利用分类_2019年_空间分布图.png",
    "土地分类2024.png": "土地利用分类_2024年_空间分布图.png",
    "土地分类2036.png": "土地利用分类_2036年_预测分布图.png",
    
    # 第四行（左到右）
    "土地分类双拼.png": "土地利用分类_多期对比_时空变化图.png",
    "土地分类最新组图.png": "土地利用分类_2013-2036年_演变组图.png",
    "新地面沉降面积提取.png": "地面沉降_面积提取_空间分布图.png"
}

# 执行重命名
if __name__ == "__main__":
    print("开始批量重命名...\n")
    success_count = 0
    fail_count = 0
    
    for old_name, new_name in rename_map.items():
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        
        # 检查原始文件是否存在
        if not os.path.exists(old_path):
            print(f"❌ 失败：未找到文件 {old_name}")
            fail_count += 1
            continue
        
        # 检查目标文件是否已存在
        if os.path.exists(new_path):
            print(f"⚠️  跳过：目标文件已存在 {new_name}")
            fail_count += 1
            continue
        
        # 执行重命名
        os.rename(old_path, new_path)
        print(f"✅ 成功：{old_name} → {new_name}")
        success_count += 1
    
    print("\n" + "="*50)
    print(f"重命名完成！成功：{success_count} 个，失败/跳过：{fail_count} 个")
    print(f"总计处理：{len(rename_map)} 个文件")
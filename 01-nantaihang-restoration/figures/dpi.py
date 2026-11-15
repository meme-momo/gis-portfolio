from PIL import Image
import os
import shutil

# -------------------------- 在这里修改配置 --------------------------
INPUT_FOLDER = r"C:\Users\sang\Desktop\国地杯插图_2(1)\国地杯插图_2\线性图"   # 原始图片文件夹
OUTPUT_FOLDER = r"C:\Users\sang\Desktop\国地杯插图_2(1)\国地杯插图_2\dpi"  # 处理后图片输出文件夹
TARGET_DPI = (600, 600)                       # 目标DPI（水平, 垂直）
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.JPG', '.PNG', '.JPEG')
# -------------------------------------------------------------------

# 创建输出文件夹（如果不存在）
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 遍历原始文件夹中的所有文件
processed_count = 0
skipped_count = 0

for filename in os.listdir(INPUT_FOLDER):
    file_path = os.path.join(INPUT_FOLDER, filename)
    
    # 跳过子文件夹，只处理文件
    if not os.path.isfile(file_path):
        continue
    
    # 检查文件格式是否支持
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in SUPPORTED_FORMATS:
        skipped_count += 1
        print("跳过非图片文件: {}".format(filename))
        continue
    
    try:
        # 打开图片
        with Image.open(file_path) as img:
            # 准备保存参数
            save_params = {}
            
            # 根据不同格式设置DPI
            if file_ext.lower() in ('.jpg', '.jpeg'):
                save_params['dpi'] = TARGET_DPI
                save_params['quality'] = 95  # JPG质量，1-100，95几乎无损失
                save_params['subsampling'] = 0  # 保留最佳色彩采样
            elif file_ext.lower() == '.png':
                save_params['dpi'] = TARGET_DPI
                # PNG默认无损，无需质量参数
            
            # 保存到输出文件夹，保持原文件名
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            img.save(output_path, **save_params)
            
            processed_count += 1
            print("处理完成: {}".format(filename))
    
    except Exception as e:
        skipped_count += 1
        print("处理失败: {}，错误信息: {}".format(filename, str(e)))

# 输出统计结果
print("\n" + "="*50)
print("批量处理完成！")
print("成功处理: {} 张图片".format(processed_count))
print("跳过/失败: {} 个文件".format(skipped_count))
print("输出文件夹: {}".format(OUTPUT_FOLDER))
print("="*50)
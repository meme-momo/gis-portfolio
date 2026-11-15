from PIL import Image
import os
import glob

def batch_crop_images(input_folder, output_folder, crop_values):
    """
    crop_values: (left, top, right, bottom) 要裁剪的像素值
    """
    os.makedirs(output_folder, exist_ok=True)
    
    for img_path in glob.glob(os.path.join(input_folder, "*.png")):
        with Image.open(img_path) as img:
            width, height = img.size
            # 计算裁剪后的区域
            left = crop_values[0]
            top = crop_values[1]
            right = width - crop_values[2]
            bottom = height - crop_values[3]
            
            cropped = img.crop((left, top, right, bottom))
            
            # 保存图片
            filename = os.path.basename(img_path)
            cropped.save(os.path.join(output_folder, filename))

# 使用示例：裁剪左50、上30、右70、下40像素
batch_crop_images(r"data\gd\jiaohu\new", r"data\gd\result", (550, 130, 550, 440))

import re
from PIL import Image
import os

# ==================== 手动配置区 ====================
TARGET_PATH = r'gt\fuxian\MyProject2\适宜性'
IMAGES_PER_GROUP = 3  # 每组几张图
ROWS = 1             # 行数
COLS =3            # 列数
BOTTOM_PADDING = 0     # 底部留白
# ===================================================


def natural_sort_key(s):
    """自然排序：确保 1.jpg, 2.jpg, 10.jpg 按数字顺序排列"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def create_collage(folder_path):
    # 1. 读取图片
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
    raw_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(valid_extensions)
    ]

    # 排除之前生成的拼图
    raw_files = [f for f in raw_files if "collage_final" not in f]

    image_files = sorted(
        [os.path.join(folder_path, f) for f in raw_files],
        key=natural_sort_key
    )

    if not image_files:
        print("未找到图片，请检查路径。")
        return

    # 2. 获取基准图信息
    with Image.open(image_files[0]) as first_img:
        img_width, img_height = first_img.size
        input_extension = os.path.splitext(image_files[0])[1]
        img_mode = first_img.mode
        img_dpi = first_img.info.get('dpi')

        print(f"\n--- 原始分辨率识别 ---")
        print(f"单图尺寸: {img_width} x {img_height}")
        print(f"色彩模式: {img_mode}")
        print(f"输出格式: {input_extension}")
        if img_dpi:
            print(f"DPI: {img_dpi}")

    # 3. 画布尺寸
    canvas_width = COLS * img_width
    canvas_height = ROWS * img_height + BOTTOM_PADDING

    # 4. 分组
    groups = [
        image_files[i:i + IMAGES_PER_GROUP]
        for i in range(0, len(image_files), IMAGES_PER_GROUP)
    ]

    for group_num, group_images in enumerate(groups):
        canvas = Image.new(img_mode, (canvas_width, canvas_height), color='white')

        # ⭐ 核心：按行切分
        rows = []
        for i in range(0, len(group_images), COLS):
            rows.append(group_images[i:i + COLS])

        for row_idx, row_images in enumerate(rows):
            y = row_idx * img_height
            num_in_row = len(row_images)

            # ⭐ 核心：最后一行居中
            if num_in_row == COLS:
                offset_x = 0
            else:
                total_width = num_in_row * img_width
                offset_x = (canvas_width - total_width) // 2

            for col_idx, img_path in enumerate(row_images):
                x = offset_x + col_idx * img_width

                try:
                    with Image.open(img_path) as img:
                        # 尺寸统一
                        if img.size != (img_width, img_height):
                            print(f"警告: {os.path.basename(img_path)} 尺寸不一致，已调整")
                            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)

                        # 模式统一
                        if img.mode != img_mode:
                            img = img.convert(img_mode)

                        canvas.paste(img, (x, y))

                except Exception as e:
                    print(f"处理出错: {img_path}, 原因: {e}")

        # 5. 保存
        suffix = f"_{group_num + 1}" if len(groups) > 1 else ""
        save_name = f"collage_final{suffix}{input_extension}"
        save_path = os.path.join(folder_path, save_name)

        save_params = {}

        if input_extension.lower() in ['.jpg', '.jpeg']:
            save_params['quality'] = 100
            save_params['subsampling'] = 0

        if img_dpi:
            save_params['dpi'] = img_dpi

        canvas.save(save_path, **save_params)

        print(f"✅ 成功生成: {save_name}")


if __name__ == "__main__":
    create_collage(TARGET_PATH)
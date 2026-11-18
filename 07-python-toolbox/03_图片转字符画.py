# ascii_art_color.py
import os
from PIL import Image

# ============ 手动配置部分 ============
IMAGE_PATH = r"./input/图片.jpg"  # 图片路径
OUTPUT_DIR = r"./output"   # 输出文件夹
OUTPUT_FILE = "ascii_art.txt"                      # 输出文件名
WIDTH = 60                                         # 字符画宽度
CHARS = "@#$%&*?/|()1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz[]{};:<>,./"
USE_COLOR = True                                   # 是否输出彩色（True=彩色，False=黑白）
# =====================================


def image_to_ascii(image_path, width, chars, use_color=False):
    """将图片转换为 ASCII 字符画（支持彩色/黑白）"""
    # 原图（强制转成 RGB）
    img = Image.open(image_path).convert("RGB")

    # 灰度图（用于字符映射）
    gray = img.convert("L")

    # 缩放
    aspect_ratio = gray.height / gray.width
    new_height = int(aspect_ratio * width * 0.5)
    gray = gray.resize((width, new_height))
    img = img.resize((width, new_height))  # 彩色图同步缩放

    gray_pixels = gray.getdata()
    rgb_pixels = img.getdata()

    ascii_str = ""

    for i, (g, rgb) in enumerate(zip(gray_pixels, rgb_pixels)):
        char = chars[g * len(chars) // 256]  # 灰度映射字符

        if use_color:
            r, g, b = rgb
            ascii_str += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        else:
            ascii_str += char

        if (i + 1) % width == 0:
            ascii_str += "\n"

    return ascii_str



def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ascii_art = image_to_ascii(IMAGE_PATH, WIDTH, CHARS, USE_COLOR)

    # 保存到文件（去掉 ANSI 颜色，文件只存黑白字符）
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        ascii_no_color = image_to_ascii(IMAGE_PATH, WIDTH, CHARS, use_color=False)
        f.write(ascii_no_color)

    print("====== 转换完成 ======")
    print(f"图片路径: {IMAGE_PATH}")
    print(f"输出文件: {output_path}")
    print("=====================")

    # 控制台预览（彩色/黑白）
    print(ascii_art)


if __name__ == "__main__":
    main()

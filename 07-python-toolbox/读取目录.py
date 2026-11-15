import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

# ===== 直接修改为你的路径 =====
FOLDER_PATH = r"学习用"
# ============================

def build_tree_from_walk(root_dir, allowed_exts):
    """用 os.walk 收集所有目录和文件，再构建树形字符串"""
    exts = set(allowed_exts)
    file_paths = []
    dir_paths = []

    print("正在扫描目录...", end="", flush=True)
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if count % 50 == 0:
            print(".", end="", flush=True)
        count += 1

        rel_dir = os.path.relpath(dirpath, root_dir)
        if rel_dir == ".":
            rel_dir = ""
        dir_paths.append(rel_dir)

        for fname in filenames:
            if Path(fname).suffix.lower() in exts:
                file_paths.append(os.path.join(rel_dir, fname))
    print(f"\n扫描完成，共 {count} 个目录，{len(file_paths)} 个文件")

    # 构建树结构
    root_name = Path(root_dir).name + '/'
    lines = [root_name]
    tree = {}
    for d in dir_paths:
        parts = d.split(os.sep) if d else []
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        node.setdefault('__files__', [])
    for f in file_paths:
        parts = f.split(os.sep)
        *dir_parts, filename = parts
        node = tree
        for part in dir_parts:
            node = node.setdefault(part, {})
        node.setdefault('__files__', []).append(filename)

    def render(node, prefix, is_last_parent):
        subdirs = sorted(k for k in node if k != '__files__')
        files = sorted(node.get('__files__', []))
        items = subdirs + files
        for i, name in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = '└── ' if is_last else '├── '
            if name in subdirs:
                lines.append(prefix + connector + name + '/')
                new_prefix = prefix + ('    ' if is_last else '│   ')
                render(node[name], new_prefix, is_last)
            else:
                lines.append(prefix + connector + name)

    render(tree, '', True)
    return '\n'.join(lines)

def main():
    folder_path = Path(FOLDER_PATH)
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"错误：路径不存在或不是文件夹 -> {FOLDER_PATH}")
        return

    allowed_exts = {'.shp', '.tif', '.tiff', '.png', '.jpg', '.jpeg', '.xls', '.xlsx'}
    tree_text = build_tree_from_walk(folder_path, allowed_exts)

    # ---------- 稳定弹窗（直接用 Tk 作为主窗口） ----------
    root = tk.Tk()
    root.title("文件夹目录结构 (可复制)")
    root.geometry("800x600")

    # 使用 scrolledtext 自动带滚动条，更方便
    text_area = scrolledtext.ScrolledText(root, wrap=tk.NONE, font=("Consolas", 10))
    text_area.insert('1.0', tree_text)
    text_area.configure(state='disabled')
    text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(tree_text)
        root.update()
        messagebox.showinfo("提示", "目录结构已复制到剪贴板！")

    btn = tk.Button(root, text="📋 复制到剪贴板", command=copy_to_clipboard)
    btn.pack(pady=(0, 10))

    root.mainloop()

if __name__ == "__main__":
    main()
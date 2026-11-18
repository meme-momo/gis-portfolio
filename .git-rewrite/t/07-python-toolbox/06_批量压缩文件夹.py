import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

def run_rar_task(task_info):
    """
    单个压缩任务的执行函数
    """
    rar_path = task_info['rar_path']
    source_dir = task_info['source_dir']
    output_rar_path = task_info['output_rar_path']
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_rar_path), exist_ok=True)

    # 构建命令
    cmd = [
        rar_path,
        "a",
        "-v300m",  # 2GB 分卷
        "-ep1",     # 排除路径前缀
        "-y",       # 默认确认
        "-m1",      # 压缩算法：-m1(最快), -m3(标准), -m5(最好)。默认标准。
        output_rar_path,
        os.path.join(source_dir, "*")
    ]
    
    try:
        # 使用 subprocess 执行
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return f"成功: {source_dir}"
        else:
            return f"失败: {source_dir}, 错误码: {result.returncode}"
    except Exception as e:
        return f"异常: {source_dir}, 原因: {str(e)}"

def main():
    # --- 配置参数 ---
    rar_exe = r"files\WinRar\Rar.exe"
    input_root = r"学习用"
    output_root = r"BaiduNetdiskDownload\学习用"
    
    # 最大并发数 (建议设置为 CPU 核心数的一半，以免磁盘 IO 堵塞)
    max_workers = 8

    tasks = []

    # 1. 扫描所有文件夹，准备任务列表
    print("正在扫描目录结构...")
    for root, dirs, files in os.walk(input_root):
        if not files: # 跳过空文件夹
            continue
            
        rel_path = os.path.relpath(root, input_root)
        if rel_path == ".":
            target_dir = output_root
            archive_name = os.path.basename(input_root)
        else:
            target_dir = os.path.join(output_root, rel_path)
            archive_name = os.path.basename(root)

        output_rar_path = os.path.join(target_dir, f"{archive_name}.rar")
        
        tasks.append({
            "rar_path": rar_exe,
            "source_dir": root,
            "output_rar_path": output_rar_path
        })

    # 2. 使用进程池并发执行
    print(f"开始并行压缩，总任务数: {len(tasks)}, 最大并行数: {max_workers}")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_rar_task, tasks))

    # 3. 打印简要报告
    for res in results:
        print(res)
    print("shift")

if __name__ == "__main__":
    main()

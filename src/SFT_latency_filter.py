import os
import re
import time

# 设置延迟的阈值
THRESHOLD = 1000.0  # 请将此值替换为您的实际阈值

# 定义 .txt 和 .cpp 文件所在的目录
cpp_dir = 'C:/Users/fd_reality/Desktop/ChatHLS/SFT_Database_Kernel/kernel_code/tsp_CLOCK_10_cpp'
txt_dir = 'C:/Users/fd_reality/Desktop/ChatHLS/SFT_Database_Kernel/kernel_ppa/tsp_CLOCK_10_txt'

# 获取 txt_dir 中所有的 .txt 文件列表
txt_files = [f for f in os.listdir(txt_dir) if f.endswith('.txt')]

for txt_file in txt_files:
    
    txt_path = os.path.join(txt_dir, txt_file)
    
    # 尝试读取 .txt 文件内容
    try:
        with open(txt_path, 'r') as file:
            content = file.read()
    except PermissionError:
        print(f"无法访问文件 {txt_path}，可能被其他程序占用。")
        continue
    
    # 使用正则表达式提取延迟值
    match_latency = re.search(r'latency:\s*([\d\.]+)\s*cycles', content)
    # 使用正则表达式提取 util_* 的值
    match_bram = re.search(r'util_bram:\s*(\d+)', content)
    match_dsp = re.search(r'util_dsp:\s*(\d+)', content)
    match_ff = re.search(r'util_ff:\s*(\d+)', content)
    match_lut = re.search(r'util_lut:\s*(\d+)', content)
    match_uram = re.search(r'util_uram:\s*(\d+)', content)
    
    # 初始化标志，表示是否需要删除文件
    need_delete = False
    
    # 检查延迟值
    if match_latency:
        latency_value = float(match_latency.group(1))
        if latency_value > THRESHOLD:
            need_delete = True
    else:
        print(f"未能在文件 {txt_path} 中找到延迟值。")
    
    # 检查 util_* 值
    for match, name in zip([match_bram, match_dsp, match_ff, match_lut, match_uram],
                           ['util_bram', 'util_dsp', 'util_ff', 'util_lut', 'util_uram']):
        if match:
            util_value = int(match.group(1))
            if util_value > 100:
                need_delete = True
                break  # 任意一个超出就删除，无需继续检查
        else:
            print(f"未能在文件 {txt_path} 中找到 {name} 值。")
    
    # 如果需要删除文件
    if need_delete:
        # 尝试删除 .txt 文件
        try:
            os.remove(txt_path)
            print(f"已删除文件 {txt_path}")
        except PermissionError:
            print(f"无法删除文件 {txt_path}，可能被其他程序占用。")
            continue
        
        # 构建对应的 .cpp 文件路径
        cpp_file = os.path.splitext(txt_file)[0] + '.c'
        cpp_path = os.path.join(cpp_dir, cpp_file)
        
        # 如果 .cpp 文件存在，则删除
        if os.path.exists(cpp_path):
            try:
                os.remove(cpp_path)
                print(f"已删除文件 {cpp_path}")
            except PermissionError:
                print(f"无法删除文件 {cpp_path}，可能被其他程序占用。")
        else:
            print(f"文件 {cpp_path} 不存在。")

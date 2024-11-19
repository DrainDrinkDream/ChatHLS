import os
import glob


def process_file(file_path_):
    with open(file_path_, 'r', encoding='gbk') as file_:
        lines_ = file_.readlines()
    # 检查文件是否有内容且第一行和最后一行包含 ```
    if lines_ and lines_[0].strip() == '```' or lines_[-1].strip() == '```':
        # 删除第一行和最后一行
        print(file_path_)
        modified_lines = lines_[1:-1]
        # 将修改后的内容写回文件
        with open(file_path_, 'w', encoding='gbk') as file_:
            file_.writelines(modified_lines)


def process_folder(folder_path_):
    pattern = os.path.join(folder_path_, '*.cpp')
    for file_path_ in glob.glob(pattern):
        process_file(file_path_)


code_header_path = [
    "3mm",
    "atax",
    "bicg",
    "covariance",
    "gemm",
    "gesummv",
    "heat-3d",
    "mvt",
]
folder_head_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_hls_DSE/Polybench_kernel_hls_llama3_aug"

# remove markdown
for file_path in code_header_path:
    folder_path = os.path.join(folder_head_path, f"{file_path}")
    process_folder(folder_path)

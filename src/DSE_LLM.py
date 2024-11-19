import os
import shutil

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from concurrent.futures import ThreadPoolExecutor

# coding=utf-8
os.environ["OPENAI_API_BASE"] = "https://a.fe8.cn/v1"
os.environ["OPENAI_API_KEY"] = "sk-jxGxEstKGNXlwD4gaFIIveFQOAWm7hRxUZth8k191o5m8DE4"
chat = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"),
                  base_url=os.environ.get("OPENAI_API_BASE"),
                  model='gpt-4o-2024-08-06',
                  temperature=0.7)

oracle_hlsc_code_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_hls"
output_file_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_hls_DSE/Polybench_kernel_hls_4o_simple"

code_header_path = [
    "3mm",
]
origin_code_cpps = [
    "3mm.cpp",
]

def DSE_prompt(hls_code):
    prompt = f"""Your task is to optimize an operator (kernel) in HLS by inserting #pragma directives to optimize loops and arrays. 
    The design of low latency with relative low resource utilization is prefered.
    You can use the following pragma types:
    Loop Pipeline
    Loop Unroll
    Array Partition

    The provided code:
    {hls_code}
    Output the modified code, no other explanations, no markdown format.
    """
    return prompt

def copy_run_hls_tcl(target_dir, output_dir, project_name):
    # Define the source and destination file paths
    source_file = os.path.join(target_dir, 'run_hls.tcl')
    destination_file = os.path.join(output_dir, 'run_hls.tcl')
    souce_header_file = os.path.join(target_dir, f'{project_name}.h')
    destination_header_file = os.path.join(output_dir, f'{project_name}.h')

    # Check if the source file exists
    if os.path.exists(source_file):
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy the file
        shutil.copy(source_file, destination_file)
        shutil.copy(souce_header_file, destination_header_file)
        print(f"Successfully copied {source_file} to {destination_file}")
    else:
        print(f"File {source_file} does not exist.")


def process_file_pair(code_path, origin_code_cpp):
    code_cpp = os.path.splitext(origin_code_cpp)[0]
    origin_cpp_folder = os.path.join(oracle_hlsc_code_path, f"{code_path}")
    origin_cpp_code_head = os.path.join(origin_cpp_folder, f"{code_cpp}.cpp")
    output_cpp_folder = os.path.join(output_file_path, f"{code_path}")
    output_cpp_name = os.path.join(output_cpp_folder, f"{origin_code_cpp}")
    
    copy_run_hls_tcl(origin_cpp_folder, output_cpp_folder, code_path)

    # read buggy code
    if os.path.exists(origin_cpp_code_head):
        with open(origin_cpp_code_head, 'r', encoding='utf-8') as file:
            origin_cpp_code = file.read()
    else:
        print(f"file path {origin_cpp_code_head} doesn't exist.")

    prompt = DSE_prompt(origin_cpp_code)
    messages = [
        SystemMessage(content="""You are an expert in High-Level Synthesis (HLS) programming."""),
        HumanMessage(content=prompt),
    ]
    res = chat.invoke(messages)

    directory = os.path.dirname(output_cpp_name)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(output_cpp_name, "w", encoding='utf8') as file:
        file.write(res.content)


with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit tasks to the executor
    for code_path, code_cpp in zip(code_header_path, origin_code_cpps):
        executor.submit(process_file_pair, code_path, code_cpp)

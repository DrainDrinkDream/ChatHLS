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

oracle_hlsc_code_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel"
oracle_cpp_code_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_cpp_labled"
output_file_path = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_hls"

code_header_path = [
    "2mm",
    "correlation",
    "floyd-warshall",
    "jacobi-2d",
    "nussinov",
    "symm",
    "syr2k",
    "trmm"
]
origin_code_cpps = [
    "2mm.cpp",
    "correlation.cpp",
    "floyd-warshall.cpp",
    "jacobi-2d.cpp",
    "nussinov.cpp",
    "symm.cpp",
    "syr2k.cpp",
    "trmm.cpp"
]

def C2HLS_prompt(cpp_code, hls_code):
    prompt = f"""Your task is to convert the given modified CPP code into HLS code, where you need to remove comments in the CPP code that are in the format of /*L1*/. An example is as follows:
    Code segment with comments: /*L1:*/    for (int i = 0; i < 16; ++i)
    The code segment you need after modification: L1:    for (int i = 0; i < 16; ++i)
    I will provide you with the complete code that needs to be modified, as well as the HLS code without the above comment format to help you add necessary code:
    The code you need to modify:
    {cpp_code}
    The reference HLS code:
    {hls_code}
    Just output the code, no other explanations, and do not use markdown format
    """
    return prompt

def process_file_pair(code_path, origin_code_cpp):
    code_cpp = os.path.splitext(origin_code_cpp)[0]
    hls_cpp_code_head = os.path.join(oracle_hlsc_code_path, code_path, f"{code_cpp}.cpp")
    origin_cpp_code_head = os.path.join(oracle_cpp_code_path, code_path, f"{code_cpp}.cpp")
    output_cpp_name = os.path.join(output_file_path, code_path, f"{origin_code_cpp}")
    

    # read buggy code
    if os.path.exists(origin_cpp_code_head):
        with open(origin_cpp_code_head, 'r', encoding='utf-8') as file:
            origin_cpp_code = file.read()
    else:
        print(f"file path {origin_cpp_code_head} doesn't exist.")

    if os.path.exists(hls_cpp_code_head):
        with open(hls_cpp_code_head, 'r', encoding='utf-8') as file:
            hls_cpp_code = file.read()
    else:
        print(f"file path {hls_cpp_code_head} doesn't exist.")

    prompt = C2HLS_prompt(origin_cpp_code, hls_cpp_code)
    messages = [
        SystemMessage(content="""You are an expert in High-Level Synthesis (HLS) programming. 
        Your primary task is to translate C/C++ programs according to the provided information into HLS code."""),
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

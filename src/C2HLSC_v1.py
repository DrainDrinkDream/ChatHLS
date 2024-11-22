import os

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from concurrent.futures import ThreadPoolExecutor

# coding=utf-8
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""
chat = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"),
                  base_url=os.environ.get("OPENAI_API_BASE"),
                  model='gpt-4o-2024-08-06',
                  temperature=0.7)

oracle_cpp_code_path = "./Polybench_kernel_cpp"
output_file_path = "./Polybench_kernel_hls"

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
origin_code_cpps = [
    "3mm.cpp",
    "atax.cpp",
    "bicg.cpp",
    "covariance.cpp",
    "gemm.cpp",
    "gesummv.cpp",
    "heat-3d.cpp",
    "mvt.cpp",
]

def C2HLS_prompt(cpp_code, head_code):
    prompt = f"""Convert the provided C++ code into HLS (High-Level Synthesis) code according to the given header file to modify the data type.
    During the conversion, be mindful of any incompatibilities between HLS and certain C algorithms.
    Output the translated code without other description.

    C++ Code to be Converted:
    {cpp_code}

    HLS headfile:
    {head_code}"""
    return prompt

def process_file_pair(code_path, origin_code_cpp):
    code_cpp = os.path.splitext(origin_code_cpp)[0]
    origin_head_code_head = os.path.join(oracle_cpp_code_path, code_path, f"{code_cpp}.cpp")
    origin_cpp_code_head = os.path.join(oracle_cpp_code_path, code_path, f"{code_cpp}.cpp")
    output_cpp_name = os.path.join(output_file_path, code_path, f"{origin_code_cpp}")


    # read buggy code
    if os.path.exists(origin_cpp_code_head):
        with open(origin_cpp_code_head, 'r', encoding='utf-8') as file:
            origin_cpp_code = file.read()
    else:
        print(f"file path {origin_cpp_code_head} doesn't exist.")

    if os.path.exists(origin_head_code_head):
        with open(origin_head_code_head, 'r', encoding='utf-8') as file:
            head_cpp_code = file.read()
    else:
        print(f"file path {origin_head_code_head} doesn't exist.")

    prompt = C2HLS_prompt(origin_cpp_code, head_cpp_code)
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

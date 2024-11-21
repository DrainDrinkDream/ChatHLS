import re
import os

# Example usage
RUN_MODE = 0

def parse_rpt_file(rpt_file_path, output_file_path):
    with open(rpt_file_path, 'r') as f:
        lines = f.readlines()

    clock_period_ns = None
    latency_cycles = None
    utilization = {}

    for i, line in enumerate(lines):
        line = line.strip()
        if '|ap_clk' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                clock_str = parts[2].strip()
                if clock_str.endswith('ns'):
                    clock_period_ns = float(clock_str.replace('ns', '').strip())
                    print(f"Clock Period {clock_period_ns} ns")

        elif re.search(r'\|\s*min\s*\|\s*max\s*\|\s*min\s*\|\s*max\s*\|\s*min\s*\|\s*max\s*\|\s*Type\s*\|', line):
            if i + 2 < len(lines):
                data_line = lines[i + 2].strip()

                data_parts = [part.strip() for part in data_line.strip().split('|') if part.strip()]
                if len(data_parts) >= 7:
                    min_cycles_str = data_parts[0]
                    try:
                        latency_cycles = int(min_cycles_str)
                        print(f"Latency cycles: {latency_cycles} cycles")
                    except ValueError:
                        pass
        elif '|Utilization (%)' in line:
            parts = line.split('|')
            if len(parts) >= 7:
                util_values = {}
                keys = ['util_bram', 'util_dsp', 'util_ff', 'util_lut', 'util_uram']
                for idx, key in enumerate(keys, start=2):
                    value_str = parts[idx].strip().replace('-', '0')
                    try:
                        util_values[key] = int(value_str)
                    except ValueError:
                        util_values[key] = 0
                utilization.update(util_values)
                print(f"Resource Utilization : {utilization}")

    if clock_period_ns is not None and latency_cycles is not None:
        latency_sec = latency_cycles * clock_period_ns / 10
        latency_us = latency_sec * 1e6
    else:
        latency_sec = None
        latency_us = None

    with open(output_file_path, 'w') as f:
        if latency_sec is not None:
            f.write(f"latency: {latency_sec:.6f} cycles\n")
        else:
            f.write("latency: N/A\n")
        for key in ['util_bram', 'util_dsp', 'util_ff', 'util_lut', 'util_uram']:
            value = utilization.get(key, 'N/A')
            f.write(f"{key}: {value}%\n")
    
    return utilization

if RUN_MODE:
    DSE_Dataset_heads = [
        "machsuite-md-knn",
        "machsuite-sort-radix",
        "machsuite-spmv-ellpack",
        "machsuite-stencil2d",
        "rodinia_cfd_step_factor_1_tiling_0",
        "rodinia_dilate_1_tiling_0",
        "rodinia_lc_gicov_0_baseline_0",
        "rodinia_lc_mgvf_1_tiling_0",
        "rodinia_streamcluster_1_tiling_0",
        "rodinia-backprop-0-baseline-back",
        "rodinia-backprop-0-baseline-forward",
        "rodinia-backprop-1-tiling-back",
        "rodinia-backprop-1-tiling-forward",
        "rodinia-backprop-2-pipeline-back",
        "rodinia-backprop-2-pipeline-forward",
        "rodinia-kmeans-2-pipeline",
        "rodinia-knn-1-tiling",
        "rosetta-spam-filter",
        "serrano-kalman-filter",
        "spcl_example_05",
        "vitis-tsp"
    ]
    test_proj_heads = [
        "md_knn",
        "sort",
        "spmv",
        "stencil",
        "md_cfd_step_factor",
        "dilate",
        "lc_gicov",
        "lc_mgvf",
        "streamcluster",
        "backdrop_0",
        "md_forward_0",
        "backdrop_1",
        "forward_1",
        "backdrop_2",
        "forward_2",
        "kmeans",
        "knn",
        "sgd",
        "krnl_KALMAN",
        "MatrixMultiplication",
        "tsp"
    ]
    main_function_heads = [
        "md_kernel",
        "ss_sort",
        "ellpack",
        "stencil",
        "cfd_step_factor_workload",
        "dilate_workload",
        "lc_gicov_workload",
        "lc_mgvf_workload",
        "streamcluster_workload",
        "backdrop_0_baseline_workload",
        "forward_0_baseline_workload",
        "backdrop_1_tilling_workload",
        "forward_1_tilling_workload",
        "backdrop_2_pipeline_workload",
        "forward_2_pipeline_workload",
        "kmeans_workload",
        "knn_workload",
        "SgdLR",
        "krnl_KALMAN",
        "MatrixMultiplication",
        "tsp",
    ]
    rpt_file_path_head = "E:/VScode/HLS_LLM_Code/HLSGen/SFT_Oracle_database"
    output_file_path_head = rpt_file_path_head

    for DSE_Dataset_head, test_proj_head, main_function_head in zip(DSE_Dataset_heads, test_proj_heads, main_function_heads):
        rpt_file_path = os.path.join(rpt_file_path_head, DSE_Dataset_head, f"test_proj_{test_proj_head}", "solution/syn/report", f"{main_function_head}_csynth.rpt")
        output_file_path = os.path.join(output_file_path_head, DSE_Dataset_head, "PPA_report.txt")
        utilization = parse_rpt_file(rpt_file_path, output_file_path)
        print(utilization['util_dsp'])

else:
    code_header_path = [
    "2mm",
    "correlation",
    "floyd-warshall",
    "jacobi-2d",
    "nussinov",
    "symm",
    "syr2k",
    "trmm",
    "3mm",
    "atax",
    "bicg",
    "covariance",
    "gemm",
    "gesummv",
    "heat-3d",
    "mvt",
    ]
    rpt_file_path_head = "E:/VScode/HLS_LLM_Code/HLSGen/Polybench_kernel_hls_DSE/Polybench_kernel_hls_4o_aug"
    output_file_path_head = rpt_file_path_head
    for code_header in code_header_path:
        rpt_file_path = os.path.join(rpt_file_path_head, code_header, f"test_proj_{code_header}", "solution/syn/report", f"kernel_{code_header}_csynth.rpt")
        output_file_path = os.path.join(output_file_path_head, code_header, "PPA_result.txt")

        if(code_header == "heat-3d"):
            rpt_file_path = os.path.join(rpt_file_path_head, code_header, f"test_proj_heat_3d", "solution/syn/report", f"kernel_heat_3d_csynth.rpt")
            output_file_path = os.path.join(output_file_path_head, code_header, "PPA_result.txt")
        if(code_header == "floyd-warshall"):
            rpt_file_path = os.path.join(rpt_file_path_head, code_header, f"test_proj_floyd-warshall", "solution/syn/report", f"kernel_floyd_warshall_csynth.rpt")
            output_file_path = os.path.join(output_file_path_head, code_header, "PPA_result.txt")
        if(code_header == "jacobi-2d"):
            rpt_file_path = os.path.join(rpt_file_path_head, code_header, f"test_proj_jacobi-2d", "solution/syn/report", f"kernel_jacobi_2d_csynth.rpt")
            output_file_path = os.path.join(output_file_path_head, code_header, "PPA_result.txt")

        if(os.path.exists(rpt_file_path)):
            rpt_file_path = rpt_file_path
        else:
            continue
        utilization = parse_rpt_file(rpt_file_path, output_file_path)

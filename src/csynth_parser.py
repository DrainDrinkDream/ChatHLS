import json
import shutil
import os
import re


def parse_csynth(log_lines):
    passed_csynth = None
    csynth_failure_reason = None
    csynth_failure_details = []
    in_csynth = False
    success_indicators = {'rtl_generated': False, 'fmax_estimated': False}

    for line in log_lines:
        if 'Running: csynth_design' in line:
            in_csynth = True
            passed_csynth = False  # Assume failure unless proven otherwise
            csynth_failure_details = []  # Reset details for new synthesis section
        elif 'Finished Command csynth_design' in line:
            in_csynth = False
            # Check if all required success indicators are True
            if all(success_indicators.values()):
                passed_csynth = True
                #csynth_failure_details = []  # Clear details as CSynth passed
            else:
                passed_csynth = False
                # Filter to only keep WARNING and ERROR lines if synthesis failed
                csynth_failure_details = [line for line in csynth_failure_details if "WARNING" in line or "ERROR" in line]
                if csynth_failure_reason==None:
                    csynth_failure_reason = "Unknown error"
            break  # Exit loop after csynth section ends
        elif in_csynth:
            if 'Generating Verilog RTL for' in line:
                success_indicators['rtl_generated'] = True
            if 'Estimated Fmax:' in line:
                success_indicators['fmax_estimated'] = True
            if "ERROR" in line or "WARNING" in line:
                csynth_failure_details.append(line)
            if 'Pre-synthesis failed.' in line:
                csynth_failure_reason = "Code Pre-synthesis failed"
            if "#pragma HLS" in line and "is only allowed in function scope" in line:
                csynth_failure_reason = "#pragma location fault"
            if "Syn check fail" in line:
                csynth_failure_reason = "Code Pre-synthesis success, synthesis failed"
            if "problem during source synthesis" in line:
                csynth_failure_reason = "Source synthesis failed"
            if "is invalid in" in line:
                csynth_failure_reason = "Invalid code construct/type for Synthesis"
            if "invalid variable expr" in line: 
                csynth_failure_reason = "Invalid variable expression"
            if "Terminated" in line:
                csynth_failure_reason = "Excessive pragma optimization causes compiler timeouts and high resource utilization."
            if "All loop constraints were NOT satisfied." in line:
                csynth_failure_reason = "Timing/Loop constraints not satisfied, synthesis may pass"
            if "use of undeclared identifier" in line:
                csynth_failure_reason = "Undeclared identifier"
            if "Killed" in line:
                csynth_failure_reason = "Synthesis time-out"
            if "ERROR: [HLS 207-1186] expected expression" and "ERROR: [HLS 207-1222] expected statement" in line:
                csynth_failure_reason = "Loop Label Misplacement"
            if "expected '}'" in line:
                csynth_failure_reason = "Unclosed Parentheses"
            if "unknown HLS pragma ignored" in line:
                csynth_failure_reason = "Undefined Pragma type"
            if "Cannot find any design unit to elaborate." in line:
                csynth_failure_reason = "Source file doesn't exist"
            if "unknown type name 't_ap_fixed'" and "ERROR: [HLS 207-3801] unknown type name 't_ap_fixed'" in line:
                csynth_failure_reason = "#include missing;"
                
    for line in log_lines:
        if 'PPA Unsatisfied' in line:
            print('PPA Unsatisfied')
            passed_csynth = False
            in_csynth = False
            csynth_failure_reason = "PPA Unsatisfied may cause co-simulation false"
            csynth_failure_details = [line for line in csynth_failure_details if "WARNING" in line or "ERROR" in line]

    return passed_csynth, csynth_failure_reason, csynth_failure_details

def parse_log(log_file_path, project_name):
    with open(log_file_path, 'r') as file:
        log_content = file.readlines()

    # Parse C Synthesis
    passed_csynth, csynth_failure_reason, csynth_failure_details = parse_csynth(log_content)

    # if passed_csynth:
    #     try:
    #         shutil.rmtree(project_name)
    #         print(f"delete folder {project_name} because it passed C Synthesis")
    #     except Exception as e:
    #         print(f"delete folder {project_name} occur error {e}")

    results = {
        "Project Name": project_name,
        "Passed C-synth": passed_csynth,
        "C-SYNTH Failure Reason": csynth_failure_reason,
        "C-SYNTH Failure Details": csynth_failure_details,
    }
    return results

def write_to_json(data, file_name):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def parse_rpt_file(rpt_file_path):
    with open(rpt_file_path, 'r') as f:
        lines = f.readlines()

    clock_period_ns = None
    latency_cycles = None

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

    if clock_period_ns is not None and latency_cycles is not None:
        latency_sec = latency_cycles * clock_period_ns / 10
    else:
        latency_sec = None
    print("latency_sec: ", latency_sec)
    if latency_sec == 'N/A':
        latency_sec = 0

    return latency_sec

def get_project_latency(project_name, rpt_file_path_head):
    parts = project_name.split('_')
    project_name = parts[0]
    rpt_file_path = os.path.join(rpt_file_path_head, project_name, f"test_proj_{project_name}", "solution/syn/report", f"kernel_{project_name}_csynth.rpt")

    if(project_name == "heat-3d"):
        rpt_file_path = os.path.join(rpt_file_path_head, project_name, f"test_proj_heat_3d", "solution/syn/report", f"kernel_heat_3d_csynth.rpt")
    if(project_name == "floyd-warshall"):
        rpt_file_path = os.path.join(rpt_file_path_head, project_name, f"test_proj_floyd-warshall", "solution/syn/report", f"kernel_floyd_warshall_csynth.rpt")
    if(project_name == "jacobi-2d"):
        rpt_file_path = os.path.join(rpt_file_path_head, project_name, f"test_proj_jacobi-2d", "solution/syn/report", f"kernel_jacobi_2d_csynth.rpt")
    print(rpt_file_path)
    if(os.path.exists(rpt_file_path)):
        rpt_file_path = rpt_file_path
    else:
        return 0
    latency = parse_rpt_file(rpt_file_path)
    return latency

def latency_project_compare(latency, project_name):
    if(project_name == "3mm" and latency <= 8000 and latency != 0):
        return True
    if(project_name == "atax" and latency <= 2000 and latency != 0):
        return True
    if(project_name == "bicg" and latency <= 1700 and latency != 0):
        return True
    if(project_name == "covariance" and latency <= 4000 and latency != 0):
        return True
    if(project_name == "gemm" and latency <= 16000 and latency != 0):
        return True
    if(project_name == "gesummv" and latency <= 500 and latency != 0):
        return True
    if(project_name == "heat-3d" and latency <= 83000 and latency != 0):
        return True
    if(project_name == "mvt" and latency <= 1700 and latency != 0):
        return True
    else:
        return False
    
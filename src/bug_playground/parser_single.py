# %% [markdown]
# ## Vitis_HLS log parser (2022.1)
# The parser reads the log (from cosole output) to determine the final status of the project. It detects which stage has a failure, extract failure reasons and related logs.

# %%
import re
import os
import csv


code_header_path = [
    "2mm",
    "3mm",
    "atax",
    "bicg",
    "correlation",
    "covariance",
    "floyd-warshall",
    "gemm",
    "gesummv",
    "heat-3d",
    "jacobi-2d",
    "mvt",
    "nussinov",
    "symm",
    "syr2k",
    "trmm"
]
code_cpp_base = [
    "2mm.cpp",
    "3mm.cpp",
    "atax.cpp",
    "bicg.cpp",
    "correlation.cpp",
    "covariance.cpp",
    "floyd-warshall.cpp",
    "gemm.cpp",
    "gesummv.cpp",
    "heat-3d.cpp",
    "jacobi-2d.cpp",
    "mvt.cpp",
    "nussinov.cpp",
    "symm.cpp",
    "syr2k.cpp",
    "trmm.cpp"
]


# %%
def extract_project_bug_name(log_lines, code_header_path, code_cpp_base):
    # Look for the line that specifies the directory path
    directory_line = next((line for line in log_lines if "In directory" in line), None)
    if directory_line:
        # Extract the path from the line
        path_match = re.search(r"In directory '(.+)'", directory_line)
        if path_match:
            directory_path = path_match.group(1)
            # Split the directory path to analyze its components
            path_parts = directory_path.split('/')

            # Initialize variables
            project_name = None
            ref_name = None

            # Check each part of the path against known project names and cpp bases
            for part in path_parts:
                if part in code_header_path:
                    project_name = part
                    #print("detected project name:", project_name)  # Debugging output
                elif any(part.startswith(base.split('.')[0]) for base in code_cpp_base):
                    ref_name = part
                    #print("detected ref name:", ref_name)  # Debugging output

            # If ref_name is not found in the path, look in other log lines
            if not ref_name:
                add_files_lines = [line for line in log_lines if "Running: add_files" in line]
                for line in add_files_lines:
                    file_match = re.search(r"add_files\s+(.+)", line)
                    if file_match:
                        file_path = file_match.group(1)
                        file_name = file_path.split('/')[-1]
                        base_name = file_name.split('.')[0]
                        if any(base_name == base.split('.')[0] for base in code_cpp_base):
                            ref_name = base_name
                            break

            # Validate if we have found valid matches
            if project_name:
                # Handle cases where ref_name might not be present
                ref_name = ref_name if ref_name else "unknown_top_module"
                print("Matched names:", project_name, ref_name)  # Debugging output
                return f"{project_name}_{ref_name}"

    # If no matches or directory line not found, return None
    return None

# %%

def parse_csim(log_lines):
    passed_csim = None
    csim_failure_reason = None
    csim_failure_details = []
    in_csim = False

    for line in log_lines:
        if 'CSIM start' in line:
            in_csim = True
            passed_csim = False  # Assume failure unless proven otherwise
        elif 'Finished Command csim_design' in line:
            in_csim = False
            #if not passed_csim:
                #csim_failure_details = ''.join(csim_failure_details)
            if passed_csim==None:
                passed_csim = False
                csim_failure_reason = "Unknown error"
        elif in_csim:
            if 'HLS 200-10' not in line and 'HLS 200-112' not in line and 'APCC 202' not in line:
                csim_failure_details.append(line)
                #csim_failure_details=''.join(csim_failure_details)
            if 'CSim done with 0 errors' in line:
                passed_csim = True
                #csim_failure_details = []  # Clear details as CSim passed
                # capture csim complication logs even is passed
                break
            if 'failed: nonzero return value' in line:
                csim_failure_reason = "Inconsistent simulation result"
                passed_csim = False
            if 'CSim failed with errors' in line:
                passed_csim = False
                csim_failure_reason = "Runtime error"
            if "compilation error" in line:
                passed_csim = False
                csim_failure_reason = "Compilation error"
            if "Terminated" in line:
                passed_csim = False
                csim_failure_reason = "CSim timeout"

    return passed_csim, csim_failure_reason, csim_failure_details



# %%

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
                csynth_failure_reason = "Synthesis time-out"
            if "All loop constraints were NOT satisfied." in line:
                csynth_failure_reason = "Timing/Loop constraints not satisfied, synthesis may pass"
            if "use of undeclared identifier" in line:
                csynth_failure_reason = "Undeclared identifier"
            if "Killed" in line:
                csynth_failure_reason = "Synthesis time-out"

    return passed_csynth, csynth_failure_reason, csynth_failure_details

# %%
def parse_cosim(log_lines):
    in_cosim = False
    passed_cosim = None
    cosim_failure_details = []
    cosim_failure_reason = None

    for line in log_lines:
        if 'Running: cosim_design' in line:
            in_cosim = True
            passed_cosim = False  # Assume failure unless proven otherwise
        elif 'Finished Command cosim_design' in line:
            in_cosim = False
            # Check if we never updated the pass status to True
            if not passed_cosim:
                # Filter to only keep ERROR and WARNING lines if cosim failed
                cosim_failure_details = [
                                        line for line in cosim_failure_details 
                                        if "ERROR" in line or ("WARNING" in line and "WARNING: [XSIM 43-3431]" not in line)
                                        ]
            break
        elif in_cosim:
            if 'C/RTL co-simulation finished: PASS' in line:
                passed_cosim = True
                cosim_failure_details = []  # Clear details as Co-sim passed
                break
            if "ERROR" in line or "WARNING" in line:
                cosim_failure_details.append(line)
            if 'C/RTL co-simulation finished: FAIL' in line:
                passed_cosim = False
            if 'Aborting co-simulation: C TB simulation failed, nonzero return value' in line:
                cosim_failure_reason = "C TB simulation failed"
            if 'C TB post check failed, nonzero return value' in line:
                cosim_failure_reason = "Inconsistent C/RTL simulation result"
            if 'System recieved a signal named SIGSEGV' in line:
                cosim_failure_reason = "Segmentation fault"
            #if 'There are uninitialized variables' in line:
            #    cosim_failure_reason = "Uninitialized variables"
            if 'Terminated' in line:
                passed_cosim = False
                cosim_failure_reason = "Co-simulation time-out"

    return passed_cosim, cosim_failure_reason, cosim_failure_details


# %%
def parse_log(log_file_path):
    with open(log_file_path, 'r') as file:
        log_content = file.readlines()

    project_name = None
    passed_cosim = None
    cosim_failure_reason = None

    project_name = extract_project_bug_name(log_content,code_header_path, code_cpp_base)

    # Parse C Simulation
    passed_csim, csim_failure_reason, csim_failure_details = parse_csim(log_content)

    # Parse C Synthesis
    passed_csynth, csynth_failure_reason, csynth_failure_details = parse_csynth(log_content)

    passed_cosim, cosim_failure_reason, cosim_failure_details = parse_cosim(log_content)

    results = {
        "Project Name": project_name,
        "Passed C-SIM": passed_csim,
        "C-SIM Failure Reason": csim_failure_reason,
        "C-SIM Failure Details": csim_failure_details,
        "Passed C-synth": passed_csynth,
        "C-SYNTH Failure Reason": csynth_failure_reason,
        "C-SYNTH Failure Details": csynth_failure_details,
        "Passed Co-SIM": passed_cosim,
        "Co-SIM Failure Reason": cosim_failure_reason,
        "Co-SIM Failure Details": cosim_failure_details
    }
    return results


# %% [markdown]
# ## Export to `.csv` for human check

# %%
import os

def collect_data_csv(log_folder_path):
    projects = {}
    log_file_count = 0

    for root, dirs, files in os.walk(log_folder_path):
        for file in files:
            if file.endswith("_log.txt"):
                log_file_path = os.path.join(root, file)
                log_file_count += 1
                print(f"Processing log file: {log_file_path}")

                result = parse_log(log_file_path)
                #print("Parsed result:", result)  # Debug print

                project_name = result.get("Project Name", "Unknown Project")
                print(f"Processing project: {project_name}")  # Debug print

                # Determine overall status and reason for each project and bug
                if result.get("Passed C-SIM", False):
                    if result.get("Passed C-synth", False):
                        if result.get("Passed Co-SIM", False):
                            status = "PASS"
                        else:
                            status = f"COSIM ({result.get('Co-SIM Failure Reason', 'Unknown Reason')})"
                    else:
                        status = f"CSYNTH ({result.get('C-SYNTH Failure Reason', 'Unknown Reason')})"
                else:
                    status = f"CSIM ({result.get('C-SIM Failure Reason', 'Unknown Reason')})"

                if project_name not in projects:
                    projects[project_name] = {}
                projects[project_name]['NL2HLS'] = status
                #print(status)

    print(f"Total log files processed: {log_file_count}")
    return projects




# %%
def write_to_csv(projects, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write header with "Project Name" and "NL2HLS"
        writer.writerow(["Project Name", "NL2HLS"])
        
        # Write data rows
        for project, data in projects.items():
            # Assuming 'NL2HLS' is a key in the data dictionary
            nl2hls_value = data.get('NL2HLS', "N/A")
            writer.writerow([project, nl2hls_value])


# %%
#log_folder_path = "./logs"
#projects = collect_data_csv(log_folder_path)
#write_to_csv(projects, "./project_results.csv")

# %% [markdown]
# ## Export result to dataset

# %%
# write to json
import json

def collect_data_json(log_folder_path):
    projects = {}

    for root, dirs, files in os.walk(log_folder_path):
        for file in files:
            if file.endswith("_log.txt"):
                log_file_path = os.path.join(root, file)
                result = parse_log(log_file_path)  # This function needs to return detailed info for each bug

                project_name = result.get("Project Name", "Unknown Project")

                # Initialize project dictionary if not already present
                if project_name not in projects:
                    projects[project_name] = {}

                # Store detailed bug information under the project
                projects[project_name] = result  # Storing the entire result dictionary under the bug name

    return projects

def write_to_json(data, file_name):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# %%
# Export result to JSON as dataset
# Example usage:
#log_folder_path = "./logs"
#projects = collect_data_json(log_folder_path)
#write_to_json(projects, "project_results.json")

# %% [markdown]
# ## For debug only

# %%
# for debug purpose
#log_file_path = './bug_run_test_3/pp4fpgas_out'


#for root, dirs, files in os.walk(log_file_path):
#    for file in files:
#        if file.endswith("_log.txt"):
#            log_file_paths = os.path.join(root, file)
#            print(f"Processing log file: {log_file_paths}")  # Debug: Print the path of each log file processed
#            result = parse_log(log_file_paths)
#            print(result)


import json
import csv
import sys

def print_json_to_console(data):
    print(json.dumps(data, indent=4))

def print_csv_to_console(data):
    writer = csv.writer(sys.stdout)
    # Write header with "Project Name" and "NL2HLS"
    writer.writerow(["Project Name", "NL2HLS"])
    for project, project_data in data.items():
        # 'project_data' is expected to be a dictionary with key 'NL2HLS'
        nl2hls_value = project_data.get('NL2HLS', "N/A")
        writer.writerow([project, nl2hls_value])


import argparse

def main():
    parser = argparse.ArgumentParser(description="Parse Vitis_HLS log files and export results.")
    parser.add_argument("input_path", type=str, help="Path to a log file or directory containing log files.")
    parser.add_argument("-j", "--json", nargs='?', const=True, default=False, help="Output results in JSON format. Optionally specify a JSON file name.")
    parser.add_argument("-c", "--csv", nargs='?', const=True, default=False, help="Output results in CSV format. Optionally specify a CSV file name.")
    parser.add_argument("-p", "--print", action="store_true", help="Print results to the command line instead of a file.")
    args = parser.parse_args()

    # Determine the output file names or use default names
    json_output_file = "project_results.json" if args.json is True else args.json
    csv_output_file = "project_results.csv" if args.csv is True else args.csv

    # Call processing functions based on input arguments
    if os.path.isdir(args.input_path):
        # Handle directory
        if args.json:
            results = collect_data_json(args.input_path)
            if args.print:
                print_json_to_console(results)
            elif args.json is not True:  # Check if a filename was actually provided
                write_to_json(results, json_output_file)
        if args.csv:
            results = collect_data_csv(args.input_path)
            if args.print:
                print_csv_to_console(results)
            elif args.csv is not True:  # Check if a filename was actually provided
                write_to_csv(results, csv_output_file)
    elif os.path.isfile(args.input_path):
        # Handle single file
        result = parse_log(args.input_path)
        if args.json:
            if args.print:
                print_json_to_console(result)
            elif args.json is not True:
                write_to_json(result, json_output_file)
        if args.csv:
            if args.print:
                print_csv_to_console(result)
            elif args.csv is not True:
                write_to_csv(result, csv_output_file)

if __name__ == "__main__":
    main()

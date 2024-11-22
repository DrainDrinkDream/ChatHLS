import os
import subprocess
import time
import psutil
import csynth_parser

from concurrent.futures import ThreadPoolExecutor

vitis_hls_run = "./vitis_hls.bat"
base_dir = "./Polybench_kernel_hls_4o_aug"
rpt_file_path_head = base_dir
script_name = "run_hls.tcl"   # run_hls.tcl for polybench || dataset_hls.tcl for HLSGEN

def kill_vitis_process():
    """Kill the vitis_hls.exe process if it exists."""
    for proc in psutil.process_iter():
        try:
            if proc.name() == "vitis_hls.exe":
                proc.kill()
                print(f"Killed vitis_hls.exe process.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def compile_with_vitis_hls(script_path, cwd):
    project = os.path.basename(cwd)
    logs_folder = os.path.join(cwd, "logs")
    os.makedirs(logs_folder, exist_ok=True)
    log_file_path = os.path.join(logs_folder, "compilation_log.txt")
    start_time = time.time()
    if os.path.exists(script_path):
        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            try:
                process = subprocess.Popen([vitis_hls_run, script_path],
                               stdout=log_file, stderr=subprocess.STDOUT, cwd=cwd)
                while True:
                    elapsed_time = time.time() - start_time
                    if process.poll() is not None:  # Process has finished
                        if process.returncode == 0:
                            latency = csynth_parser.get_project_latency(project, rpt_file_path_head)
                            ppa_satisfy = csynth_parser.latency_project_compare(latency, project)
                            if not ppa_satisfy:
                                log_file.write("PPA Unsatisfied\n")
                        break
                    if elapsed_time > 500:  # 5 minutes timeout
                        print(f"Timeout: Vitis HLS for {script_path} is hanging. Killing vitis.exe and skipping this iteration.")
                        log_file.write("Terminated\n")
                        kill_vitis_process()  # Kill csim.exe process
                        process.terminate()  # Terminate the Vitis HLS process
                        break
                    time.sleep(20)  # Refresh every 2 seconds            
                print(f"Compilation log saved to: {log_file_path}")

            except subprocess.CalledProcessError as e:
                print(f"Error running Vitis HLS. Error: {e}")
    else:
        print("can't find dataset_hls.tcl")
        return ""
    
    log_input_path = cwd
    json_output_file = os.path.join(cwd, "csynth_analysis.json")
    results = csynth_parser.parse_log(log_file_path, log_input_path)
    if not results["Passed C-synth"]:
        csynth_parser.write_to_json(results, json_output_file)

def main():
    if not os.path.exists(base_dir):
        print(f"Base dir {base_dir} doesn't exist")
        return

    for item in os.listdir(base_dir):
        sub_dir = base_dir + f"/{item}"
        if os.path.isdir(sub_dir):
            script_path = sub_dir + f"/{script_name}"
            if os.path.exists(script_path):
                print(f"Handling {sub_dir}")
                compile_with_vitis_hls(script_path, sub_dir)
            else:
                print(f"Script {script_name} not found in {sub_dir}")
        else:
            print(f"Skip {sub_dir}, not a directory")

# just run specific project
def main1():
    if not os.path.exists(base_dir):
        print(f"base_dir {base_dir} doesn't exist")
        return

    sub_dir = base_dir + "/bicg"   ##    "nussinov","symm","syr2k","trmm"
    if os.path.isdir(sub_dir):
        script_path = sub_dir + f"/{script_name}"
        print(f"handling {sub_dir}")

        compile_with_vitis_hls(script_path, sub_dir)
    else:
        print(f"skip {sub_dir}")

if __name__ == "__main__":
    main1()

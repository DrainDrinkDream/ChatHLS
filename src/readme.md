# ChatHLS Frontend Workflow

## Converting C Algorithms to HLSC Code and Algorithm Optimization

This document outlines the workflow for converting C algorithms into High-Level Synthesis C (HLSC) code and optimizing them using a Large Language Model (LLM). The process involves several steps, including code transformation, loop and array information extraction, initial HLSC code conversion, Design Space Exploration (DSE) optimization, and resource utilization analysis.

---
# ChatHLS Frontend Workflow

## Converting C Algorithms to HLSC Code and Algorithm Optimization

This document outlines the workflow for converting C algorithms into High-Level Synthesis C (HLSC) code and optimizing them using a Large Language Model (LLM). The process involves several steps, including code transformation, loop and array information extraction, initial HLSC code conversion, Design Space Exploration (DSE) optimization, and resource utilization analysis.

---

## Workflow Overview

The workflow consists of the following main steps:

- [ChatHLS Frontend Workflow](#chathls-frontend-workflow)
  - [Converting C Algorithms to HLSC Code and Algorithm Optimization](#converting-c-algorithms-to-hlsc-code-and-algorithm-optimization)
- [ChatHLS Frontend Workflow](#chathls-frontend-workflow-1)
  - [Converting C Algorithms to HLSC Code and Algorithm Optimization](#converting-c-algorithms-to-hlsc-code-and-algorithm-optimization-1)
  - [Workflow Overview](#workflow-overview)
    - [1. Prepare Original C Code](#1-prepare-original-c-code)
    - [2. Code Transformation and Information Extraction](#2-code-transformation-and-information-extraction)
    - [3. Initial HLSC Code Conversion](#3-initial-hlsc-code-conversion)
    - [4. DSE Optimization without Loop/Array Information](#4-dse-optimization-without-looparray-information)
    - [5. DSE Optimization with Loop/Array Information](#5-dse-optimization-with-looparray-information)
    - [6. Synthesis and Resource Utilization Analysis](#6-synthesis-and-resource-utilization-analysis)
  - [Additional Notes](#additional-notes)

---

### 1. Prepare Original C Code

- **Directory**: `Polybench_kernel_cpp`
- **Description**: This directory contains the original C code that you wish to convert.
- **Note**: You should provide your own C algorithms for conversion.
- **Purpose**: Before conversion to HLSC, we need to extract loop and array information to aid in DSE.

---

### 2. Code Transformation and Information Extraction

- **Directory**: `Polybench_kernel_labeled`
- **Description**: This directory will contain the transformed C code and extracted loop/array information. The transformation involves labeling loops and arrays within the code.
- **Procedure**:
  1. **Access the Docker Tool**: Use the Docker container that contains the code transformation tools.
     - In the terminal, copy the `Polybench_kernel_cpp` directory into the Docker container:

       ```bash
       cp -r ./Polybench_kernel_cpp <container_id>:/tool/HLSAnalysisTools
       ```

       Replace `<container_id>` with your Docker container ID (e.g., `16a8738f593e`).

     - Attach to the Docker container:

       ```bash
       docker attach <container_id>
       ```

  2. **Run the Transformation Tool**:
     - Inside the Docker container, navigate to the tools directory:

       ```bash
       cd /tool/HLSAnalysisTools
       ```

     - Verify that your C algorithm files are present in the `Polybench_kernel_cpp` directory.

     - Execute the analysis tool:

       ```bash
       ./analysis_tool.sh Polybench_kernel_cpp/gemm/gemm.cpp kernel_gemm
       ```

       Replace `Polybench_kernel_cpp/gemm/gemm.cpp` with the path to your C file, and `kernel_gemm` with the appropriate kernel name.

     - The transformed files and loop/array information will be generated in the current directory.

  3. **Exit the Docker Container**:

     ```bash
     exit
     ```

  4. **Copy Transformed Files Back to Host**:
     - In the terminal on the host machine, copy the transformed files from the Docker container:

       ```bash
       cp -r <container_id>:/tool/HLSAnalysisTools/Polybench_kernel_cpp ./Polybench_kernel_labeled
       ```

---

### 3. Initial HLSC Code Conversion

- **Directory**: `Polybench_kernel_hls`
- **Description**: This directory initially contains HLSC code directly converted from the original C algorithms using the LLM. This code serves as a reference for variable names and header file inclusions.
- **Procedure**:
  1. **Convert C to HLSC (Version 1)**:
     - Execute the conversion script:

       ```bash
       python C2HLSC_v1.py
       ```

     - This script converts the C algorithms in `Polybench_kernel_cpp` into HLSC code.
     - Provide the necessary header files to ensure the basic information is correct.

  2. **Generate Transformed HLSC Code**:
     - The converted HLSC code is now available in `Polybench_kernel_hls`, serving as a reference for the subsequent conversion process.

  3. **Convert Labeled C to HLSC (Version 2)**:
     - Execute the second conversion script:

       ```bash
       python C2HLSC_v2.py
       ```

     - This script processes the transformed (labeled) C code to produce the HLSC code, turning labels from comments into meaningful annotations in the code.

---

### 4. DSE Optimization without Loop/Array Information

- **Directory**: `Polybench_kernel_hls_o1_simple`
- **Description**: This directory contains HLSC code optimized by performing DSE (inserting pragma annotations) using the LLM, without referencing the previously extracted loop and array information.
- **Procedure**:
  - Execute the DSE script:

    ```bash
    python DSE_LLM.py
    ```

  - This script uses the LLM to insert pragma annotations for optimization directly on the HLSC code.

---

### 5. DSE Optimization with Loop/Array Information

- **Directory**: `Polybench_kernel_hls_o1`
- **Description**: This directory contains HLSC code optimized by performing DSE using the LLM, this time leveraging the previously extracted loop and array information for more informed optimizations.
- **Procedure**:
  - Execute the augmented DSE script:

    ```bash
    python DSE_LLM_aug.py
    ```

  - This script uses the LLM to insert pragma annotations, taking into account the loop and array information extracted in step 2.

---

### 6. Synthesis and Resource Utilization Analysis

- **Purpose**: The optimized HLSC code can be synthesized using Vitis HLS to generate hardware descriptions and to analyze resource utilization.
- **Procedure**:
  1. **Run Synthesis**:
     - Execute the synthesis script:

       ```bash
       python run_hls.py
       ```

     - This script runs Vitis HLS synthesis on the optimized HLSC code.

  2. **Extract PPA Information**:
     - Parse the performance, power, and area (PPA) report:

       ```bash
       python PPA_info_parser.py
       ```

     - This script extracts relevant PPA information from the synthesis reports.

  3. **Iterative Optimization (If Necessary)**:
     - If the resource utilization exceeds 100%, perform iterative optimization to reduce resource usage.
     - Execute the iterative DSE script:

       ```bash
       python DSE_Iteration.py
       ```

     - Repeat the synthesis and analysis steps until the resource utilization is within acceptable limits.

---

## Additional Notes

- **Docker Container ID**: Replace `<container_id>` with your actual Docker container ID in the commands provided.
- **Paths and File Names**: Adjust the file paths and names in the commands according to your specific setup and files.
- **LLM Requirements**: Ensure that the LLM used for code conversion and DSE optimization is properly configured and accessible by the scripts.
- **Header Files**: Provide necessary header files in the `Polybench_kernel_cpp` and `Polybench_kernel_hls` directories to avoid compilation errors.
- **Dependencies**: Ensure that all required Python packages and tools are installed, including Vitis HLS, Docker, and any other dependencies.

---

By following this workflow, you can effectively convert your C algorithms into optimized HLSC code suitable for hardware synthesis, leveraging the power of LLMs for code transformation and optimization.
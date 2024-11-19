
ChatHLS前端工作流--C算法转换为HLSC代码，对其进行算法优化

工作流程大致如下：
1. Polybench_kernel_cpp中存放有原始的C代码，在对其进行向HLSC转换之前，需要先通过编译器抓取他的Loop/Array信息，为DSE提供依据；
（此处应由用户自己提供待转换的C算法）
2. Polybench_kernel_labled文件中存放有原始C代码经过转换工具后的变形代码和Loop/Array信息，所谓变形就是对Loop/Array打上标签；
（此处通过访问Docker中工具进行代码变形和Loop/Array信息提取。
具体操作如下：在Terminal中执行指令：
docker cp ./Polybench_kernel_cpp 16a8738f593ea1fe0ef47f70a25f571e240b5cb152fb0a617b54297c39745b67:/tool/HLSAnalysisTools
docker attach 16a8738f593ea1fe0ef47f70a25f571e240b5cb152fb0a617b54297c39745b67
进入docker容器中 cd /tool/HLSAnalysisTools
检查确定路径中已经有你添加进去的C算法后，执行./analysis_tool.sh Polybench_kernel_cpp/gemm/gemm.cpp kernel_gemm
得到的变形后文件和相关信息会保留在当前路径下  exit  退出容器
Terminal中执行
docker cp 16a8738f593ea1fe0ef47f70a25f571e240b5cb152fb0a617b54297c39745b67:/tool/HLSAnalysisTools/Polybench_kernel_cpp ./Polybench_kernel_labled
）
3. Polybench_kernel_hls文件中一开始存放有直接将C算法通过LLM转换后的HLSC代码，将其作为变量名、头文件包含的参考代码，对变形后的C算法进行实际转化，将标签从注释转换为实际意义上的标签；
（先执行 python C2HLSC_v1.py   此时首先将Polybench_kernel_cpp中C算法直接转换成HLSC，此时应该提供可以参考的头文件，保证基本的信息不会出错
  此时在Polybench_kernel_hls路径下已经存在可以参考转换的HLSC code,他将为正式的转换过程提供参考
  此时执行 python C2HLSC_v2 ，得到变形后的HLSC代码
）
4. Polybench_kernel_hls_o1_simple文件中即通过LLM执行DSE(插入pragma annotation)优化后的HLSC算法，这里的simple是指LLM直接对，而不参考之前抓取到的loop/Array信息
（执行 python DSE_LLM.py）
5. Polybench_kernel_hls_o1文件中即通过LLM执行DSE(插入pragma annotation)优化后的HLSC算法，这里参考之前抓取到的loop/Array信息
（执行 python DSE_LLM_aug.py）
6. 以上得到的优化后的算法可以通过run_hls.py脚本运行Vitis_HLS 综合，再通过PPA_info_parser.py抓取相关信息,如果发现resource utilization超出100%,可以选择执行DSE_Iteration.py进行迭代优化，直到资源利用率下降到可用空间
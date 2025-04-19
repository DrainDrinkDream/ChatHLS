open_project -reset test_proj_gemm
set_top kernel_gemm
add_files gemm.cpp
open_solution -reset solution
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
export_design -format ip_catalog
exit

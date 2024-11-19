open_project -reset test_proj_jacobi-2d
add_files jacobi-2d.cpp
add_files jacobi-2d.h
open_solution solution
set_top kernel_jacobi_2d
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
exit
open_project -reset test_proj_nussinov
add_files nussinov.cpp
add_files nussinov.h
open_solution solution
set_top kernel_nussinov
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
exit
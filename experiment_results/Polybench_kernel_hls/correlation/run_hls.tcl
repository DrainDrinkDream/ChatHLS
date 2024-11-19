open_project -reset test_proj_correlation
add_files correlation.cpp
add_files correlation.h
open_solution solution
set_top kernel_correlation
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
exit

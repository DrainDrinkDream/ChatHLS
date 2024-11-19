open_project -reset test_proj_2mm
add_files 2mm.cpp
add_files 2mm.h
open_solution solution
set_top kernel_2mm
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
exit

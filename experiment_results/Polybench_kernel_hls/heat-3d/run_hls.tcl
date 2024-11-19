open_project -reset test_proj_heat_3d
set_top kernel_heat_3d
add_files heat-3d.cpp
open_solution -reset solution
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
export_design -format ip_catalog
exit

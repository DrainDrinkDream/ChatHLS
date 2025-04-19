open_project -reset test_proj_mvt
set_top kernel_mvt
add_files mvt.cpp
open_solution -reset solution
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
csynth_design
export_design -format ip_catalog
exit

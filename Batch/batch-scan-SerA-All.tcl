# Script to run scans in batch mode
# Syntax: vivado -mode batch -source Batch/batch-scan-SerA-All.tcl

open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target {localhost:3121/xilinx_tcf/Xilinx/000015de453601}
current_hw_device [get_hw_devices xcvu9p_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcvu9p_0] 0]

# Program device? Currently done interactively

# Generate links
source ./GenerateLinks/SerA/b14_create_links_b129-130-131.tcl

# Run scan
source ./Scans/SerA-2/SerA-2-BTScan-BER-All.tcl

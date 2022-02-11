open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target {localhost:3121/xilinx_tcf/Xilinx/00000000000000}
current_hw_device [get_hw_devices xcvu7p_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcvu7p_0] 0]
source /home/meholmbe/optics-scan/BGenerateLinks/gen_links_vu7p_alpha.tcl
source /home/meholmbe/optics-scan/Scans/BTscanSWING-all-mei.tcl
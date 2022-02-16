
# Script to run scans in batch mode
# Syntax: vivado -mode batch -source batch-scan-all.tcl

open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target {localhost:3121/xilinx_tcf/Xilinx/00000000000000}
current_hw_device [get_hw_devices xcvu7p_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcvu7p_0] 0]

# Program device? Currently done interactively

# Generate links
source /home/meholmbe/optics-scan/GenerateLinks/gen_links_vu7p_alpha.tcl
# remove_hw_sio_link [get_hw_sio_links {localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y19/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y19/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y17/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y21/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y20/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y16/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y18/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y18/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_228/MGT_X1Y16/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y20/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y27/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y23/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y25/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y27/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y23/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y25/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y26/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y22/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y24/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y24/RX localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_229/MGT_X1Y22/TX->localhost:3121/xilinx_tcf/Xilinx/00000000000000/0_1_0_0/IBERT/Quad_230/MGT_X1Y26/RX}]

# Run scan
source /home/meholmbe/optics-scan/Scans/BTScanAll.tcl

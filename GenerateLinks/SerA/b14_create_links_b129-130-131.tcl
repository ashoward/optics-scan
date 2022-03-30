refresh_hw_device [lindex [get_hw_devices xcvu9p_0] 0]
set xil_newLinks [list]

set xil_newlink [create_hw_sio_link -description {link 0}  [lindex [get_hw_sio_txs */Quad_129/MGT_X0Y40/TX] 0] [lindex [get_hw_sio_rxs */Quad_129/MGT_X0Y41/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 1}  [lindex [get_hw_sio_txs */Quad_129/MGT_X0Y41/TX] 0] [lindex [get_hw_sio_rxs */Quad_129/MGT_X0Y40/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 2}  [lindex [get_hw_sio_txs */Quad_129/MGT_X0Y42/TX] 0] [lindex [get_hw_sio_rxs */Quad_129/MGT_X0Y43/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 3}  [lindex [get_hw_sio_txs */Quad_129/MGT_X0Y43/TX] 0] [lindex [get_hw_sio_rxs */Quad_129/MGT_X0Y42/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 4}  [lindex [get_hw_sio_txs */Quad_130/MGT_X0Y44/TX] 0] [lindex [get_hw_sio_rxs */Quad_130/MGT_X0Y45/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 5}  [lindex [get_hw_sio_txs */Quad_130/MGT_X0Y45/TX] 0] [lindex [get_hw_sio_rxs */Quad_130/MGT_X0Y44/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 6}  [lindex [get_hw_sio_txs */Quad_130/MGT_X0Y46/TX] 0] [lindex [get_hw_sio_rxs */Quad_130/MGT_X0Y47/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 7}  [lindex [get_hw_sio_txs */Quad_130/MGT_X0Y47/TX] 0] [lindex [get_hw_sio_rxs */Quad_130/MGT_X0Y46/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 8}  [lindex [get_hw_sio_txs */Quad_131/MGT_X0Y48/TX] 0] [lindex [get_hw_sio_rxs */Quad_131/MGT_X0Y49/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 9} [lindex [get_hw_sio_txs */Quad_131/MGT_X0Y49/TX] 0] [lindex [get_hw_sio_rxs */Quad_131/MGT_X0Y48/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 10} [lindex [get_hw_sio_txs */Quad_131/MGT_X0Y50/TX] 0] [lindex [get_hw_sio_rxs */Quad_131/MGT_X0Y51/RX] 0]]
#lappend xil_newLinks $xil_newLink
set xil_newlink [create_hw_sio_link -description {link 11} [lindex [get_hw_sio_txs */Quad_131/MGT_X0Y51/TX] 0] [lindex [get_hw_sio_rxs */Quad_131/MGT_X0Y50/RX] 0]]
#lappend xil_newLinks $xil_newLink

create_hw_sio_linkgroup -description {Link Group B129-130-131} [list [get_hw_sio_links {*}]]

unset xil_newLinks

set_property TX_PATTERN {PRBS 31-bit} [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
commit_hw_sio [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
set_property RX_PATTERN {PRBS 31-bit} [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
commit_hw_sio [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
commit_hw_sio [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]
commit_hw_sio [get_hw_sio_links -of_objects [get_hw_sio_linkgroups {LINKGROUP_0}]]

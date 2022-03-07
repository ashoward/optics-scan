### ### ### ### ###
###################
### ### ### ### ###

# DAQ -> socket0 only form serenity v1.2
# Tx0 -> socket1
# Rx0 -> socket2
# Tx1 -> socket3
# Rx1 -> socket4
# Tx2 -> socket5
# Rx2 -> socket6
# Tx3 -> socket7
# Rx3 -> socket8
# Tx4 -> socket9
# Rx4 -> socket10
# Tx5 -> socket11
# Rx5 -> socket12
# ext -> socket13 only from serenity v1.2

### ### ### ### ###
###################
### ### ### ### ###

package require json

# GTY and GTH "numbering"
set MGTtypeId [ dict create GTH "_1_0_50/IBERT" GTY "_1_0_0/IBERT" ]

# Set base directory of optics scan
set tclBase "/home/meholmbe/optics-scan"
# Open files
set vu7p_so1_v1_fileName "$tclBase/json/Board04/vu7p_so1_v1_connectivity.json"
# Map Tx0 to Rx0, Tx1 to Rx1, etc.
set configFileName "$tclBase/json/Board04/connections_config_vu7p_alpha.json"
# Map Tx0 to Rx11, Tx1 to Rx10, etc.
#set configFileName "$tclBase/json/connections_config_vu7p_alpha_inverted.json"


set configFileIn [open $configFileName r]
set connectivity [dict create \
                      vu7p_so1 [ ::json::json2dict [read [open $vu7p_so1_v1_fileName r] ] ] \
                      # ----->>>>> add here any configuration: e.g. VU9P and sm1_v2
                 ]

# Get data 
set configRaw [read $configFileIn]

set config [ ::json::json2dict $configRaw ]

set baseBoard     [ dict get $config BaseBoard ]
set DCs           [ dict get $config DCs ]

set hwConnections_tmp [ dict get $config hardwareConnections ]
set hwConnections [ dict create ]

dict for { key c } $hwConnections_tmp {
    dict append hwConnections $c $key
}

set JTAG          [ dict get $config JTAG ]
set JTAGid        [ dict get $JTAG JTAGid ]
set host          [ dict get $JTAG host ]

set pathBase "$host/xilinx_tcf/$JTAGid"

set connections [ dict get $config connections ]


#### Generate links

dict for { id c } $connections {
    
    set connectionType [ dict get $c connectionType ]

    set siteA           [ dict get [ dict get $c sideA ] site ]
    set connectorAlogic [ dict get [ dict get $c sideA ] connector ]
    set connectorA      [ dict get $hwConnections $connectorAlogic ]
    set daughterCardA   [ dict get $DCs $siteA ]
    set socketA         [ dict get [dict get $connectivity [dict get $daughterCardA type] ] $connectorA] 
    
    set siteB           [ dict get [ dict get $c sideB ] site ]
    set connectorBlogic [ dict get [ dict get $c sideB ] connector ]
    set connectorB      [ dict get $hwConnections $connectorBlogic ]
    set daughterCardB   [ dict get $DCs $siteB ]
    set socketBtmp      [ dict get [dict get $connectivity [dict get $daughterCardB type] ] $connectorB] 
    
    ## Invert lines on the fibre/bundle if needed
    set socketB []
    set nConnections [ dict size $socketBtmp ]
    if { $connectionType == "InvertFibre" } {
        
        for {set i [expr $nConnections-1]} {$i > -1} {incr i -1} { 
            dict set socketB $i [ dict get $socketBtmp $i ] 
        }

    } elseif { $connectionType == "Fibre" } {
        
        for {set i [expr 0]} {$i < $nConnections} {incr i} { 
            dict set socketB $i [dict get $socketBtmp $i] 
        }
    
    } else {
        
        puts "Error: Connection type not recognised: $connectionType."
        return -1
    
    } 

    ##Generate the links
    foreach {socketLineIdA A} $socketA {socketLineIdB B} $socketB {
        
        # Get the MGTs path and type
        set MGTa     [ dict get $A MGT ]
        set MGTaType [ dict get $A type ]
        set MGTb     [ dict get $B MGT ]
        set MGTbType [ dict get $B type ]

        if { $MGTa == "none" || $MGTb == "none" } {
            continue
        }

        # RX vars
        set rxMGT []
        set rxMGTtype []
        set rxSite []
        set rxConnector []
        set rxSocketLineId []
        # TX vars
        set txMGT []
        set txMGTtype []
        set txSite []
        set txConnector []
        set txSocketLineId []
        
        if { [ string first "RX" $MGTa ] != -1 && [ string first "TX" $MGTb ] != -1 } {
            # A is RX
            set rxMGT $MGTa
            set rxMGTtype $MGTaType
            set rxSite [ string map {"X" ""} $siteA ]
            set rxConnectorLogic $connectorAlogic
            set rxConnector $connectorA
            set rxSocketLineId $socketLineIdA
            # B is TX
            set txMGT $MGTb
            set txMGTtype $MGTbType
            set txSite [ string map {"X" ""} $siteB]
            set txConnectorLogic $connectorBlogic
            set txConnector $connectorB
            set txSocketLineId $socketLineIdB
        } elseif { [ string first "TX" $MGTa ] != -1 && [ string first "RX" $MGTb ] != -1 } {
            # B is RX
            set rxMGT $MGTb
            set rxMGTtype $MGTbType
            set rxSite [ string map {"X" ""} $siteB ] 
            set rxConnectorLogic $connectorBlogic
            set rxConnector $connectorB
            set rxSocketLineId $socketLineIdB
            # A is TX
            set txMGT $MGTa
            set txMGTtype $MGTaType
            set txSite [ string map {"X" ""} $siteA ]
            set txConnectorLogic $connectorAlogic
            set txConnector $connectorA
            set txSocketLineId $socketLineIdA
        
        } else {
            puts "Wrong assignment!!! Check your configuration file. Two RX or two TX are matched."
            puts "Site $siteA $MGTa"
            puts "Site $siteB $MGTb"
            return -1
        }
        

#   if { $txSocketLineId == "$argv" } {
    
    set rxDCid   [ dict get [ dict get $DCs X$rxSite ] id ]
    set rxDCtype [ dict get [ dict get $DCs X$rxSite ] type ]
    set txDCid   [ dict get [ dict get $DCs X$txSite ] id ]  
    set txDCtype [ dict get [ dict get $DCs X$txSite ] type ]
    
    set rxMGTid [dict get $MGTtypeId $rxMGTtype ]
    set txMGTid [dict get $MGTtypeId $txMGTtype ]
    
    set txPath "$pathBase/$txSite$txMGTid/$txMGT"
    set rxPath "$pathBase/$rxSite$rxMGTid/$rxMGT"
    
    set description "Link X$txSite-$txDCtype-$txDCid-$txConnectorLogic-$txSocketLineId:X$rxSite-$rxDCtype-$rxDCid-$rxConnectorLogic-$rxSocketLineId"
    puts $description
        
    # Generate the link
    puts $txPath
    puts $rxPath
    set xil_newLink [create_hw_sio_link -description $description [lindex [get_hw_sio_txs $txPath] 0] [lindex [get_hw_sio_rxs $rxPath] 0] ]
    puts $xil_newLink
    lappend xil_newLinks $xil_newLink

#   }
        
    }

    # Group links
    set groupDescription "$baseBoard-$connectionType:$siteA-$connectorAlogic<->$siteB-$connectorBlogic"
    puts $groupDescription
    set xil_newLinkGroup [create_hw_sio_linkgroup -description $groupDescription [get_hw_sio_links $xil_newLinks]]
    unset xil_newLinks

}

#### Setup links
set links [get_hw_sio_links]

foreach link $links {

    # DFE off
    #set_property RXDFEENABLED {0} [get_hw_sio_links $link]
    #set_property TXDFEENABLED {0} [get_hw_sio_links $link] - cannot work?!

    set_property LOOPBACK {none} [get_hw_sio_links $link]
    
    # PRBS set to 31 bits
    set_property TX_PATTERN {PRBS 31-bit} [get_hw_sio_links $link]
    set_property RX_PATTERN {PRBS 31-bit} [get_hw_sio_links $link]

    # Set polarity only if status is NO LINK
    set linkStatus [ get_property STATUS [get_hw_sio_links $link] ]
    if { $linkStatus == "NO LINK" } {
        set tx_polarity [ get_property PORT.TXPOLARITY $link ]
        set rx_polarity [ get_property PORT.RXPOLARITY $link ]
        if { $tx_polarity != $rx_polarity } {
            set_property PORT.RXPOLARITY {1} [get_hw_sio_links $link]
            commit_hw_sio [get_hw_sio_links $link]
        }
    }

    # Rx reset
    set_property LOGIC.RX_RESET_DATAPATH 1 [get_hw_sio_links $link]
    commit_hw_sio [get_hw_sio_links $link]
    set_property LOGIC.RX_RESET_DATAPATH 0 [get_hw_sio_links $link]
    commit_hw_sio [get_hw_sio_links $link]
    
    # Reset counters
    set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links $link]
    commit_hw_sio [get_hw_sio_links $link]
    set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links $link]
    commit_hw_sio [get_hw_sio_links $link]

}

## ALL relevant settings - beware > 500000 sweeps!!
## 500 scans per hour

## Makes scans with varying settings on the Tx path (and RxTerm but this can be changed)

###########################
# Set folder and file names

# Get the system time to name the directory
set systemTime [clock seconds]
set folderTime [clock format $systemTime -format %Y-%m-%d-%H%M]
# Output folder
set folderName "/home/luis/Projects/optics-scan/results/SerA-2_BTScan_BER_Tx_$folderTime"
# Board name
set board "xcvu9p_0"
set boardName "root@128.141.223.196"
# Paths to scripts on the board
set setEqScript "/root/optical_eval/setPre.sh"
set setAmpScript "/root/optical_eval/setAmp.sh"
set setPreEmpScript "/root/optical_eval/setPre-emp.sh"

###########################

# Which precision
#set dwell_ber 1e-8
set dwell_ber 1e-6

# Open file to store the BER and open area
set file_ber [open ./BER_summary.txt w]
puts $file_ber "Link: $argv\n"

# Generate the folders 
exec mkdir -p -- $folderName
exec mkdir -p -- $folderName/data

# Remove the current scans if any
remove_hw_sio_scan [get_hw_sio_scans {}]

# Get links 
set links [ get_hw_sio_links ]

set groups [ get_hw_sio_linkgroups ]

set config [ dict create ]


# Tx Diff/Swing [mV]
set txdiff_default_index (11000)
set txdiff_default 950
array set txdiff_setting_gty {
    (00101) 530
    (11000) 950
    (11111) 1040
}
# All possible TxDiffSwing values
    # (00000) 390
    # (00001) 430
    # (00010) 450
    # (00011) 470
    # (00100) 490
    # (00101) 530
    # (00110) 550
    # (00111) 570
    # (01000) 590
    # (01001) 630
    # (01010) 650
    # (01011) 670
    # (01100) 690
    # (01101) 730
    # (01110) 740
    # (01111) 760
    # (10000) 780
    # (10001) 820
    # (10010) 840
    # (10011) 850
    # (10100) 870
    # (10101) 900
    # (10110) 920
    # (10111) 930
    # (11000) 950 # Default
    # (11001) 970
    # (11010) 980
    # (11011) 990
    # (11100) 1000
    # (11101) 1020
    # (11110) 1030
    # (11111) 1040


# TxPrecursor [dB]
set txpre_default_index (00000)
set txpre_default 0.00
array set txpre_setting_gty {
    (00000) 0.00
    (01001) 2.21
    (01111) 4.08
}
# All possible TxPre values
#     (00000) 0.00 # Default
#     (00001) 0.22
#     (00010) 0.45
#     (00011) 0.68
#     (00100) 0.92
#     (00101) 1.16
#     (00110) 1.41
#     (00111) 1.67
#     (01000) 1.94
#     (01001) 2.21
#     (01010) 2.50
#     (01011) 2.79
#     (01100) 3.10
#     (01101) 3.41
#     (01110) 3.74
#     (01111) 4.08
#     (10000) 4.44
#     (10001) 4.81
#     (10010) 5.19
#     (10011) 5.60
#     (10100) 6.02
# What are these for...
#     (10101) 6.02
#     (10110) 6.02
#     (10111) 6.02
#     (11000) 6.02
#     (11001) 6.02
#     (11010) 6.02
#     (11011) 6.02
#     (11100) 6.02
#     (11101) 6.02
#     (11110) 6.02
#     (11111) 6.02


# TxPostcursor [dB]
set txpost_default_index (00000)
set txpost_default 0.00
array set txpost_setting_gty {
    (00000) 0.00
    (01001) 2.21
    (01111) 4.08
    (10100) 6.02
}
# All possible TxPost values
    # (00000) 0.00 # Default
    # (00001) 0.22
    # (00010) 0.45
    # (00011) 0.68
    # (00100) 0.92
    # (00101) 1.16
    # (00110) 1.41
    # (00111) 1.67
    # (01000) 1.94
    # (01001) 2.21
    # (01010) 2.50
    # (01011) 2.79
    # (01100) 3.10
    # (01101) 3.41
    # (01110) 3.74
    # (01111) 4.08
    # (10000) 4.44
    # (10001) 4.81
    # (10010) 5.19
    # (10011) 5.60
    # (10100) 6.02
    # (10101) 6.47
    # (10110) 6.94
    # (10111) 7.43
    # (11000) 7.96
    # (11001) 8.52
    # (11010) 9.12
    # (11011) 9.76
    # (11100) 10.46
    # (11101) 11.21
    # (11110) 12.04
    # (11111) 12.96


# Optical EQ on the transmitter [dB]
set txeq_default 0
array set txeq_setting {
  1 0
  2 1
  3 2
  5 4
  8 7
}
# All possible EQ values
  # 1 0
  # 2 1
  # 3 2
  # 4 3
  # 5 4
  # 6 5
  # 7 6
  # 8 7


# Termination voltage [mV]
set rxterm_default 800
array set rxterm_setting_gty {
    1  100
    6  400
    11  800
}
# All possible RxTerm values
    # 1  100
    # 2  200
    # 3  250
    # 4  330
    # 5  350
    # 6  400
    # 7  500
    # 8  550
    # 9  600
    # 10  700
    # 11  800 # Default
    # 12  850
    # 13  900
    # 14  950
    # 15  1000
    # 16  1100 


# Other default values 
set rxamp_default Medium
set rxemp_default 2
set dfe_default 0


# Set optical configurations default
# Remember to exit the Smash interactive shell, or the script will be stuck here
puts "Setting amplitude $rxamp_default..."
catch {exec -ignorestderr ssh $boardName "source $setAmpScript $rxamp_default"} rxamp_value
while { $rxamp_value == "child process exited abnormally" } {
puts "Set Amp i2c error: $rxamp_value"
catch {exec -ignorestderr ssh $boardName "source $setAmpScript $rxamp_default"} rxamp_value
}
puts "Amplitude value: $rxamp_value"

puts "Setting pre-emphasis $rxemp_default..."
catch {exec -ignorestderr ssh $boardName "source $setPreEmpScript $rxemp_default"} rxemp_value
while { $rxemp_value == "child process exited abnormally" } {
puts "Set Pre-Emp i2c error: $rxemp_value"
catch {exec -ignorestderr ssh $boardName "source $setPreEmpScript $rxemp_default"} rxemp_value
}
puts "Pre-emphasis value: $rxemp_value"


# Start loop over values
set i 0
set sweep 0
foreach group $groups {

  set groupName [get_property DESCRIPTION $group]
  set tmp [ lindex [split $groupName ":"] 0 ]
  set baseBoard [ lindex [ split $tmp "-" ] 0 ]
  set connectionType [ lindex [ split $tmp "-" ] 1 ]
  #set site [ lindex [ split $tmp "_" ] 1 ]
  #set DC [ lindex [ split $tmp "_" ] 2 ]
  set links [get_hw_sio_links -of_objects [get_hw_sio_linkgroups $group]]

  # Loop over Tx Equalisation
  foreach index_eq [array names txeq_setting] {

    puts "Setting equalization to $txeq_setting($index_eq)..."
    catch {exec -ignorestderr ssh $boardName "source $setEqScript $txeq_setting($index_eq)"} txeq_value
    while { $txeq_value == "child process exited abnormally" } {
      puts "Set EQ i2c error: $txeq_value"
      catch {exec -ignorestderr ssh $boardName "source $setEqScript $txeq_setting($index_eq)"} txeq_value
    }
    puts "Equalization value: $txeq_value"

    # Loop over Tx DiffSwing
    foreach index_diff [array names txdiff_setting_gty] {
      # Loop over Tx Precursor
      foreach index_pre [array names txpre_setting_gty] {
        # Loop over Tx Postcursor
        foreach index_post [array names txpost_setting_gty] {
          # Loop over Rx Termination voltage
          foreach index_rxterm [array names rxterm_setting_gty] { 
            # Loop over LPM and DFE filters [list 0 1]
            foreach dfe [list 0] {
              # Loop over all links
              foreach link $links {

                after 3000 

                # Set DFE on or off:
                set_property RXDFEENABLED $dfe [get_hw_sio_links $link]
                puts "DFE: $dfe"

                # PRBS set to 31 bits
                set_property TX_PATTERN "PRBS 31-bit" [get_hw_sio_links $link]
                set_property RX_PATTERN "PRBS 31-bit" [get_hw_sio_links $link]

                # Set datawidths
                set rx_datawidth [get_property RX_DATA_WIDTH [get_hw_sio_links $link] ]
                set tx_datawidth [get_property TX_DATA_WIDTH [get_hw_sio_links $link] ]
                puts "TX datawidthvalue value: $tx_datawidth"
                puts "RX datawidthvalue value: $rx_datawidth"

                # Set RX term
                set_property RXTERM "$rxterm_setting_gty($index_rxterm) mV" [get_hw_sio_links $link]
                puts "RXTERM: $rxterm_setting_gty($index_rxterm)"

                # Set TX pre/post
                set_property TXDIFFSWING "$txdiff_setting_gty($index_diff) mV $index_diff" [get_hw_sio_links $link]
                set_property TXPRE "$txpre_setting_gty($index_pre) dB $index_pre" [get_hw_sio_links $link]
                set_property TXPOST "$txpost_setting_gty($index_post) dB $index_post" [get_hw_sio_links $link]
                puts "TXPDIFFSWING : $txdiff_setting_gty($index_diff)"
                puts "TXPRE : $txpre_setting_gty($index_pre)"
                puts "TXPOST: $txpost_setting_gty($index_post)"

                puts "TXEQ: $txeq_setting($index_eq)"

                # RX reset
                set_property LOGIC.RX_RESET_DATAPATH 1 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]
                set_property LOGIC.RX_RESET_DATAPATH 0 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]
                # TX reset
                set_property LOGIC.TX_RESET_DATAPATH 1 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]
                set_property LOGIC.TX_RESET_DATAPATH 0 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]

                # Reset counters
                set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]
                set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]

                # Define scan name from link name
                set linkName [get_property DESCRIPTION $link]
                if { $dfe == "0" } {
                  set DFE lpm
                } else {
                  set DFE dfe
                }

                set scanName "$DFE TXDIFF-$txdiff_setting_gty($index_diff) TXPOST-$txpost_setting_gty($index_post) TXPRE-$txpre_setting_gty($index_pre) TXEQ-$txeq_setting($index_eq) RXTERM-$rxterm_setting_gty($index_rxterm)Scan $groupName $linkName"

                # Get the DCs info
                set linkName [ lindex [ split $linkName " " ] 1 ]
                set tx [ lindex [ split $linkName ":" ] 0 ]
                set rx [ lindex [ split $linkName ":" ] 1 ]
                set DCtx [ dict create site [lindex [ split $tx "-"] 0 ] type [lindex [ split $tx "-"] 1 ] id [lindex [ split $tx "-"] 2 ] ]
                set DCrx [ dict create site [lindex [ split $rx "-"] 0 ] type [lindex [ split $rx "-"] 1 ] id [lindex [ split $rx "-"] 2 ] ]

                # The site is the TX site
                set site [ dict get $DCtx site ]

                # Get all qplls and their status
                set QPLLs [ get_hw_sio_plls -of_objects [ get_hw_sio_commons -of_objects [ get_hw_sio_gtgroup -of_objects [ get_hw_sio_gts -of_objects [get_hw_sio_links $link] ] ] ] ]

                set PLL0status [get_property STATUS [lindex $QPLLs 0] ]
                set PLL1status [get_property STATUS [lindex $QPLLs 1] ]

                set txEndpoint [ get_property TX_ENDPOINT $link ]
                set tx [ get_property TX_ENDPOINT $link ]
                set rxEndpoint [ get_property RX_ENDPOINT $link ]

                # Do not scan if pll is not locked, report it instead
                if { $PLL0status == "NOT LOCKED" } {
                  puts "WARNING wrong PLL status ($scanName): PLL0 is $PLL0status, PLL1 is $PLL1status"
                  set error_count none
                  set open_area none
                } else {
                  set xil_newScan [create_hw_sio_scan -description $scanName  1d_bathtub  [lindex [get_hw_sio_links $link] ] ]
                  set_property HORIZONTAL_INCREMENT {1} [get_hw_sio_scans $xil_newScan]
                  set_property DWELL_BER $dwell_ber [get_hw_sio_scans $xil_newScan]

                  # Run the bathtub scan! :) 
                  run_hw_sio_scan [get_hw_sio_scans $xil_newScan]
                  wait_on_hw_sio_scan [get_hw_sio_scans $xil_newScan]

                  puts "Scan finished for $link"
                  puts $scanName

                  set hex_error_count [get_property LOGIC.ERRBIT_COUNT [get_hw_sio_links $link] ]
                  set error_count [expr 0x$hex_error_count]
                  set received_bits [ get_property RX_RECEIVED_BIT_COUNT [get_hw_sio_links $link] ]
                  set open_area_int [get_property Open_Area [get_hw_sio_scans $xil_newScan] ]
                  set open_area [expr 100*$open_area_int/64.0]

                  puts "Error_count (after bathtub): $error_count"
                  puts "Received bits (after bathtub): $received_bits"
                  puts "Open Area: $open_area"

                  # Save the scan! :D
                  exec mkdir -p -- $folderName/data/sweep$sweep
                  write_hw_sio_scan -force "$folderName/data/sweep${sweep}/$scanName" [get_hw_sio_scans $xil_newScan]
                }

                set status    [ get_property STATUS      $link ]
                set tx_pattern  [ get_property TX_PATTERN    $link ]
                set rx_pattern  [ get_property RX_PATTERN    $link ]
                set tx_polarity [ get_property PORT.TXPOLARITY $link ]
                set rx_polarity [ get_property PORT.RXPOLARITY $link ]
                set DFE_enabled [ get_property RXDFEENABLED  $link ]

                # Measure BER and error count
                # Do it after the bathtub scan or one get an "incorrect" error count
                refresh_hw_device -update_hw_probes false [lindex [get_hw_devices $board] 0] 
                set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]
                set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links $link]
                commit_hw_sio [get_hw_sio_links $link]

                set received_bits [ get_property RX_RECEIVED_BIT_COUNT [get_hw_sio_links $link] ] 
                set hex_error_count [ get_property LOGIC.ERRBIT_COUNT [get_hw_sio_links $link] ]
                set rx_ber [ get_property RX_BER [get_hw_sio_links $link] ]
                set error_count [expr 0x$hex_error_count]

                puts "Received bits: $received_bits"
                puts "Error count: $error_count"
                puts "BER: $rx_ber"

                # Write BER file
                set text ""
                append text "$scanName : \n"
                append text "txDiff: $txdiff_setting_gty($index_diff)\n"
                append text "txPre : $txpre_setting_gty($index_pre)\n"
                append text "txPost: $txpost_setting_gty($index_post)\n"
                append text "txEq  : $txeq_setting($index_eq)\n"
                append text "rxTerm: $rxterm_setting_gty($index_rxterm)\n"
                append text "Bits  : $received_bits\n"
                append text "Errors: $error_count\n"
                append text "BER   : $rx_ber\n"
                append text "OpenA : $open_area\n"
                append text "DFE   : $DFE\n"

                puts $file_ber $text

                incr i
              }
            incr sweep
            }
          }
        }
      }
    }
  }

  # Reset values to default
  foreach link $links {
    set_property TXPRE "$txpre_default dB $txpre_default_index" [get_hw_sio_links $link]
    set_property TXPOST "$txpost_default dB $txpost_default_index" [get_hw_sio_links $link]
    set_property TXDIFFSWING "$txdiff_default mV $txdiff_default_index" [get_hw_sio_links $link]

    set_property RXDFEENABLED $dfe_default [get_hw_sio_links $link]
    set_property RXTERM "$rxterm_default mV" [get_hw_sio_links $link]
  }
  # Set optical configurations default
  # Remember to exit the Smash interactive shell, or the script will be stuck here
  puts "Setting equalization $txeq_default..."
  catch {exec -ignorestderr ssh $boardName "source $setEqScript $txeq_default"} txeq_value
  while { $txeq_value == "child process exited abnormally" } {
  puts "Set EQ i2c error: $txeq_value"
  catch {exec -ignorestderr ssh $boardName "source $setEqScript $txeq_default"} txeq_value
  }
  puts "Equalization value: $txeq_value"

}

# Close and move BER summary
close $file_ber
exec mv ./BER_summary.txt $folderName

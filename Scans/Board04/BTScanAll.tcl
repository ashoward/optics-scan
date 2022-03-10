## ALL relevant settings - beware > 500000 sweeps!!
## 500 scans per hour

### Which precision ###

##set dwell_ber 1e-8
set dwell_ber 1e-6

#######################

# Remove the current scans if any
remove_hw_sio_scan [get_hw_sio_scans {}]

# Get the system time to name the directory
set systemTime [clock seconds]
 
set folderName [clock format $systemTime -format %Y_%m_%d_%H%M-%S]
set folderName "/home/meholmbe/optics-scan/results/Board04-$folderName-all"

# Generate the folders 
exec mkdir -p -- $folderName
exec mkdir -p -- $folderName/data
exec mkdir -p -- $folderName/data/best

# Open file to store the configuration 
set fout [open ./configuration_summary.json w]
puts $fout "{"
# Open file to store the best configuration
set fbest [open ./best_area_summary.json w]
puts $fbest "{"
set fbest_err [open ./best_errors_summary.json w]
puts $fbest_err "{"
# Open file to store the BER
set fber [open ./BER_summary.txt w]
puts $fber "Link: $argv\n"

# Get links 
set links [ get_hw_sio_links ]

set groups [ get_hw_sio_linkgroups ]

set config [ dict create ]


# Tx Diff/Swing [mV]
set txdiff_default_key (11000)
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


# TxPre [dB]
set txpre_default_key (00000)
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


# TxPost [dB]
set txpost_default_key (00000)
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
set txeq_default None
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
catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setAmp.sh $rxamp_default"} rxamp_value
while { $rxamp_value == "child process exited abnormally" } {
puts "Set Amp i2c error: $rxamp_value"
catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setAmp.sh $rxamp_default"} rxamp_value
}
puts "Amplitude value: $rxamp_value"

puts "Setting pre-emphasis $rxemp_default..."
catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setPre-emp.sh $rxemp_default"} rxemp_value
while { $rxemp_value == "child process exited abnormally" } {
puts "Set Pre-Emp i2c error: $rxemp_value"
catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setPre-emp.sh $rxemp_default"} rxemp_value
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

  foreach link $links {
    # Best Open Area
    set best_area($link) -1
    set best_errors($link) 999999999999
    set best_txdiff($link) -1
    set best_txdiff_index($link) -1
    set best_txpre($link) -1
    set best_txpre_index($link) -1
    set best_txpost($link) -1
    set best_txpost_index($link) -1
    set best_txeq($link) -1
    set best_dfe($link) unset
    set best_scanName($link) unset
    set best_xil_newScan($link) unset
    # Best Error Count
    set best_err_area($link) -1
    set best_err_errors($link) 999999999999
    set best_err_txdiff($link) -1
    set best_err_txdiff_index($link) -1
    set best_err_txpre($link) -1
    set best_err_txpre_index($link) -1
    set best_err_txpost($link) -1
    set best_err_txpost_index($link) -1
    set best_err_txeq($link) -1
    set best_err_dfe($link) unset
    set best_err_xil_newScan($link) unset
    set best_err_scanName($link) unset
    set best_err_cfg($link) unset
  }

  foreach index_eq [array names txeq_setting] {

    # Set optical equalisation on transmitter
    # Remember to exit the Smash interactive shell, or the script will be stuck here
    puts "Setting equalization to $txeq_setting($index_eq)..."
    catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setPre.sh $txeq_setting($index_eq)"} txeq_settingue
    while { $txeq_settingue == "child process exited abnormally" } {
      puts "Set EQ i2c error: $txeq_settingue"
      catch {exec -ignorestderr ssh cmx@serenity-2368-04-i5.cern.ch "source ahoward/picocom/setPre.sh $txeq_setting($index_eq)"} txeq_settingue
    }
    puts "Equalization value: $txeq_settingue"

    foreach index_diff [array names txdiff_setting_gty] {
      foreach index_pre [array names txpre_setting_gty] {
        foreach index_post [array names txpost_setting_gty] {
          foreach index_rxterm [array names rxterm_setting_gty] { 
            # Loop over LPM and DFE filters [list 0 1]
            foreach dfe [list 0] {
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

                set scanName "$DFE RXTERM-$rxterm_setting_gty($index_rxterm) TXDIFF-$txdiff_setting_gty($index_diff) TXPOST-$txpost_setting_gty($index_post) TXPRE-$txpre_setting_gty($index_pre) TXEQ-$txeq_setting($index_eq) Scan $groupName $linkName"

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

                  # Run the scan! :) 
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
                  puts "Received bits: $received_bits"
                  puts "Open Area: $open_area"
                  puts "Best Area: $best_area($link)"

                  # The best Open Area
                  if { $open_area > $best_area($link)} {
                    set best_area($link) $open_area
                    set best_errors($link) $error_count
                    set best_dfe($link) [ get_property RXDFEENABLED  $link ]
                    set best_txdiff($link) $txdiff_setting_gty($index_diff)
                    set best_txpre($link) $txpre_setting_gty($index_pre)
                    set best_txpost($link) $txpost_setting_gty($index_post)
                    set best_txdiff_index($link) $txdiff_setting_gty($index_diff)
                    set best_txpre_index($link) $index_pre
                    set best_txpost_index($link) $index_post
                    set best_rxterm($link) $rxterm_setting_gty($index_rxterm)
                    set best_txeq($link) $txeq_setting($index_eq)
                    set best_scanName($link) $scanName
                    set best_xil_newScan($link) $xil_newScan
                  }

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

                # Write configuration to out file
                set text ""

                if { $i > 0 } {
                  append text "\},\n"
                }

                append text "\"$scanName\" : \{\n"
                append text "\"baseBoard\" : \"$baseBoard\",\n"

                append text "\"DCtx\" : \{ "
                append text "\"site\" : \""
                append text [ dict get $DCtx site ]
                append text "\", \"type\" : \""
                append text [ dict get $DCtx type ]
                append text "\", \"id\" : \""
                append text [ dict get $DCtx id ]
                append text "\" \},\n"

                append text "\"DCrx\" : \{ "
                append text "\"site\" : \""
                append text [ dict get $DCrx site ]
                append text "\", \"type\" : \""
                append text [ dict get $DCrx type ]
                append text "\", \"id\" : \""
                append text [ dict get $DCrx id ]
                append text "\" \},\n"

                append text "\"status\" : \"$status\", \n"
                append text "\"DFE\" : \"$DFE_enabled\", \n"
                append text "\"tx\" : \"$txEndpoint\",\n" 
                append text "\"txPolarity\" : \"$tx_polarity\", \n"
                append text "\"txPattern\" : \"$tx_pattern\", \n"
                append text "\"rx\" : \"$rxEndpoint\", \n"
                append text "\"rxPolarity\" : \"$rx_polarity\", \n"
                append text "\"rxPattern\" : \"$rx_pattern\", \n"

                append text "\"txEq\" : \"$txeq_setting($index_eq)\", \n"
                append text "\"txDiff\" : \"$txdiff_setting_gty($index_diff)\", \n"
                append text "\"txPre\" : \"$txpre_setting_gty($index_pre)\", \n"
                append text "\"txPost\" : \"$txpost_setting_gty($index_post)\", \n"

                append text "\"rxTerm\" : \"$rxterm_setting_gty($index_rxterm)\", \n"

                append text "\"OpenArea\" : \"$open_area\", \n"
                append text "\"ErrorCount\" : \"$error_count\" \n"

                puts $fout $text

                # Measure errors
                # Do it after the bathtub scan or one get an "incorrect" error count
                refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcvu7p_0] 0] 
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

                # The best Error Count and open area
                # Add within 3%?
                if { $error_count < $best_err_errors($link) || ($error_count == $best_err_errors($link) && $open_area > $best_err_area($link))} {
                  set best_err_area($link) $open_area
                  set best_err_errors($link) $error_count
                  set best_err_dfe($link) [ get_property RXDFEENABLED  $link ]
                  set best_err_txdiff($link) $txdiff_setting_gty($index_diff)
                  set best_err_txpre($link) $txpre_setting_gty($index_pre)
                  set best_err_txpost($link) $txpost_setting_gty($index_post)
                  set best_err_rxterm($link) $rxterm_setting_gty($index_rxterm)
                  set best_err_txdiff_index($link) $index_diff
                  set best_err_txpre_index($link) $index_pre
                  set best_err_txpost_index($link) $index_post
                  set best_err_txeq($link) $txeq_setting($index_eq)
                  set best_err_scanName($link) $scanName
                  set best_err_xil_newScan($link) $xil_newScan
                  # Reset best configuration list and save the better one
                  set best_err_cfg($link) {}
                  set best_err_cfg($link) "($txdiff_setting_gty($index_diff),$txpre_setting_gty($index_pre),$txpost_setting_gty($index_post),$rxterm_setting_gty($index_rxterm),$txeq_setting($index_eq))"
                } elseif {$error_count == $best_err_errors($link) && $open_area == $best_err_area($link)} {
                  # Save configuration as it gave the same result as the current best
                  lappend best_err_cfg($link) "($txdiff_setting_gty($index_diff),$txpre_setting_gty($index_pre),$txpost_setting_gty($index_post),$rxterm_setting_gty($index_rxterm),$txeq_setting($index_eq))"
                }

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

                puts $fber $text

                incr i
              }
            incr sweep
            }
          }
        }
      }
    }
  }

  # The best configurations
  set j 0
  foreach link $links {

    set linkName [get_property DESCRIPTION $link]

    # Best Open Area
    set text ""
    if { $j > 0 } {
      append text "\},\n"
    }
    append text "\"$link\" : \{\n"
    append text "\"LinkName: \"$linkName\", \n"
    append text "\"ScanName: \"$best_scanName($link)\", \n"
    append text "\"BestArea\" : \"$best_area($link)\", \n"
    append text "\"Errors\" : \"$best_errors($link)\", \n"
    append text "\"txDiff\" : \"$best_txdiff($link)\", \n"
    append text "\"txPre\" : \"$best_txpre($link)\", \n"
    append text "\"txPost\" : \"$best_txpost($link)\", \n"
    append text "\"rxTerm\" : \"$best_rxterm($link)\", \n"
    append text "\"DFE\" : \"$best_dfe($link)\", \n"

    puts $fbest $text

    # Save best scan
    write_hw_sio_scan -force "$folderName/data/best_area/$scanName" [get_hw_sio_scans $best_xil_newScan($link)]

    # Best Error Count
    set text ""
    if { $j > 0 } {
      append text "\},\n"
    }
    append text "\"$link\" : \{\n"
    append text "\"LinkName: \"$linkName\", \n"
    append text "\"ScanName: \"$best_err_scanName($link)\", \n"
    append text "\"BestArea\" : \"$best_err_area($link)\", \n"
    append text "\"Errors\" : \"$best_err_errors($link)\", \n"
    append text "\"DFE\" : \"$best_err_dfe($link)\", \n"
    append text "\"txDiff,txPre,txPost,rxTerm,txEq\" : \[$best_err_cfg($link)\], \n"
    puts $fbest_err $text

    # Save one of the best scans...
    write_hw_sio_scan -force "$folderName/data/best_errors/$scanName" [get_hw_sio_scans $best_err_xil_newScan($link)]

    # Set one of the best configurations
    set_property TXPRE "$best_err_txpre($link) dB $best_err_txpre_index($link)" [get_hw_sio_links $link]
    set_property TXPOST "$best_err_txpost($link) dB $best_err_txpost_index($link)" [get_hw_sio_links $link]
    # Add the other values as well?

    incr j
  }

  # Reset values to default
  foreach link $links {
    set_property TXPRE "$txpre_setting_gty($txpre_default_key) dB $txpre_default_key" [get_hw_sio_links $link]
    set_property TXPOST "$txpost_setting_gty($txpost_default_key) dB $txpost_default_key" [get_hw_sio_links $link]
    set_property TXDIFFSWING "$txdiff_setting_gty($txdiff_default_key) mV $txdiff_default_key" [get_hw_sio_links $link]

    set_property RXDFEENABLED $dfe_default [get_hw_sio_links $link]
    set_property RXTERM "$rxterm_default mV" [get_hw_sio_links $link]
  }
  # Set optical configurations default
  # Remember to exit the Smash interactive shell, or the script will be stuck here
  puts "Setting equalization $txeq_default..."
  catch {exec -ignorestderr ssh cmx@serenity-2368-03-i5.cern.ch "source /home/cmx/ahoward/bin/setEq.sh $txeq_default"} txeq_value
  while { $txeq_value == "child process exited abnormally" } {
  puts "Set EQ i2c error: $txeq_value"
  catch {exec -ignorestderr ssh cmx@serenity-2368-03-i5.cern.ch "source /home/cmx/ahoward/bin/setEq.sh $txeq_default"} txeq_value
  }
  puts "Equalization value: $txeq_value"

}

puts $fout "\}"
puts $fout "\}"
close $fout

puts $fbest "\}"
puts $fbest "\}"
close $fbest

puts $fbest_err "\}"
puts $fbest_err "\}"
close $fbest_err

close $fber

exec mv ./configuration_summary.json $folderName
exec mv ./best_area_summary.json $folderName
exec mv ./best_errors_summary.json $folderName
exec mv ./BER_summary.txt $folderName

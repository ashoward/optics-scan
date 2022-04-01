# Optics Scan

Scripts and files for testing and scanning the optical links on Serenity.

## Contents of Repository

- `Batch/` scripts for running the scans in Vivado batch mode. Currently the scripts does not program the device, thus this must be done interactively.
- `BitFiles/` files for programming the device.
- `GenerateLinks/` scripts for generating the links. It is possible to change which `json` configuration file to load to change the order of the links.
- `Scans/` scripts for running the actual scans.
- `json/` configuration files, e.g. for generating the links.
- `results/` contains data and plots for some of the scans. See `results/README.md` for more information.
- `plotting_script.py` script that uses the results from the scans to create plots.

## Setup

Clone this repo into the machine, with Vivado installed, you want to run the scans from if it is not already there:

    git clone git@github.com:meisonlikesicecream/optics-scan.git
    cd optics-scan/

#### On the Serenity Board

Before running the scans, SSH into the Serenity board and set it up:

    source setup_320_biFF.sh # For board 03
    source setup_320_alpha.sh # For board 04
    

This will enter SMASH in interactive mode at the end. To run the `Scans/BTScanAll.tcl`, or any other script that includes SSHing to the board to modify settings using SMASH, make sure to exit SMASH interacative mode (escape key) before running the script or it will get stuck. Also, make sure to have an SSH key set up on the board to avoid the password.

When done with the scans, power off something by doing (probably a quicker way to do this):

    smash -i # To enter interactive mode
    X0:Power Off

#### On the Computer

Start Vivado and open Hardware Manager. In the Hardware Menu to the left, press the Auto Link button (looks like two sideways Y's) to get a list of all the connected devices. For board 03 (board 04), right-click on `Digilent/210249A847C1` (`Xilinx/00000000000000`) and press Open Target. This will close any other devices that might be open. Once the desired device open, right-click on the FPGA ku15p (xcvu7p) and press Program Device to run a bitstream file from the `BitFiles/` folder. In the top menu, go to Tools, and then to Run Tcl Script. Then, run a script to generate the links from the `GenerateLinks/` folder. Links should be listed in the Serial I/O Links tab. Everything is now set up to run the scans.

## Run Scans

Make sure the steps in Setup has been made. The final results will be written to a `results/` folder. It will save information about all the bathtub scans, where a summary can be found in `configuration_summary.json`. Information about the bit rate error (BER) of every scan can be found in `BER_summary.txt`. For easier comparison, the `best_area_summary.json` saves one value with the best open area from the bathtub scan (Note: doesn't save multiple values if other settings give the same open area). All the settings with the largest open area that gives the lowest errors, are saved in `best_error_summary.json`.

### Run Interactively

In the top menu in Vivado Hardware Manager, go to Tools, and to Run Tcl Script. Choose the desired script from the `Scans/` folder.

### Run in Batch Mode

In the terminal, type

    vivado -mode batch -source Batch/batch-scan-all.tcl

## Plot Results

Plotting script can plot histograms of e.g. the open area, error count, and number of good links, for each configuration in histograms. It can also use tSNE to plot the multi-dimensional configuration/results space into a two-dimensional scatter plot. Example of how to run

    python3 plotting_script.py -i results/<DIRECTORY_NAME> -p "Board 4 (12 Ch)" -tx

Specifying the plot titles with the `-p` flag is a requirement. One must also specify which plots to create: `-tsne`, `-tx`, `-txinv`, `-rx`. 
The default output directory for the plots is within the input directory, but this can be changed with the `-o` flag. 
It is also possible to set the open area cut using the `--open_area` flag.

## Setup with SerA

### in the ZynqMP
0. ssh to ZynqMP `ssh root@128.141.223.196` and reset FF `./optical_eval/reset_ff.sh` 
1. `./optical_eval/configure_clocks.sh` # for SerA board to configure the clocks before configuring the FPGA
### in the Host PC
2. start vivado at the root of the optics-scan project. 
3. in vivado TCL run `source ./BitFiles/SerA/configure_device.tcl` to configure the FPGA, the cable should be `/Xilinx/000015de453601`
4. in vivado TCL run `source ./GenerateLinks/SerA/b14_create_links_b129-130-131.tcl` to create the links 
5. in vivado `source ./Scans/SerA-2/SerA-2-BTScan-BER-Tx.tcl` to run the scans
6. run the plot script

## Measurements Log

| Board   | Firefly                             | Folder Name                            | type of measurement |
|---------|-------------------------------------|----------------------------------------|---------------------|
| Board04 | IC May2021 "Alex's Fav" "Alpha2-V2" | Board04_BTScan_BER_Tx_2022-03-10-1447  | TX scan             |
| Board04 | IC May2021 "Alex's Fav" "Alpha2-V2" | Board04_BTScan_BER_All_2022-03-12-1920 | RX scan             |
| SerA    | IC May2021 "Alex's Fav" "Alpha2-V2" | SerA-2_BTScan_BER_Tx_2022-03-29-1009   | TX scan             |
| SerA    | IC May2021 "Alex's Fav" "Alpha2-V2" | SerA-2_BTScan_BER_All_2022-03-30-1215  | RX scan             |
| SerA    | IC May2021 "Alex's Fav" "Alpha2-V2" | SerA-2_BTScan_BER_All_2022-03-30-1807  | RX scan txpost 4dB  |
| Board04 | KIT Sept2021                        | Board04_BTScan_BER_Tx_2022-03-28-1728  | TX scan             |
| Board04 | KIT Sept2021                        | Board04_BTScan_BER_All_2022-03-30-0116 | RX scan             |
| SerA    | KIT Sept2021                        | SerA-2_BTScan_BER_Tx_2022-03-30-2341   | TX scan             |
| SerA    | KIT Sept2021                        | SerA-2_BTScan_BER_All_2022-03-XX       | RX scan             |
| Board04 | KIT May2021                         | Board04_BTScan_BER_Tx_2022-03-XX       | TX scan             |
| Board04 | KIT May2021                         | Board04_BTScan_BER_All_2022-03-XX      | RX scan             |
| SerA    | KIT May2021                         | SerA-2_BTScan_BER_Tx_2022-03-XX        | TX scan             |
| SerA    | KIT May2021                         | SerA-2_BTScan_BER_All_2022-03-XX       | RX scan             |

## Useful Links

1. [Serenity Documentation](https://serenity.web.cern.ch/serenity/)
2. [SMASH Documentation](https://serenity.web.cern.ch/serenity/smash/)

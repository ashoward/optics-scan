# Optics Scan

Scripts and files for testing and scanning the optical links on Serenity.

## Contents of Repository

- `Batch/` scripts for running the scans in Vivado batch mode. Currently the scripts does not program the device, thus this must be done interactively.
- `BitFiles/` files for programming the device.
- `GenerateLinks/` scripts for generating the links. It is possible to change which configuration file to load to change the order of the links.
- `Scans/` scripts for running the actual scans.
- `json/` configuration files, e.g. for generating the links.

## Setup

Clone this repo into the machine, with Vivado installed, you want to run the scans from if it is not already there

    git clone git@github.com:meisonlikesicecream/optics-scan.git
    cd optics-scan/

#### On the Serenity Board

Before running the scans, SSH into the Serenity board and power it on:

    source setup_320_alpha.sh

This will enter SMASH in interactive mode. To run the `Scans/BTScanAll.tcl`, or any other script that includes SSHing to the board to modify settings using SMASH, make sure to exit SMASH interacative mode (escape key) before running the script, or it will get stuck. Also, make sure to have an SSH key set up on the board to avoid the password.

When done with the scans, power off something by doing (probably a quicker way to do this):

    smash -i # To enter interactive mode
    X0:Power Off

#### On the Computer

Start Vivado and open Hardware Manager. In the Hardware Menu to the left, press the Auto Link button (looks like two sideways Y's) to get a list of all the connected devices. Right-click on the one with all the 0s and press Open Target. This will close any other devices that might be open. Once the desired device open, right-click on the FPGA xcvu7p and press Program Device to run a bitstream file from the `BitFiles/` folder. In the top menu, go to Tools, and to Run Tcl Script. Then run a script to generate the links from the `GenerateLinks/` folder. Links should be listed in the Serial I/O Links tab. Everything is now set up to run the scans.

## Run Scans

Make sure the steps in Setup has been made. The final results will be written to a `results/` folder.

### Run Interactively

In the top menu in Vivado Hardware Manager, go to Tools, and to Run Tcl Script. Choose the desired script from the `Scans/` folder.

### Run in Batch Mode

In the terminal, type

    vivado -mode batch -source Batch/batch-scan-all.tcl

## Useful Links

1. [Serenity Documentation](https://serenity.web.cern.ch/serenity/)
2. [SMASH Documentation](https://serenity.web.cern.ch/serenity/smash/)

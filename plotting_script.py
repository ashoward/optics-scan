#!/usr/bin/env python3
import os
import sys
import argparse

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.manifold import TSNE
import numpy as np
import seaborn as sns

# Argument parser
parser = argparse.ArgumentParser(description="Reads scan data and makes plots.", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-i", "--inputDir", nargs="+", help="Directory to the scan results with the BER_summary.txt file. Multiple directories possible, but not really used...", required=True)
parser.add_argument("-o", "--outputDir", default=None, help="Name of output directory. Defaults to input directory.")
parser.add_argument("-b", "--board", default=None, help="Board number, e.g. 04.", required=True)
parser.add_argument("--open_area", default=30, help="Open area cut in \%.")
parser.add_argument("-tsne", action='store_true', help="Plot tSNE.")
parser.add_argument("-test", action='store_true', help="Plot single link test.")
parser.add_argument("-tx", action='store_true', help="Plot all Tx.")
parser.add_argument("-txinv", action='store_true', help="Plot all Tx inverted links.")
parser.add_argument("-rx", action='store_true', help="Plot all Rx.")
parser.add_argument("-all", action='store_true', help="Make separate plots for all links.")
args = parser.parse_args()

# Create list of input files. Only used for tSNE plots
input_list = [dir+"/BER_summary.txt" for dir in args.inputDir]

# Create output directory
if not args.outputDir:
    args.outputDir = args.inputDir[0] + "/plots" # Just take the first input directory...
args.outputDir += "/"
if not os.path.exists(args.outputDir):
    os.makedirs(args.outputDir)


# Help functions

# Converts long numerical values to a string with 3 numbers and a prefix, e.g. 3 millions becomes 3M
def convert_int_prefix(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


# Class that is amazing
class AmazingClassName():

    def __init__(self, file_list, output_dir="./", board=None, openarea_cut=30):

        # Set input parameters
        self.file_list = file_list
        self.output_dir = output_dir
        self.board = board
        self.openarea_cut = openarea_cut

        # Set board specific values
        if self.board == "03":
            self.channels = "4+4 Ch" # Number of channels, used for plot titles
        elif self.board == "04":
            self.channels = "12 Ch" # Number of channels, used for plot titles
        elif self.board == "HNZN":
            self.channels = "12+12 Ch" # Number of channels, used for plot titles
        else:
            print("Warning: undefined board, no channels specified. Used for plot titles.")
            self.channels = ""

        # TSNE training settings
        self.perplexity = 150
        self.n_iter = 1000
        self.learning_rate = 200

        # Names of the columns for dataframe, same as the values in BER_summary.txt
        self.column_names = ["Link", "txDiff", "txPre", "txPost", "rxTerm", "txEq", "rxAmp", "rxEmp", "Bits", "Errors", "BER", "OpenA"]

        # Stuff we will fill
        self.df = pd.DataFrame(columns = self.column_names) # Dataframe with all the results from the input files
        self.link_dict = {} # Dictionary of links and their corresponding value

        # Read BER Files
        self.readBERFile()

        # Count number of bins we need
        self.nTxPre_vals = self.df["txPre"].nunique()
        self.nTxPost_vals = self.df["txPost"].nunique()
        self.nTxDiff_vals = self.df["txDiff"].nunique()
        self.nTxEq_vals = self.df["txEq"].nunique()
        self.nRxTerm_vals = self.df["rxTerm"].nunique()
        self.nRxAmp_vals = self.df["rxAmp"].nunique()
        self.nRxEmp_vals = self.df["rxEmp"].nunique()

        # Dictionary of unique values
        self.txPre_vals = {sorted(self.df["txPre"].unique())[i] : i for i in range(self.nTxPre_vals)}
        self.txPost_vals = {sorted(self.df["txPost"].unique())[i] : i for i in range(self.nTxPost_vals)}
        self.txDiff_vals = {sorted(self.df["txDiff"].unique())[i] : i for i in range(self.nTxDiff_vals)}
        self.txEq_vals = {sorted(self.df["txEq"].unique())[i] : i for i in range(self.nTxEq_vals)}
        self.rxTerm_vals = {sorted(self.df["rxTerm"].unique())[i] : i for i in range(self.nRxTerm_vals)}
        self.rxEmp_vals = {sorted(self.df["rxEmp"].unique())[i] : i for i in range(self.nRxEmp_vals)}
        # Some rxAmp settings are strings like "Low/Medium/High/Off" thus don't sort it, and remove Off
        if all(isinstance(x, float) for x in self.df["rxAmp"].unique()):
            self.rxAmp_vals = {sorted(self.df["rxAmp"].unique())[i] : i for i in range(self.nRxAmp_vals)}
        else:
            # Remove any "Off" settings
            if "Off" in self.df["rxAmp"].unique():
                self.df.drop(self.df[self.df.rxAmp == "Off"].index, inplace=True)
                self.nRxAmp_vals -= 1 if self.nRxAmp_vals > 1 else 0
                self.df.reset_index(inplace=True, drop=True)
            # Add the strings to the value dictionary
            rxAmp_list = ["Low", "Medium", "High"] # Hardcoded bodge to keep this specific order
            self.rxAmp_vals = {}
            i = 0
            for val in rxAmp_list:
                if val in self.df["rxAmp"].unique():
                    self.rxAmp_vals[val] = i
                    i += 1

        # Make new dictionaries of arrays which will correspond to our Tx histogram of values
        self.openA_tx_dict = { rxTerm : {link : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for link in self.link_dict.keys()} for rxTerm in self.rxTerm_vals.keys()}
        self.error_tx_dict = { rxTerm : {link : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for link in self.link_dict.keys()} for rxTerm in self.rxTerm_vals.keys()}
        # Make array with the number of good links for every configuration
        self.good_links_tx_dict = {rxTerm : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for rxTerm in self.rxTerm_vals.keys()}
        self.super_good_links_tx_dict = {rxTerm : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for rxTerm in self.rxTerm_vals.keys()}
        # Fill arrays
        self.fillTxArrays()

        # Same but for Rx
        self.openA_rx_dict = {link : np.zeros((self.nRxEmp_vals, self.nRxTerm_vals*self.nRxAmp_vals)) for link in self.link_dict.keys()}
        self.error_rx_dict = {link : np.zeros((self.nRxEmp_vals, self.nRxTerm_vals*self.nRxAmp_vals)) for link in self.link_dict.keys()}
        # Make array with the number of good links for every configuration
        self.good_links_rx = np.zeros((self.nRxEmp_vals, self.nRxTerm_vals*self.nRxAmp_vals))
        self.super_good_links_rx = np.zeros((self.nRxEmp_vals, self.nRxTerm_vals*self.nRxAmp_vals))
        # Fill arrays
        self.fillRxArrays()


    # Reads a BER file and saves it as a dictionary of pandas dataframe. One dataframe per link.
    def readBERFile(self):

        current_link = ""
        row = -1 # Counter of which row to write to
        link_number = -1 # Numerical value for links

        # Loop over all input files
        for file_name in self.file_list:

            file = open(file_name, "r") # Open file
            # Loop over all lines in the file
            for line in file:

                line = line.replace(" ", "") # Remove all spaces

                # Start of new Scan
                if "Scan" in line:
                    # Add empty row
                    row += 1
                    self.df.loc[row] = [None] * len(self.column_names)
                    # Update current link name
                    current_link = line.split("Link")[1][:-2]
                    # Add new link to dictionary
                    if current_link not in self.link_dict.keys():
                        link_number += 1
                        self.link_dict[current_link] = link_number
                    # Add link name to dataframe
                    self.df.at[row,"Link"] = current_link
                    # Process next line
                    continue
                # Lines to ignore
                elif "Link:" in line or line == "\n":
                    continue

                # Get key and value from line
                key, val = line.split(":")

                # Insert val in the dataframe
                if key in self.column_names:
                    try:
                        self.df.at[row, key] = float(val)
                    except ValueError: # Some settings are strings like "Low/Medium/High/Off"
                        self.df.at[row, key] = val.strip()


    # Fills open area and error arrays for Tx side
    def fillTxArrays(self):

        # Check that we have all the Tx values needed
        if not self.nTxPre_vals or not self.nTxPost_vals or not self.nTxDiff_vals or not self.nTxEq_vals:
            print("Warning: couldn't fill Tx Arrays, no values.")
            return False

        # Loop over values in Error/Open Area column and fill array
        for index, row in self.df.iterrows():

            # Compute the x/y indices of where to save the values
            x_index = self.txEq_vals[row["txEq"]] * self.nTxDiff_vals + self.txDiff_vals[row["txDiff"]]
            y_index = self.txPre_vals[row["txPre"]] * self.nTxPost_vals + self.txPost_vals[row["txPost"]]

            # Fill arrays
            link= row["Link"]
            rxTerm = row["rxTerm"]
            self.openA_tx_dict[rxTerm][link][y_index][x_index] = row["OpenA"]
            self.error_tx_dict[rxTerm][link][y_index][x_index] = row["Errors"]

            # Check if good configuration
            if row["Errors"] == 0:
                self.good_links_tx_dict[rxTerm][y_index][x_index] += 1
                if row["OpenA"] > self.openarea_cut:
                    self.super_good_links_tx_dict[rxTerm][y_index][x_index] += 1

        return True


    # Fills open area and error arrays for Rx side
    def fillRxArrays(self):

        # Check that we have all the Rx values needed
        if not self.nRxEmp_vals or not self.nRxAmp_vals or not self.nRxTerm_vals:
            print("Warning: couldn't fill Rx Arrays, no values.")
            return False

        # Loop over values in Error/Open Area column and fill array
        for index, row in self.df.iterrows():

            # Compute the x/y indices of where to save the values
            x_index = self.rxTerm_vals[row["rxTerm"]] * self.nRxAmp_vals + self.rxAmp_vals[row["rxAmp"]]
            y_index = self.rxEmp_vals[row["rxEmp"]]

            # Fill arrays
            link= row["Link"]
            self.openA_rx_dict[link][y_index][x_index] = row["OpenA"]
            self.error_rx_dict[link][y_index][x_index] = row["Errors"]

            # Check if good configuration
            if row["Errors"] == 0:
                self.good_links_rx[y_index][x_index] += 1
                if row["OpenA"] > self.openarea_cut:
                    self.super_good_links_rx[y_index][x_index] += 1

        return True


    # Function that sets the axes ticks for Tx configuration histograms
    def setTxConfigAxesTicks(self, axes, fontsize=10):

        # Plot TxDiff Axis
        axes.set_xlabel("TxDiff [mV]")
        x1_tick_labels = [str(int(val)) for i in range(self.nTxEq_vals) for val in self.txDiff_vals]
        axes.set_xticks(np.arange(self.nTxDiff_vals*self.nTxEq_vals))  # Set ticks
        axes.set_xticklabels(x1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot TxPre Axis
        axes.set_ylabel("TxPre [dB]")
        y1_tick_labels = [str(val) for val in self.txPre_vals for i in range(self.nTxPost_vals)]
        axes.set_yticks(np.arange(self.nTxPre_vals*self.nTxPost_vals))  # Set ticks
        axes.set_yticklabels(y1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot TxEq values
        ax_x2 = axes.secondary_xaxis('top', xlabel="Eq [dB]")
        x2_tick_labels = [str(val) for val in self.txEq_vals for i in range(self.nTxDiff_vals)]
        ax_x2.set_xticks(np.arange(self.nTxDiff_vals*self.nTxEq_vals)) # Set ticks
        ax_x2.set_xticklabels(x2_tick_labels, fontsize=fontsize) # Set tick labels

        # Plot TxPost values
        ax_y2 = axes.secondary_yaxis('right', ylabel="TxPost [dB]")
        y2_tick_labels = [str(val) for i in range(self.nTxPre_vals) for val in self.txPost_vals]
        ax_y2.set_yticks(np.arange(self.nTxPre_vals*self.nTxPost_vals)) # Set ticks
        ax_y2.set_yticklabels(y2_tick_labels, fontsize=fontsize) # Set tick labels


    # Function that sets the axes ticks for Rx configuration histograms
    def setRxConfigAxesTicks(self, axes, fontsize=10):

        # Plot Amplitude Axis
        axes.set_xlabel("Amplitude %s" % ("[mV]" if isinstance(list(self.rxAmp_vals.keys())[0], float) else ""))
        x1_tick_labels = [str(val) for i in range(self.nRxTerm_vals) for val in self.rxAmp_vals]
        axes.set_xticks(np.arange(self.nRxAmp_vals*self.nRxTerm_vals))  # Set ticks
        axes.set_xticklabels(x1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot PreEmp Axis
        axes.set_ylabel("PreEmp [dB]")
        y1_tick_labels = [str(val) for val in self.rxEmp_vals]
        axes.set_yticks(np.arange(self.nRxEmp_vals))  # Set ticks
        axes.set_yticklabels(y1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot RxTerm values
        ax_x2 = axes.secondary_xaxis('top', xlabel="RxTerm [mV]")
        x2_tick_labels = [str(int(val)) for val in self.rxTerm_vals for i in range(self.nRxAmp_vals)]
        ax_x2.set_xticks(np.arange(self.nRxAmp_vals*self.nRxTerm_vals)) # Set ticks
        ax_x2.set_xticklabels(x2_tick_labels, fontsize=fontsize) # Set tick labels


    # Make 2D plots out of multidimensional data using tSNE
    def plotTSNE(self, only_good_configs=False, output_name=""):
    
        # Only use the interesting columns
        df_data = pd.DataFrame(self.df, columns=["txDiff", "txPre", "txPost", "txEq", "rxTerm", "rxAmp", "rxEmp", "Errors", "OpenA", "Link"]) # "BER"
        df_data.dropna(axis='columns', inplace=True)
        # df_data["Errors"] = np.log(1.0/(df_data["Errors"].astype("int")+1))

        # Replace link string by its corresponding number value or TSNE won't work
        for index, row in df_data.iterrows():
            df_data.loc[index, "Link"] = self.link_dict[row["Link"]]
        df_data[["Link"]] = df_data[["Link"]].astype("int")
        # Replace rxAmp by its corresponding number value, if it isn't one already
        if not all(isinstance(x, float) for x in self.rxAmp_vals):
            for index, row in df_data.iterrows():
                df_data.loc[index, "rxAmp"] = self.rxAmp_vals[row["rxAmp"]]
            df_data[["rxAmp"]] = df_data[["rxAmp"]].astype("int")

        # Add/remove columns depending on what plots to create
        if only_good_configs:
            df_data.reset_index(inplace=True) # Reset index or we will drop more than needed
            df_data.drop(df_data[(df_data.Errors>0) & (df_data.OpenA>self.openarea_cut)].index, inplace=True)
            df_data.drop(columns=["Errors", "OpenA"], inplace=True)
        else:
            df_errors = pd.DataFrame(self.df, columns=["Errors"]) # True/False, If have errors or not
            # df_errors = df_errors[["Errors"]].astype("bool")
            df_errors.loc[self.df.Errors == 0, 'Errors'] = "False"
            df_errors.loc[self.df.Errors > 1000, 'Errors'] = "True"
            df_errors.loc[(self.df.Errors <= 1000) & (self.df.Errors > 0), 'Errors'] = "False-ish (<1000 errors)"
    
            df_errors.reset_index(inplace=True, drop=True)
    
        # Reset index
        df_data.reset_index(inplace=True, drop=True)
    
        # Do the TSNE dimensionality reduction
        tsne = TSNE(n_components=2, perplexity=self.perplexity, n_iter=self.n_iter, learning_rate=self.learning_rate)
        tsne_results = tsne.fit_transform(df_data.values)
    
        # Convert results into dataframe
        df_results = pd.DataFrame(tsne_results, columns=['tsne-x','tsne-y'])
        df_results = df_results.join(df_data["Link"])
        if not only_good_configs:
            df_results = df_results.join(df_errors["Errors"])
    
        # Plot the results
        fig, axes = plt.subplots(figsize=(12, 9))
        sns.scatterplot(
            data=df_results, x="tsne-x", y="tsne-y",
            hue="Link",
            palette=sns.color_palette("hls", len(self.link_dict)),
            style=None if only_good_configs else "Errors",
            markers=['o'] if only_good_configs else ['X', 's', 'o'],
            legend="full",
            alpha=0.4
        ).set(title="Board %s (%s), only good configurations: 0 errors, Open Area>%i%%\nTraining input: %s" % (self.board, self.channels, self.openarea_cut, list(df_data.columns)) if only_good_configs else "Board %s (%s)\nTraining input: %s" % (self.board, self.channels, list(df_data.columns)))

        # Fix padding
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        fig.tight_layout()

        # Save figure
        plt.savefig("%stsne_%s_%s.pdf" % (self.output_dir, output_name, "good" if only_good_configs else "all"), bbox_inches='tight')
        # plt.show()
        plt.close()


    # Plots the primary array as a histogram with colourbar
    # Values of a secondary array can be printed in each bin
    def plotSingleArray(self, primary_array=None, secondary_array=None, tx=True, mask=True, title="", cbar_label="", cbar_limits=(None,None), output_name=""):

        # Make plot
        fig, axes = plt.subplots(figsize=(12, 9))
        axes.set_title(title)
        if tx:
            self.setTxConfigAxesTicks(axes)
            x_range = range(self.nTxDiff_vals*self.nTxEq_vals)
            y_range = range(self.nTxPre_vals*self.nTxPost_vals)
        else:
            self.setRxConfigAxesTicks(axes)
            x_range = range(self.nRxAmp_vals*self.nRxTerm_vals)
            y_range = range(self.nRxEmp_vals)

        # Plot the primary array
        if mask:
            primary_array_masked = np.ma.masked_where(secondary_array > 0, primary_array)
            primary_array_masked = np.ma.masked_where(primary_array_masked <= self.openarea_cut, primary_array_masked)
            plt.imshow(primary_array_masked)
        else:
            plt.imshow(primary_array)

        # Print the secondary array in each bin
        if secondary_array.any():
            for i in y_range:
                for j in x_range:
                    text = axes.text(j, i, convert_int_prefix(secondary_array[i, j]), ha="center", va="center", color="black")
    
        # Plot colour bar
        cbar = plt.colorbar(fraction=0.027, pad=0.1)
        plt.clim(cbar_limits[0], cbar_limits[1])
        cbar.set_label(cbar_label)
    
        # Save figure
        plt.savefig("%sconfigs%s%s.pdf" % (self.output_dir, "_"+output_name if output_name else "", "_masked" if mask else ""))
        # plt.show()
        plt.close()


    # Same as above but plots histograms for all links in the same plot
    def plotArrays(self, primary_dict=None, secondary_dict=None, tx=True, mask=True, title="", cbar_label="", cbar_limits=(None,None), output_name=""):

        ncols = 4 # Number of subplot columns
        nrows = int(np.ceil(len(self.link_dict)/ncols)) # Number of subplot rows
            
        c, r = 0, 0 # Some counters

        fig, fig_axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(24, 15))
        fig.suptitle(title, fontsize=20)

        # Loop over all dataframes in the dictionary
        for link in self.link_dict.keys():

            # Make subplot
            axes = fig_axes[r,c]
            axes.set_title(link)
            if tx:
                self.setTxConfigAxesTicks(axes, fontsize=8)
                x_range = range(self.nTxDiff_vals*self.nTxEq_vals)
                y_range = range(self.nTxPre_vals*self.nTxPost_vals)
            else:
                self.setRxConfigAxesTicks(axes, fontsize=8)
                x_range = range(self.nRxAmp_vals*self.nRxTerm_vals)
                y_range = range(self.nRxEmp_vals)

            # Plot the primary array
            if mask:
                primary_array_masked = np.ma.masked_where(secondary_dict[link] > 0, primary_dict[link])
                primary_array_masked = np.ma.masked_where(primary_array_masked <= self.openarea_cut, primary_array_masked)
                im = axes.imshow(primary_array_masked, vmin=cbar_limits[0], vmax=cbar_limits[1])
            else:
                im = axes.imshow(primary_dict[link], vmin=cbar_limits[0], vmax=cbar_limits[1])

            # Print the error count in each bin
            if secondary_dict:
                for i in y_range:
                    for j in x_range:
                        text = axes.text(j, i, convert_int_prefix(secondary_dict[link][i, j]), ha="center", va="center", color="black", fontsize=5)
    
            # Don't plot NaN
            current_cmap = matplotlib.cm.get_cmap().copy()
            current_cmap.set_bad(color='white')
    
            # Increment row and column counters
            if c < ncols-1:
                c += 1
            else:
                c = 0
                r += 1

        # Fix padding between subplots
        fig.tight_layout()
    
        # Plot colour bar
        fig.subplots_adjust(right=0.93)
        cbar_ax = fig.add_axes([0.96, 0.07, 0.01, 0.85])
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label(cbar_label)
    
        # Save figure
        plt.savefig("%sconfigs%s%s.pdf" % (self.output_dir, "_"+output_name if output_name else "", "_masked" if mask else ""))
        # plt.show()
        plt.close()


########################################
# Run script

amazing_thing = AmazingClassName(file_list=input_list, output_dir=args.outputDir, board=args.board, openarea_cut=args.open_area)


# Plot snake
if args.tsne:
    amazing_thing.plotTSNE(output_name="board%s" % (amazing_thing.board))
    # amazing_thing.plotTSNE(only_good_configs=True, output_name="board%s" % (amazing_thing.board))


# Plot error count and open area

# Test one link
if args.test:
    test_rxTerm = next(iter(amazing_thing.rxTerm_vals.keys()))
    test_link = next(iter(amazing_thing.link_dict.keys()))
    amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_tx_dict[test_rxTerm][test_link],
                                  secondary_array=amazing_thing.error_tx_dict[test_rxTerm][test_link],
                                  title="Board %s (%s), %s, Open Area>%i%%, RxTerm %i mV" % (amazing_thing.board, amazing_thing.channels, test_link, amazing_thing.openarea_cut, test_rxTerm),
                                  cbar_label="Open Area [%]",
                                  cbar_limits=(amazing_thing.openarea_cut,100),
                                  output_name="board%s_tx_openArea_error_rxTerm%i_%s" % (amazing_thing.board, test_rxTerm, test_link)
                                 )

# Create all Tx plots
if args.tx or args.txinv:
    if args.all:
        # All links in seperate plots
        for rxTerm in amazing_thing.rxTerm_vals.keys():
            for link in amazing_thing.link_dict.keys():
                amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_tx_dict[rxTerm][link],
                                              secondary_array=amazing_thing.error_tx_dict[rxTerm][link],
                                              title="Board %s (%s), %s, Open Area>%i%%, RxTerm %i mV" % (amazing_thing.board, amazing_thing.channels, link, amazing_thing.openarea_cut, rxTerm),
                                              mask=False,
                                              cbar_label="Open Area [%]",
                                              cbar_limits=(0,100),
                                              output_name="board%s_tx%s_openArea_error_rxTerm%i_%s" % (amazing_thing.board, "_inverted" if args.txinv else "", rxTerm, link)
                                             )

    # All links in the same plot
    for rxTerm in amazing_thing.rxTerm_vals.keys():
        amazing_thing.plotArrays(primary_dict=amazing_thing.openA_tx_dict[rxTerm],
                                 secondary_dict=amazing_thing.error_tx_dict[rxTerm],
                                 title="Board %s (%s), All Links%s, Open Area>%i%%, RxTerm %i mV" % (amazing_thing.board, amazing_thing.channels, " Inverted" if args.txinv else "", amazing_thing.openarea_cut, rxTerm),
                                 cbar_label="Open Area [%]",
                                 cbar_limits=(amazing_thing.openarea_cut,100),
                                 output_name="board%s_tx%s_openArea_error_rxTerm%i_all" % (amazing_thing.board, "_inverted" if args.txinv else "", rxTerm)
                                )

    # All links in the same plot but don't mask 0 errors and open area cut
    for rxTerm in amazing_thing.rxTerm_vals.keys():
        amazing_thing.plotArrays(primary_dict=amazing_thing.openA_tx_dict[rxTerm],
                                 secondary_dict=amazing_thing.error_tx_dict[rxTerm],
                                 mask=False,
                                 title="Board %s (%s), All Links%s, RxTerm %i mV" % (amazing_thing.board, amazing_thing.channels, " Inverted" if args.txinv else "", rxTerm),
                                 cbar_label="Open Area [%]",
                                 cbar_limits=(0,100),
                                 output_name="board%s_tx%s_openArea_error_rxTerm%i_all" % (amazing_thing.board, "_inverted" if args.txinv else "", rxTerm)
                                )

    # Plot number of good links, 0 errors
    for rxTerm in amazing_thing.rxTerm_vals.keys():
        amazing_thing.plotSingleArray(primary_array=amazing_thing.good_links_tx_dict[rxTerm],
                                      secondary_array=amazing_thing.good_links_tx_dict[rxTerm],
                                      mask=False,
                                      title="Board %s (%s), number of good links%s (RxTerm %i mV): 0 Errors" % (amazing_thing.board, amazing_thing.channels, " inverted" if args.txinv else "", rxTerm),
                                      cbar_label="Number of good links",
                                      cbar_limits=(0,len(amazing_thing.link_dict)),
                                      output_name="board%s_tx%s_good_links_rxTerm%i" % (amazing_thing.board, "_inverted" if args.txinv else "", rxTerm)
                                     )

    # Plot number of super good links, cut on both error and open area
    for rxTerm in amazing_thing.rxTerm_vals.keys():
        amazing_thing.plotSingleArray(primary_array=amazing_thing.super_good_links_tx_dict[rxTerm],
                                      secondary_array=amazing_thing.super_good_links_tx_dict[rxTerm],
                                      mask=False,
                                      title="Board %s (%s), number of super good links%s (RxTerm %i mV): 0 Errors, Open Area>%i%%" % (amazing_thing.board, amazing_thing.channels, " inverted" if args.txinv else "", rxTerm, amazing_thing.openarea_cut),
                                      cbar_label="Number of super good links",
                                      cbar_limits=(0,len(amazing_thing.link_dict)),
                                      output_name="board%s_tx%s_super_good_links_rxTerm%i" % (amazing_thing.board, "_inverted" if args.txinv else "", rxTerm)
                                     )

# Create all Rx plots
if args.rx:
    if args.all:
        for link in amazing_thing.link_dict.keys():
            amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_rx_dict,
                                          secondary_array=amazing_thing.error_rx_dict,
                                          tx=False,
                                          title="Board %s (%s), %s, Open Area>%i%%" % (amazing_thing.board, amazing_thing.channels, link, amazing_thing.openarea_cut),
                                          cbar_label="Open Area [%]",
                                          cbar_limits=(amazing_thing.openarea_cut,100),
                                          output_name="board%s_rx_openArea_error_%s" % (amazing_thing.board, link)
                                         )

    amazing_thing.plotArrays(primary_dict=amazing_thing.openA_rx_dict,
                             secondary_dict=amazing_thing.error_rx_dict,
                             tx=False,
                             title="Board %s (%s), All Links, Open Area>%i%%, txPre %.2f dB, txPost %.2f dB, txDiff %i mV, txEq %.1f dB" % (amazing_thing.board, amazing_thing.channels, amazing_thing.openarea_cut, next(iter(amazing_thing.txPre_vals.keys())), next(iter(amazing_thing.txPost_vals.keys())), next(iter(amazing_thing.txDiff_vals.keys())), next(iter(amazing_thing.txEq_vals.keys()))),
                             cbar_label="Open Area [%]",
                             cbar_limits=(amazing_thing.openarea_cut,100),
                             output_name="board%s_rx_openArea_error_all" % (amazing_thing.board)
                            )

    # All links in the same plot but don't mask 0 errors and open area cut
    amazing_thing.plotArrays(primary_dict=amazing_thing.openA_rx_dict,
                             secondary_dict=amazing_thing.error_rx_dict,
                             tx=False,
                             mask=False,
                             title="Board %s (%s), All Links, txPre %.2f dB, txPost %.2f dB, txDiff %i mV, txEq %.1f dB" % (amazing_thing.board, amazing_thing.channels, next(iter(amazing_thing.txPre_vals.keys())), next(iter(amazing_thing.txPost_vals.keys())), next(iter(amazing_thing.txDiff_vals.keys())), next(iter(amazing_thing.txEq_vals.keys()))),
                             cbar_label="Open Area [%]",
                             cbar_limits=(0,100),
                             output_name="board%s_rx_openArea_error_all" % (amazing_thing.board)
                            )

    amazing_thing.plotSingleArray(primary_array=amazing_thing.good_links_rx,
                                  secondary_array=amazing_thing.good_links_rx,
                                  tx=False,
                                  mask=False,
                                  title="Board %s (%s), txPre %.2f dB, txPost %.2f dB, txDiff %i mV, txEq %.1f dB\n Number of good links: 0 Errors" % (amazing_thing.board, amazing_thing.channels, next(iter(amazing_thing.txPre_vals.keys())), next(iter(amazing_thing.txPost_vals.keys())), next(iter(amazing_thing.txDiff_vals.keys())), next(iter(amazing_thing.txEq_vals.keys()))),
                                  cbar_label="Number of good links",
                                  cbar_limits=(0,len(amazing_thing.link_dict)),
                                  output_name="board%s_rx_good_links" % (amazing_thing.board)
                                 )

    amazing_thing.plotSingleArray(primary_array=amazing_thing.super_good_links_rx,
                                  secondary_array=amazing_thing.super_good_links_rx,
                                  tx=False,
                                  mask=False,
                                  title="Board %s (%s), txPre %.2f dB, txPost %.2f dB, txDiff %i mV, txEq %.1f dB\n Number of super good links: 0 Errors, Open Area>%i%%" % (amazing_thing.board, amazing_thing.channels, next(iter(amazing_thing.txPre_vals.keys())), next(iter(amazing_thing.txPost_vals.keys())), next(iter(amazing_thing.txDiff_vals.keys())), next(iter(amazing_thing.txEq_vals.keys())), amazing_thing.openarea_cut),
                                  cbar_label="Number of super good links",
                                  cbar_limits=(0,len(amazing_thing.link_dict)),
                                  output_name="board%s_rx_super_good_links" % (amazing_thing.board)
                                 )

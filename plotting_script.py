#!/usr/bin/env python3
import os
import argparse

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.manifold import TSNE
import numpy as np
import seaborn as sns

# Argument parser
parser = argparse.ArgumentParser(description="Reads scan data and makes plots.", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-i", "--inputDir", default=None, nargs="+", help="Directory to the scan results.")
parser.add_argument("-o", "--outputDir", default="./plots/", help="Name of output directory. (default = %(default)s)")
args = parser.parse_args()

# Create list of input files
input_list = [dir+"/BER_summary.txt" for dir in args.inputDir]

# Create output directory
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

    def __init__(self, file_list, output_dir="./", openarea_cut=30):

        # Set input parameters
        self.file_list = file_list
        self.output_dir = output_dir
        self.openarea_cut = openarea_cut

        # Stuff we don't have as input paramters
        self.column_names = ["Link", "txDiff", "txPre", "txPost", "txEq", "rxTerm", "Bits", "Errors", "BER", "OpenA"] # Names of the columns for dataframe, same as the values in BER_summary.txt

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

        # Dictionary of unique values
        self.txPre_vals = {sorted(self.df["txPre"].unique())[i] : i for i in range(self.nTxPre_vals)}
        self.txPost_vals = {sorted(self.df["txPost"].unique())[i] : i for i in range(self.nTxPost_vals)}
        self.txDiff_vals = {sorted(self.df["txDiff"].unique())[i] : i for i in range(self.nTxDiff_vals)}
        self.txEq_vals = {sorted(self.df["txEq"].unique())[i] : i for i in range(self.nTxEq_vals)}

        # Make new dictionaries of arrays which will correspond to our histogram of values
        self.openA_dict = {link : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for link in self.link_dict.keys()}
        self.error_dict = {link : np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals)) for link in self.link_dict.keys()}
        # Make array with the number of good links for every configuration
        self.good_links = np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals))
        self.super_good_links = np.zeros((self.nTxPre_vals*self.nTxPost_vals, self.nTxDiff_vals*self.nTxEq_vals))

        # Fill arrays
        self.fillArrays()


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
                    self.df.at[row, key] = float(val)


    # Fills open area and error arrays
    def fillArrays(self):
        # Loop over values in Error/Open Area column and fill array
        for index, row in self.df.iterrows():
            # Compute the x/y indices of where to save the values
            x_index = self.txPre_vals[row["txPre"]] * self.nTxPost_vals + self.txPost_vals[row["txPost"]]
            y_index = self.txEq_vals[row["txEq"]] * self.nTxDiff_vals + self.txDiff_vals[row["txDiff"]]
            # Fill arrays
            link = row["Link"]
            self.openA_dict[link][x_index][y_index] = row["OpenA"] if (row["Errors"] == 0 and row["OpenA"] > self.openarea_cut) else np.nan
            self.error_dict[link][x_index][y_index] = row["Errors"]
            # Check if good configuration
            if row["Errors"] == 0:
                self.good_links[x_index][y_index] += 1
                if row["OpenA"] > self.openarea_cut:
                    self.super_good_links[x_index][y_index] += 1


    # Function that sets the axes ticks for configuration histograms
    def setConfigAxesTicks(self, axes, fontsize=10):

        # Plot TxDiff Axis
        axes.set_xlabel("TxDiff [mV]")
        x1_tick_labels = [str(int(val)) for i in range(self.nTxEq_vals) for val in self.txDiff_vals]
        axes.set_xticks(np.arange(self.nTxDiff_vals*self.nTxEq_vals))  # Set ticks
        axes.set_xticklabels(x1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot TxPost Axis
        axes.set_ylabel("TxPost [dB]")
        y1_tick_labels = [str(val) for i in range(self.nTxPre_vals) for val in self.txPost_vals]
        axes.set_yticks(np.arange(self.nTxPre_vals*self.nTxPost_vals))  # Set ticks
        axes.set_yticklabels(y1_tick_labels, fontsize=fontsize)  # Set tick labels

        # Plot TxEq values
        ax_x2 = axes.secondary_xaxis('top', xlabel="Eq [some unit]")
        x2_tick_labels = [str(val) for val in self.txEq_vals for i in range(self.nTxDiff_vals)]
        ax_x2.set_xticks(np.arange(self.nTxDiff_vals*self.nTxEq_vals)) # Set ticks
        ax_x2.set_xticklabels(x2_tick_labels, fontsize=fontsize) # Set tick labels

        # Plot TxPre values
        ax_y2 = axes.secondary_yaxis('right', ylabel="TxPre [dB]")
        y2_tick_labels = [str(val) for val in self.txPre_vals for i in range(self.nTxPost_vals)]
        ax_y2.set_yticks(np.arange(self.nTxPre_vals*self.nTxPost_vals)) # Set ticks
        ax_y2.set_yticklabels(y2_tick_labels, fontsize=fontsize) # Set tick labels


    # Make 2D plots out of multidimensional data using tSNE
    def plotTSNE(self, only_good_configs=False):
    
        # Only use the interesting columns
        df_data = pd.DataFrame(self.df, columns=["txDiff", "txPre", "txPost", "txEq", "rxTerm", "Errors", "OpenA", "Link"])

        # Replace link string by its corresponding number value or TSNE won't work
        for index, row in df_data.iterrows():
            df_data.loc[index, "Link"] = self.link_dict[row["Link"]]
        df_data[["Link"]] = df_data[["Link"]].astype("int")

        # Add/remove columns depending on what plots to create
        if only_good_configs:
            df_data.reset_index(inplace=True) # Reset index or we will drop more than needed
            df_data.drop(df_data[(df_data.Errors>0) & (df_data.OpenA>self.openarea_cut)].index, inplace=True)
            df_data.drop(columns=["Errors", "OpenA"], inplace=True)
        else:
            df_errors = df_data[["Errors"]].copy() # True/False, If have errors or not
            # df_errors = df_errors[["Errors"]].astype("bool")
            df_errors.loc[df_data.Errors == 0, 'Errors'] = "False"
            df_errors.loc[df_data.Errors > 1000, 'Errors'] = "True"
            df_errors.loc[(df_data.Errors <= 1000) & (df_data.Errors > 0), 'Errors'] = "False-ish (<1000 errors)"
    
            df_errors.reset_index(inplace=True)
    
        # Reset index
        df_data.reset_index(inplace=True)
    
        # Do the TSNE dimensionality reduction
        tsne = TSNE(n_components=2, perplexity=20, n_iter=1000, learning_rate=200)
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
            legend="full",
            alpha=0.4
        ).set(title="Only good configurations, 0 errors, Open Area>%i%%" % self.openarea_cut if only_good_configs else "All configurations")

        # Fix padding
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        fig.tight_layout()

        # Save figure
        plt.savefig("%stsne_%s.pdf" % (self.output_dir, "good" if only_good_configs else "all"), bbox_inches='tight')
        plt.show()
        plt.close()


    # Plots the primary array as a histogram with colourbar
    # Values of a secondary array can be printed in each bin
    def plotSingleArray(self, primary_array=None, secondary_array=None, title="", cbar_label="", cbar_limits=(None,None), output_name=""):

        # Make plot
        fig, axes = plt.subplots(figsize=(12, 9))
        axes.set_title(title)
        self.setConfigAxesTicks(axes)
    
        # Plot the primary array
        plt.imshow(primary_array)
    
        # Print the secondary array in each bin
        if secondary_array.any():
            for i in range(self.nTxPre_vals*self.nTxPost_vals):
                for j in range(self.nTxDiff_vals*self.nTxEq_vals):
                    text = axes.text(j, i, convert_int_prefix(secondary_array[i, j]), ha="center", va="center", color="black")
    
        # Don't plot NaN
        current_cmap = matplotlib.cm.get_cmap().copy()
        current_cmap.set_bad(color='white')
    
        # Plot colour bar
        cbar = plt.colorbar(fraction=0.027, pad=0.1)
        plt.clim(cbar_limits[0], cbar_limits[1])
        cbar.set_label(cbar_label)
    
        # Save figure
        plt.savefig("%sconfigs%s.pdf" % (self.output_dir, "_"+output_name if output_name else ""))
        # plt.show()
        plt.close()


    # Same as above but plots histograms for all 12 links in the same plot
    def plot12Arrays(self, primary_dict=None, secondary_dict=None, title="", cbar_label="", cbar_limits=(None,None), output_name=""):
    
        ncols, nrows = 4, 3 # Number of subplots in each column/row
        c, r = 0, 0 # Some counters
    
        fig, fig_axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(24, 15))
        fig.suptitle(title, fontsize=20)
    
        # Loop over all dataframes in the dictionary
        for link in self.link_dict.keys():

            # Make subplot
            axes = fig_axes[r,c]
            axes.set_title(link)
            self.setConfigAxesTicks(axes, fontsize=8)
    
            im = axes.imshow(primary_dict[link], vmin=cbar_limits[0], vmax=cbar_limits[1])
    
            # Print the error count in each bin
            if secondary_dict:
                for i in range(self.nTxPre_vals*self.nTxPost_vals):
                    for j in range(self.nTxDiff_vals*self.nTxEq_vals):
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
        plt.savefig("%sconfigs%s_all.pdf" % (self.output_dir, "_"+output_name if output_name else ""))
        # plt.show()
        plt.close()



# Run script
amazing_thing = AmazingClassName(file_list=input_list, output_dir=args.outputDir)

# amazing_thing.plotTSNE()
# amazing_thing.plotTSNE(only_good_configs=True)

# Plot error count and open area
# test_link = next(iter(amazing_thing.link_dict.keys()))
# amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_dict[test_link],
#                               secondary_array=amazing_thing.error_dict[test_link],
#                               title="%s, Open Area>%i%%" % (test_link, amazing_thing.openarea_cut),
#                               cbar_label="Open Area [%]",
#                               cbar_limits=(amazing_thing.openarea_cut,100),
#                               output_name="openArea_error_"+test_link
#                              )

# for link in amazing_thing.link_dict.keys():
#     amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_dict[link],
#                                   secondary_array=amazing_thing.error_dict[link],
#                                   title="%s, Open Area>%i%%" % (link, amazing_thing.openarea_cut),
#                                   cbar_label="Open Area [%]",
#                                   cbar_limits=(amazing_thing.openarea_cut,100),
#                                   output_name="openArea_error_inverted"+link
#                                  )

amazing_thing.plot12Arrays(primary_dict=amazing_thing.openA_dict,
                           secondary_dict=amazing_thing.error_dict,
                           title="All links, Open Area>%i%%" % (amazing_thing.openarea_cut),
                           cbar_label="Open Area [%]",
                           cbar_limits=(amazing_thing.openarea_cut,100),
                           output_name="openArea_error"
                          )

# Plot number of good links, 0 errors
amazing_thing.plotSingleArray(primary_array=amazing_thing.good_links,
                              secondary_array=amazing_thing.good_links,
                              title="Number of good links: 0 Errors",
                              cbar_label="Number of good links",
                              cbar_limits=(0,12),
                              output_name="good_links"
                             )

# Plot number of super good links, cut on both error and open area
amazing_thing.plotSingleArray(primary_array=amazing_thing.super_good_links,
                              secondary_array=amazing_thing.super_good_links,
                              title="Number of super good links: 0 Errors, Open Area>%i%%" % (amazing_thing.openarea_cut),
                              cbar_label="Number of super good links",
                              cbar_limits=(0,12),
                              output_name="super_good_links"
                             )

# Inverted stuff
# for link in amazing_thing.link_dict.keys():
#     amazing_thing.plotSingleArray(primary_array=amazing_thing.openA_dict[link],
#                                   secondary_array=amazing_thing.error_dict[link],
#                                   title="%s, Open Area>%i%%" % (link, amazing_thing.openarea_cut),
#                                   cbar_label="Open Area [%]",
#                                   cbar_limits=(amazing_thing.openarea_cut,100),
#                                   output_name="openArea_error_inverted"+link
#                                  )
# 
# amazing_thing.plot12Arrays(primary_dict=amazing_thing.openA_dict,
#                            secondary_dict=amazing_thing.error_dict,
#                            title="All links inverted, Open Area>%i%%" % (amazing_thing.openarea_cut),
#                            cbar_label="Open Area [%]",
#                            cbar_limits=(amazing_thing.openarea_cut,100),
#                            output_name="openArea_error_inverted"
#                           )
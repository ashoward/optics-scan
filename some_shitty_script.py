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
parser.add_argument("-o", "--outputDir", default="./results/", help="Name of output directory. (default = %(default)s)")
args = parser.parse_args()

# Create list of input files
input_list = [dir+"/BER_summary.txt" for dir in args.inputDir]

# Create output directory
args.outputDir += "/"
if not os.path.exists(args.outputDir):
	os.mkdir(args.outputDir)


# Reads a BER file and saves it as a dictionary of pandas dataframe. One dataframe per link.
def readBERFile(file_list):

	df_dict = {} # Dictionary of dataframes, one per link
	current_link = ""
	column_names = ["txDiff", "txPre", "txPost", "txEq", "rxTerm", "Bits", "Errors", "BER", "OpenA"] # Names of the columns, same as the values in BER_summary.txt

	# Loop over all input files
	for file_name in file_list:

		file = open(file_name, "r") # Open file

		for line in file:

			line = line.replace(" ", "") # Remove all spaces

			if "Scan" in line:
				# Update current link name
				current_link = line.split("Link")[1][:-2]

				# Add link to dictionary and decide which row to write
				if current_link not in df_dict:
					df_dict[current_link] = pd.DataFrame(columns = column_names)
					df = df_dict[current_link]
					row = 0
				else:
					df = df_dict[current_link]
					row = df.index[-1] + 1

				# Add empty row 
				df = df_dict[current_link]
				df.loc[row] = [None] * len(column_names)

				# Process next line
				continue

			elif "Link:" in line or line == "\n":
				continue

			# Get key and value from line
			key, val = line.split(":")

			# Insert val in the dataframe
			if key in column_names:
				df.at[row, key] = float(val)

	return df_dict


# Converts long numerical values to a string with 3 numbers and a prefix, e.g. 3 millions becomes 3M
def convert_int_prefix(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


# Make 2D plots out of multidimensional data using tSNE
def plotTSNE(df_dict, only_good_configs=False, openarea_cut=50, output_dir=args.outputDir):

	# Create a dataframe with all links
	df_data = pd.DataFrame()
	link_dict = {} # Dictionary of links and their corresponding value
	link_number = -1 # Numerical value for links as training and plotting can't handle strings

	for key, df in df_dict.items():
		# Add link and value to dictionary
		if key not in link_dict:
			link_number += 1
			link_dict[key] = link_number

		# Add new column with link number
		df["Link"] = link_number
		df_data = df_data.append(df)

	# Only keep the interesting columns
	df_data = df_data[["txDiff", "txPre", "txPost", "txEq", "rxTerm", "Errors", "OpenA", "Link"]]

	# Add/remove columns depending on what plots to create
	if only_good_configs:
		df_data.reset_index(inplace=True) # Reset index or we will drop more than needed
		df_data.drop(df_data[(df_data.Errors>0) & (df_data.OpenA>openarea_cut)].index, inplace=True)
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
	plt.figure()

	sns.scatterplot(
		data=df_results, x="tsne-x", y="tsne-y",
		hue="Link",
		palette=sns.color_palette("hls", len(link_dict)),
		style=None if only_good_configs else "Errors",
		legend="full",
		alpha=0.4
	).set(title="Only good configurations, 0 errors, Open Area>%i%%" % openarea_cut if only_good_configs else "All configurations")

	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig("%stsne_%s.pdf" % (output_dir, "good" if only_good_configs else "all"), bbox_inches='tight', dpi=1200)
	# plt.show()
	plt.close()


# Plots some shit: takes one dataframe as input, corresponding to one link
# Plots the Open Area or Error Count for all configurations in a histogram
def plotSingleLink(df, link_name="SomeLink", openarea_cut=50, plot_error=True, output_dir=args.outputDir):

	# Count number of bins we need
	nTxPre_vals = df["txPre"].nunique()
	nTxPost_vals = df["txPost"].nunique()
	nTxDiff_vals = df["txDiff"].nunique()
	nTxEq_vals = df["txEq"].nunique()

	# Dictionary of unique values
	txPre_vals = {sorted(df["txPre"].unique())[i] : i for i in range(nTxPre_vals)}
	txPost_vals = {sorted(df["txPost"].unique())[i] : i for i in range(nTxPost_vals)}
	txDiff_vals = {sorted(df["txDiff"].unique())[i] : i for i in range(nTxDiff_vals)}
	txEq_vals = {sorted(df["txEq"].unique())[i] : i for i in range(nTxEq_vals)}

	# Make new arrays which will correspond to our histogram of values
	array_openA = np.zeros((nTxPre_vals*nTxPost_vals, nTxDiff_vals*nTxEq_vals))
	if plot_error:
		array_error = np.zeros((nTxPre_vals*nTxPost_vals, nTxDiff_vals*nTxEq_vals))

	# Loop over values in Error/Open Area column and fill array
	for index, row in df.iterrows():
		# Compute the x/y indices of where to save the values
		x_index = txPre_vals[row["txPre"]] * nTxPost_vals + txPost_vals[row["txPost"]]
		y_index = txEq_vals[row["txEq"]] * nTxDiff_vals + txDiff_vals[row["txDiff"]]
		# Fill arrays
		array_openA[x_index][y_index] = row["OpenA"] if (row["Errors"] == 0 and row["OpenA"] > openarea_cut) else np.nan
		if plot_error:
			array_error[x_index][y_index] = row["Errors"]

	# Make plot
	fig, axes = plt.subplots(figsize=(12, 9), dpi=80)
	axes.set_title("%s, Open Area>%i%%" % (link_name, openarea_cut))

	# Plot TxDiff Axis
	locs, labels = plt.xticks()  # Get the current locations and labels.
	axes.set_xlabel("TxDiff [mV]")
	x1_tick_labels = [str(int(val)) for i in range(nTxEq_vals) for val in txDiff_vals]
	plt.xticks(np.arange(0, nTxDiff_vals*nTxEq_vals, step=1))  # Set label locations.
	plt.xticks(np.arange(nTxDiff_vals*nTxEq_vals), x1_tick_labels)  # Set text labels.
	# Plot TxPost Axis
	locs, labels = plt.yticks()  # Get the current locations and labels.
	axes.set_ylabel("TxPost [dB]")
	y1_tick_labels = [str(val) for i in range(nTxPre_vals) for val in txPost_vals]
	plt.yticks(np.arange(0, nTxPre_vals*nTxPost_vals, step=1))  # Set label locations.
	plt.yticks(np.arange(nTxPre_vals*nTxPost_vals), y1_tick_labels)  # Set text labels.
	# Plot TxEq values
	ax_x2 = axes.secondary_xaxis('top', xlabel="Eq [some unit]")
	x2_tick_labels = [str(val) for val in txEq_vals for i in range(nTxDiff_vals)]
	ax_x2.set_xticks(np.arange(nTxDiff_vals*nTxEq_vals)) # Set ticks
	ax_x2.set_xticklabels(x2_tick_labels) # Set tick labels
	# Plot TxPre values
	ax_y2 = axes.secondary_yaxis('right', ylabel="TxPre [dB]")
	y2_tick_labels = [str(val) for val in txPre_vals for i in range(nTxPost_vals)]
	ax_y2.set_yticks(np.arange(nTxPre_vals*nTxPost_vals)) # Set ticks
	ax_y2.set_yticklabels(y2_tick_labels) # Set tick labels

	plt.imshow(array_openA)
	
	# Print the error count in each bin
	if plot_error:
		for i in range(nTxPre_vals*nTxPost_vals):
			for j in range(nTxDiff_vals*nTxEq_vals):
				text = axes.text(j, i, convert_int_prefix(array_error[i, j]), ha="center", va="center", color="black")

	# Don't plot NaN
	current_cmap = matplotlib.cm.get_cmap().copy()
	current_cmap.set_bad(color='white')

	# Plot colour bar
	cbar = plt.colorbar(fraction=0.0455, pad=0.1)
	plt.clim(openarea_cut, 100)
	cbar.set_label('Open Area [%]')

	# Save figure
	plt.savefig("%sconfigs%s_%s.pdf" % (output_dir, "_error" if plot_error else "", link_name), dpi=1200)
	# plt.show()
	plt.close()

	# Return array
	if plot_error:
		return array_error
	else:
		return array_openA


# Same as above but plots all 12 links in the same plot
# Plots the Open Area or Error Count for all configurations in a histogram
def plot12Links(df_dict, openarea_cut=50, plot_error=True, output_dir=args.outputDir):

	ncols = 4
	nrows = 3

	fig, fig_axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(24, 15), dpi=80)
	fig.suptitle("Open Area>%i%%" % (openarea_cut), fontsize=20)

	# Some counters
	c = 0
	r = 0

	# Loop over all dataframes in the dictionary
	for link_name, df in df_dict.items():

		# Make subplot
		axes = fig_axes[r,c]
		axes.set_title(link_name)

		# Count number of bins we need
		nTxPre_vals = df["txPre"].nunique()
		nTxPost_vals = df["txPost"].nunique()
		nTxDiff_vals = df["txDiff"].nunique()
		nTxEq_vals = df["txEq"].nunique()

		# Dictionary of unique values
		txPre_vals = {sorted(df["txPre"].unique())[i] : i for i in range(nTxPre_vals)}
		txPost_vals = {sorted(df["txPost"].unique())[i] : i for i in range(nTxPost_vals)}
		txDiff_vals = {sorted(df["txDiff"].unique())[i] : i for i in range(nTxDiff_vals)}
		txEq_vals = {sorted(df["txEq"].unique())[i] : i for i in range(nTxEq_vals)}

		# Make new arrays which will correspond to our histogram of values
		array_openA = np.zeros((nTxPre_vals*nTxPost_vals, nTxDiff_vals*nTxEq_vals))
		if plot_error:
			array_error = np.zeros((nTxPre_vals*nTxPost_vals, nTxDiff_vals*nTxEq_vals))

		# Loop over values in Error/Open Area column and fill array
		for index, row in df.iterrows():
			# Compute the x/y indices of where to save the values
			x_index = txPre_vals[row["txPre"]] * nTxPost_vals + txPost_vals[row["txPost"]]
			y_index = txEq_vals[row["txEq"]] * nTxDiff_vals + txDiff_vals[row["txDiff"]]
			# Fill arrays
			array_openA[x_index][y_index] = row["OpenA"] if (row["Errors"] == 0 and row["OpenA"] > openarea_cut) else np.nan
			if plot_error:
				array_error[x_index][y_index] = row["Errors"]

		# Plot TxDiff Axis
		axes.set_xlabel("TxDiff [mV]")
		x1_tick_labels = [str(int(val)) for i in range(nTxEq_vals) for val in txDiff_vals]
		axes.set_xticks(np.arange(nTxDiff_vals*nTxEq_vals))  # Set ticks
		axes.set_xticklabels(x1_tick_labels)  # Set tick labels
		# Plot TxPost Axis
		axes.set_ylabel("TxPost [dB]")
		y1_tick_labels = [str(val) for i in range(nTxPre_vals) for val in txPost_vals]
		axes.set_yticks(np.arange(nTxPre_vals*nTxPost_vals))  # Set ticks
		axes.set_yticklabels(y1_tick_labels)  # Set tick labels
		# Plot TxEq values
		ax_x2 = axes.secondary_xaxis('top', xlabel="Eq [some unit]")
		x2_tick_labels = [str(val) for val in txEq_vals for i in range(nTxDiff_vals)]
		ax_x2.set_xticks(np.arange(nTxDiff_vals*nTxEq_vals)) # Set ticks
		ax_x2.set_xticklabels(x2_tick_labels) # Set tick labels
		# Plot TxPre values
		ax_y2 = axes.secondary_yaxis('right', ylabel="TxPre [dB]")
		y2_tick_labels = [str(val) for val in txPre_vals for i in range(nTxPost_vals)]
		ax_y2.set_yticks(np.arange(nTxPre_vals*nTxPost_vals)) # Set ticks
		ax_y2.set_yticklabels(y2_tick_labels) # Set tick labels

		im = axes.imshow(array_openA, vmin=openarea_cut, vmax=100)
		
		# Print the error count in each bin
		if plot_error:
			for i in range(nTxPre_vals*nTxPost_vals):
				for j in range(nTxDiff_vals*nTxEq_vals):
					text = axes.text(j, i, convert_int_prefix(array_error[i, j]), ha="center", va="center", color="black", fontsize=5)
		
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
	cbar_ax = fig.add_axes([0.96, 0.08, 0.01, 0.85])
	cbar = fig.colorbar(im, cax=cbar_ax)
	cbar.set_label("Open Area [%]")

	# Save figure
	plt.savefig("%sconfigs%s_all.pdf" % (output_dir, "_error" if plot_error else ""), dpi=1200)
	plt.show()
	plt.close()



# Read input files and save as dictionary
df_dict = readBERFile(input_list)

# Plot using tSNE
# plotTSNE(df_dict)
# plotTSNE(df_dict, only_good_configs=True)

# Plot one shit
# plotSingleLink(next(iter(df_dict.values()))) # Plot error count and open area

# Plot all shit
for link, df in df_dict.items():
	plotSingleLink(df, link)
	# plotSingleLink(df, link, plot_error=False)

# Plot all shit in same plot...
# plot12Links(df_dict)
# plot12Links(df_dict, plot_error=False)

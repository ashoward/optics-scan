#!/usr/bin/env python3 
import argparse

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.manifold import TSNE
import numpy as np
import seaborn as sns

# Argument parser
parser = argparse.ArgumentParser(description="Reads scan data and makes plots.", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-i", "--inputDir", default="./", help="Directory to the scan results.")
parser.add_argument("-o", "--outputDir", default=".", help="Name of output directory. (default = %(default)s)")
args = parser.parse_args()

# Fix some shit
args.inputDir += "/"
args.outputDir += "/"


# Reads a BER file and saves it as a dictionary of pandas dataframe. One dataframe per link.
def readBERFile(file_name):

	file = open(file_name, "r") # Open file

	df_dict = {} # Dictionary of dataframes, one per link
	current_link = ""
	column_names = ["txDiff", "txPre", "txPost", "rxTerm", "txEq", "Bits", "Errors", "BER", "OpenA"] # Names of the columns, same as the values in BER_summary.txt

	for line in file:
		print(line)
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


# Make 2D plots out of multidimensional data using tSNE
def plotTSNE(df_dict, only_good_points=False):

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
	df_data = df_data[["txDiff", "txPre", "txPost", "txEq", "Errors", "OpenA", "Link"]]

	# Delete rows with non-zero errors? And small open area?
	if only_good_points:
		df_data.reset_index(inplace=True) # Reset index or we will drop more than needed
		df_data.drop(df_data[(df_data.Errors>0) & (df_data.OpenA>50)].index, inplace=True)
		df_data.drop(columns=["Errors", "OpenA"], inplace=True)
	else:
		df_errors = df_data[["Errors"]].copy() # True/False, If have errors or not
		df_errors = df_errors[["Errors"]].astype("bool")	
		df_errors.reset_index(inplace=True)

	# Reset index
	df_data.reset_index(inplace=True)

	# Do the TSNE dimensionality reduction
	tsne = TSNE(n_components=2, perplexity=20, n_iter=1000, learning_rate=200)
	tsne_results = tsne.fit_transform(df_data.values)

	# Convert results into dataframe
	df_results = pd.DataFrame(tsne_results, columns=['tsne-x','tsne-y'])
	df_results = df_results.join(df_data["Link"])
	if not only_good_points:
		df_results = df_results.join(df_errors["Errors"])

	# Plot the results
	plt.figure()

	sns.scatterplot(
		data=df_results, x="tsne-x", y="tsne-y",
		hue="Link",
		palette=sns.color_palette("hls", len(link_dict)),
		style=None if only_good_points else "Errors",
		legend="full",
		alpha=0.3
	)

	# plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.show()


# Plots some shit: takes one dataframe as input, corresponding to one link
# Plots the Open Area or Error Count for all configurations in a histogram
def plotHistShit(df, link_name="SomeLink", openarea_cut=30, plot_error=False):

	print(df)

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

	# Make new array which will correspond to our histogram of values
	array = np.zeros((nTxPre_vals*nTxPost_vals, nTxDiff_vals*nTxEq_vals))
	
	# Loop over values in Error/Open Area column and fill array
	for index, row in df.iterrows():
		# Compute the x/y indices of where to save the values
		x_index = txPre_vals[row["txPre"]] * nTxPost_vals + txPost_vals[row["txPost"]]
		y_index = txEq_vals[row["txEq"]] * nTxDiff_vals + txDiff_vals[row["txDiff"]]
		# Fill array
		if not plot_error:
			array[x_index][y_index] = row["OpenA"] if (row["Errors"] == 0 and row["OpenA"] > openarea_cut) else np.nan
		else:
			array[x_index][y_index] = row["Errors"] if row["OpenA"] > openarea_cut else np.nan

	# Make plot
	fig, axes = plt.subplots(figsize=(8, 6), dpi=80)
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

	plt.imshow(array)
	# plt.imshow(array, norm=matplotlib.colors.LogNorm())
	
	# Don't plot NaN
	current_cmap = matplotlib.cm.get_cmap().copy()
	current_cmap.set_bad(color='white')

	# Plot colour bar
	cbar = plt.colorbar(fraction=0.0455, pad=0.1)
	if not plot_error:
		plt.clim(openarea_cut, 100)
		cbar.set_label('Open Area [%]')
	else:
		plt.clim(vmin=0, vmax=None) # Doesn't work with log scale
		cbar.set_label('Error count')

	plt.show()
	# Save figure
	plt.savefig("shit_%s_%s.png" % ("error" if plot_error else "openArea", link_name))
	plt.close()

# Now let's do the shit
df_dict = readBERFile(args.inputDir+"BER_summary.txt")

# Plot using tSNE
# plotTSNE(df_dict)
# plotTSNE(df_dict, only_good_points=True)

# Plot one shit
# plotHistShit(next(iter(df_dict.values())))
# plotHistShit(next(iter(df_dict.values())), plot_error=True) # Plot error count instead of open area

# Plot all shit
for link, df in df_dict.items():
	plotHistShit(df, link)

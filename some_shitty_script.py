#!/usr/bin/env python3 
import argparse

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

    # Reset index
    df_data.reset_index(inplace=True)

    # Do the TSNE dimensionality reduction
    tsne = TSNE(n_components=2, perplexity=20, n_iter=1000, learning_rate=200)
    tsne_results = tsne.fit_transform(df_data.values)

    # Convert results into dataframe
    df_results = pd.DataFrame(tsne_results, columns=['tsne-x','tsne-y'])
    df_results = df_results.join(df_data["Link"])

    # Plot the results
    plt.figure()

    sns.scatterplot(
        x="tsne-x", y="tsne-y",
        hue="Link",
        palette=sns.color_palette("hls", len(link_dict)),
        data=df_results,
        legend="full",
        alpha=0.3
    )

    # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()




# Now let's do the shit
df_dict = readBERFile(args.inputDir+"BER_summary.txt")

# Plot using tSNE
plotTSNE(df_dict)
plotTSNE(df_dict, only_good_points=True)

#!/usr/bin/env python3 
import argparse

import matplotlib.pyplot as plt
import pandas as pd

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

	df_dict = {} # Dictionary of dataframes, one per link

	file = open(file_name, "r") # Open file

	current_link = ""
	column_names = ["txDiff", "txPre", "txPost", "rxTerm", "txEq", "Bits", "Errors", "BER", "OpenA"] # Names of the columns, same as the values in BER_summary.txt except for OpenA

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


# Now let's do the shit
df = readBERFile(args.inputDir+"BER_summary.txt")

print(df)

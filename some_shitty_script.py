#!/usr/bin/env python3 

import matplotlib.pyplot as plt
import pandas as pd

# Reads a BER file and saves it as a pandas dataframe
def readBERFile(file_name):

	df = pd.DataFrame() # One DF per link??!

	file = open(file_name, "r") # Open file

	current_link = ""

	for line in file:

		# Update current link name
		if "Link " in line:
			current_link = line.split(" ")[-2]
			# Add link to dataframe
			if current_link not in df.index:
				df = df.append(row)

		elif "txDiff" in line:
			pd






	return df
# Results

This folder contains some results from running the scans. A summary of the scans for each run can be found in `configuration_summary.json`, and the bit rate error (BER) of every scan can be found in `BER_summary.txt`. For easier comparison, the `best_area_summary.json` saves one value with the best open area from the bathtub scan (Note: doesn't save multiple values if other settings give the same open area). All the settings with the largest open area that gives the lowest errors, are saved in `best_error_summary.json`.

## Plots

Plots created from the results using the `plotting_script.py` can be found in the `plots/` folders. The different types of plots are:
- `openA_error` shows a histogram of the open area with one bin for each configuration. The values printed in each bin are the number of errors that were measured.
- `good_links` shows the number of links with zero errors for each setting.
- `super_good_links` shows the number of links with zero errors and that meet the open area cut for each setting.
- `tsne` plots the multidimensional configuration data in a 2D plot, using the TSNE dimensionality reduction.


The file names contain some keywords that describe what the plots contain:
- `board` which board the scans were done on.
- `tx`/`rx` if the Tx or if the Rx settings were varied during the scans.
- `rxTerm` the rxTerm value that were used for the plot (in mV).
- `all` if all links are plotted in the same file.
- `unmasked` don't mask the histogram bins that contains errors and doesn't meet the open area cut.

## Data

Information about each seperate scan within a run can be found in the `data/` folder.

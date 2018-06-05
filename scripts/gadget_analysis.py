import os, sys
from matplotlib import pyplot as plt
from matplotlib import ticker as mtick
import numpy as np
import json

def read_program_gadgets_information(program):
    if os.path.isdir(program):
        with open( os.path.join(program, "gadget_occurences") ) as p:
            return json.load(p) # It's a list



root_dir = sys.argv[1]
output_dir = sys.argv[2]

rows = ["1", "10", "100", "1000"]
columns = ["diff", "registers", "sched"]

# Format
plt.rc("xtick", labelsize=8)
plt.rc("ytick", labelsize=8)
fig, axarr = plt.subplots(4, 3, sharey=True)

pad = 15
# Add column title
for ax, col in zip(axarr[0], columns):
    ax.set_title(
            {
                "diff": "enumerate",
                "registers": "registers",
                "sched": "schedule"
            }[col], pad=pad)

# Add the row labels and annotations
for ax, row in zip(axarr[:,0], rows):
    ax.set_ylabel(row, rotation=0, size='large', labelpad=pad)


# Get the actual data
for programs in os.listdir(root_dir):
    try:
        pieces = programs.split(".")
        strat, rate = pieces[1], pieces[2]
        row, column = rows.index(rate), columns.index(strat)
    except Exception as e:
        print("\"{}\" is not in the expected format \"program.<strat>.<rate>\"".format(programs))
        continue
    print("Processing {}.{}".format(strat, rate))
    data = read_program_gadgets_information(os.path.join(root_dir, programs))
    data.sort(reverse=True)
    #data = [d for d in data if d >= 1]


    axarr[row][column].set_yscale('log')
    axarr[row][column].yaxis.set_major_formatter(mtick.PercentFormatter())
    axarr[row][column].set_yticks( list(axarr[row][column].get_yticks()) + [max(data)] )
    axarr[row][column].set_xticks( [ 0, data.index(min(data)), int((len(data)/100))*100] ) # Round # of gadgets down to nearest 100
    axarr[row][column].plot(data, color="xkcd:burnt orange")#, width=0.8, snap=False)


    anno_x = data.index(max(data))
    anno_y = data[data.index(max(data))]
    axarr[row][column].annotate("{:.0f}%".format(anno_y), xy=(anno_x, anno_y), xytext=(anno_x+50, anno_y+30), verticalalignment="top")

for ax in axarr.flatten():
    ax.yaxis.set_tick_params(labelleft=True)
    for tk in ax.get_yticklabels():
        tk.set_visible(True)

# Save it
fig.tight_layout()
fig.set_size_inches(5.11911*1.1,8.26933*1.1) # The \textwidth and \textheight from latex scaled up slightly

plt.savefig(os.path.join(output_dir, "gadgets.png"))

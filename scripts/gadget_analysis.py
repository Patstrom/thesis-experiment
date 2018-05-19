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
fig, axarr = plt.subplots(4, 3, sharey=True, sharex=True)

pad = 15
# Add column title
for ax, col in zip(axarr[0], columns):
    ax.set_title(
            {
                "diff": "enum",
                "registers": "registers",
                "sched": "schedule"
            }[col], pad=pad)

# Add the row labels and annotations
for ax, row in zip(axarr[:,0], rows):
    ax.set_ylabel(row, rotation=0, size='large', labelpad=pad)

# Remove x-ticks. They don't say anything
# Format yaxis as percentage
for ax in fig.axes:
    #ax.xaxis.set_visible(False)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())


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
    ids = [x for x in range(len(data))]

    axarr[row][column].bar(ids, data)

# Save it
fig.tight_layout()
fig.set_size_inches(11.69,8.27)
plt.savefig(os.path.join(output_dir, "gadgets.png"))

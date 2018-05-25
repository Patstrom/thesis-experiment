import os
from matplotlib import pyplot as plt
import numpy as np
import json
import sys
from itertools import cycle, islice

root_dir = sys.argv[1]
output_dir = sys.argv[2]

with open(os.path.join(root_dir, "function_generation_times")) as f:
    times = json.load(f)

strat_times = {}
for key, t in times.items():
    pieces = key.split("--")
    function, strat = pieces[0], pieces[1]

    if strat_times.get(strat, None) is None:
        strat_times[strat] = [t]
    else:
        strat_times[strat].append(t)

for strat, times in strat_times.items():
    flat_list = [0]
    markers_on = []
    for function_times in times:
        flat_list.extend( [t + max(flat_list) for t in function_times] )
        markers_on.append( len(flat_list) - 1) # Marker at current index of flat_list

    # Every element in flat_list represents one solution.
    plt.plot([x / 1000 for x in flat_list], [x for x in range(len(flat_list))],
            label=strat.replace("diff", "enumerate").replace("sched", "shedule"),
            marker="D", markevery=markers_on)

plt.ylabel("Number of emitted solutions")
plt.xlabel("Time in seconds")
plt.legend()

plt.savefig(os.path.join(output_dir, "generator_time.png"))

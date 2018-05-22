import os
from matplotlib import pyplot as plt
import numpy as np
import sys

def read_version_cost(version):
    with open( os.path.join(version, "cost") ) as p:
        total_cost = 0
        for line in p:
            cost = int(line.split(":")[1])
            total_cost += cost
        return total_cost


def read_program_costs(program):
    costs = []
    for f in os.listdir(program):
        if os.path.isdir(os.path.join(program, f)):
            costs.append( read_version_cost( os.path.join(program, f) ) )
    return costs

root_dir = sys.argv[1]
output_dir = sys.argv[2]

costs = []
labels = []
llvm_cost = 0
schedule_median_cost = {}
all_strategies = [d for d in os.listdir(root_dir)]
all_strategies.sort()
for dirs in all_strategies:
    if dirs == "llvm":
        llvm_cost = read_version_cost( os.path.join(root_dir, dirs) )
        continue

    if os.path.isdir(os.path.join(root_dir, dirs)):
        program_cost = read_program_costs( os.path.join(root_dir, dirs) )
        program_label = dirs[dirs.index(".")+1:].replace("diff", "enumerate").replace("sched", "schedule")
        costs.append( program_cost )
        labels.append( program_label )

        if "sched" in program_label:
            schedule_median_cost[program_label] = np.median(program_cost)

fig = plt.figure()
#fig.set_size_inches(5.11911*1.1,8.26933*1.1*0.5) # The \textwidth and \textheight from latex scaled up slightly

bp = fig.add_subplot(111)
bp.boxplot(costs, whis="range")

# Set labels
bp.set_ylabel("Estimated cost (in cycles)")
xtickNames = plt.setp(bp, xticklabels=labels)
plt.setp(xtickNames, rotation=45, fontsize=8)

plt.axhline(y=llvm_cost, color="r", linestyle=":", label="llvm cost")
plt.legend()
fig.tight_layout()

plt.savefig(os.path.join(output_dir, "cost.png"))

import tabulate

headers = ["Sampling Rate", "Mean Est. Cost (cycles)", "Difference (cycles)", "Overhead (\\textperthousand)"]
table = []
for label, cost in schedule_median_cost.items():
    row = [label[label.rfind(".")+1:], int(cost), int(cost - llvm_cost), "{0:.6f}".format( ( float(cost) / llvm_cost - 1) * 1000 ) ]
    table.append(row)

tabulate.LATEX_ESCAPE_RULES={}
with open(os.path.join(output_dir, "sched_perf.tex"), "w+") as out:
    out.write(tabulate.tabulate(table, headers=headers, tablefmt="latex"))#, numalign="center", stralign="center"))

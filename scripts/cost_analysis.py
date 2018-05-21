import os
from matplotlib import pyplot as plt
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
all_strategies = [d for d in os.listdir(root_dir)]
all_strategies.sort()
for dirs in all_strategies:
    if dirs == "llvm":
        llvm_cost = [read_version_cost( os.path.join(root_dir, dirs) )]
        continue

    if os.path.isdir(os.path.join(root_dir, dirs)):
        costs.append( read_program_costs( os.path.join(root_dir, dirs) ) )
        labels.append( dirs[dirs.index("."):] )

fig = plt.figure()
fig.suptitle("Estimated cost of each program")

bp = fig.add_subplot(111)
bp.boxplot(costs)

# Set labels
bp.set_ylabel("cost")
xtickNames = plt.setp(bp, xticklabels=labels)
plt.setp(xtickNames, rotation=45, fontsize=8)

plt.axhline(y=llvm_cost, color="r", linestyle=":", label="llvm cost")
plt.legend()

plt.savefig(os.path.join(output_dir, "cost.png"))

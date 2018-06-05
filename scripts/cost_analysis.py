import os
from matplotlib import pyplot as plt
import numpy as np
import sys

def read_version_cost(version):
    costs = {}
    with open( os.path.join(version, "cost_speed") ) as p:
        f_cost = np.array([])
        for line in p:
            cost = int(line.split(":")[1])
            f_cost = np.append(f_cost, cost)
        costs["speed"] = f_cost.prod()**(1.0/len(f_cost))

    with open( os.path.join(version, "cost_size") ) as p:
        f_cost = np.array([])
        for line in p:
            cost = int(line.split(":")[1])
            f_cost = np.append(f_cost, cost)
        costs["size"] = f_cost.prod()**(1.0/len(f_cost))
    return costs


def read_program_costs(program):
    costs = {"size": [], "speed": []}
    for f in os.listdir(program):
        if os.path.isdir(os.path.join(program, f)):
            version_costs = read_version_cost( os.path.join(program, f) )
            costs["speed"].append( version_costs["speed"] )
            costs["size"].append( version_costs["size"] )
    return costs

root_dir = sys.argv[1]
output_dir = sys.argv[2]

speeds = []
sizes = []
labels = []
llvm_cost = {}
all_strategies = [d for d in os.listdir(root_dir)]
all_strategies.sort()
for dirs in all_strategies:
    if dirs == "llvm":
        llvm_cost = read_version_cost( os.path.join(root_dir, dirs) )
        continue

    if os.path.isdir(os.path.join(root_dir, dirs)):
        program_label = dirs[dirs.index(".")+1:].replace("diff", "enumerate").replace("sched", "schedule")

        program_cost = read_program_costs( os.path.join(root_dir, dirs) )
        speeds.append( program_cost["speed"] )
        sizes.append( program_cost["size"] )
        labels.append( program_label )


# speed
fig, speed_bp = plt.subplots(1,1)
#fig.suptitle("Distributions of the geometric mean between the estimated speed of each function in program versions")

speed_bp.boxplot(speeds, whis="range")
speed_bp.set_ylabel("Geometric mean of estimated speed (in cycles)")
speed_xtickNames = plt.setp(speed_bp, xticklabels=labels)
plt.setp(speed_xtickNames, rotation=45, fontsize=8)
speed_bp.axhline(y=llvm_cost["speed"], color="r", linestyle=":", label="Regular LLVM solution")
speed_bp.legend()

fig.tight_layout()
plt.savefig(os.path.join(output_dir, "cost_speed.png"))

# size
fig, size_bp = plt.subplots(1,1)
#fig.suptitle("Distributions of the geometric mean between the estimated size of each function in program versions")

size_bp.boxplot(sizes, whis="range")
size_bp.set_ylabel("Geometric mean of size (number of instructions)")
size_xtickNames = plt.setp(size_bp, xticklabels=labels)
plt.setp(size_xtickNames, rotation=45, fontsize=8)
size_bp.axhline(y=llvm_cost["size"], color="r", linestyle=":", label="Regular LLVM solution")
size_bp.legend()

fig.tight_layout()
plt.savefig(os.path.join(output_dir, "cost_size.png"))

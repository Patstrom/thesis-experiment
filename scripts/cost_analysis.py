import os
from matplotlib import pyplot as plt

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
        costs.append( read_version_cost( os.path.join(program, f) ) )
    return costs

costs = []
labels = []
all_strategies = [d for d in os.listdir("programs")]
all_strategies.sort()
for dirs in all_strategies:
    program_cost =  read_program_costs( os.path.join("programs", dirs) ) 
    costs.append( read_program_costs( os.path.join("programs", dirs) ) )
    labels.append( dirs[dirs.index("."):] )

fig = plt.figure()
fig.suptitle("Estimated cost of each program")

bp = fig.add_subplot(111)
bp.boxplot(costs)

# Set labels
bp.set_ylabel("cost")
xtickNames = plt.setp(bp, xticklabels=labels)
plt.setp(xtickNames, rotation=45, fontsize=8)


plt.show()

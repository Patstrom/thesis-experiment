import os
from matplotlib import pyplot as plt
import numpy as np
import json

def read_version_gadgets(version):
    with open( os.path.join(version, "gadgets") ) as p:
        gadgets = json.load(p)
    return gadgets

def read_program_gadgets(program):
    gadgets = []
    for f in os.listdir(program):
        gadgets.append( read_version_gadgets( os.path.join(program, f) ) )
    return gadgets

a = read_program_gadgets(os.path.join("programs", "program.diff.1"))
flat_a = [item for sublist in a for item in sublist]
ratio_a = [flat_a.count(item) / len(flat_a) for item in flat_a]
ratio_a.sort(reverse=True)
ids = [x for x in range(len(ratio_a))]

fig = plt.figure()
fig.suptitle("Occurence ratio for every gadget")

b = fig.add_subplot(111)
#b.hist(percentage_a, bins, histtype='bar', rwidth=0.5)
b.bar(ids, ratio_a)

b.set_ylabel("ratio")

plt.show()

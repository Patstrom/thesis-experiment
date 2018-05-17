# Experiment to test systematic diversity

## Repository structure
This repository contains everything needed to run the tests and get the results presented
in the thesis.

###  Data
The data directory contains all generated function versions in the following structure:

```
.
+-- data/
 | +-- programs/
 |  | +-- program.<strat>.<rate>
 |  |  | +-- <version_number>/
 |  |  |  | +-- <function_name>-<rate>.unison.mir
 |  |  |  | +-- cost
 |  |  |  | +-- gadgets
 |  |  | +-- <version_number>/
 |  |  |  | +-- <function_name>-<rate>.unison.mir
 |  |  |  | +-- cost
 |  |  |  | +-- gadgets
 |  |  | +-- <version_number>/
 |  |  |  | +-- <function_name>-<rate>.unison.mir
 |  |  |  | +-- cost
 |  |  |  | +-- gadgets
```

And so on. `<function_name>`, `<rate>`, `<version_number>` and `<strat>` are of course replaced
with the appropriate value. There are 1000 versions for each function (and thus 1000 program
versions).

The strategy refered to as `enumerate` in the thesis is called `diff`, `schedule` is called
`sched` and `registers` is called `registers`.

The sampling rates used are `1`, `10`, `100` and `1000`.

The `cost` file contains one key-value pair of <function_name> and cost (in cycles) on every
line. The `gadgets` file contains a json-serialized list of all gadgets present in the
program.

Note that the `cost` file is written during the data generation phase while the `gadgets`
file must be generated afterwards. All respective `gadgets` files are present in this repository

### Scripts

#### mirget

Mirget is a rust application that takes one a `program.<strat>.<rate>` directory as input
and writes all gadgets found to the file `program.<strat>.<rate>/gadgets`.

It is written in Rust and the easiest way to run it is through Cargo:

```Bash
cargo run --release program.<strat>.<rate>
```

For convenience the is a `mir_directory.sh` script to which you can give the `data/programs`
directory and it will run the command on all directories in that directory.

#### cost\_analysis
A python script to generate the boxplots visualizing the estimated cost of each program

#### gadget\_analysis
A python script to generate the bar graphs that visualizes frequence of gadgets in programs

### Plots


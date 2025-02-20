# Plate reader and analyzer for [Eric Greene (SFSU)'s lab](http://www.egreenelab.org/)

This code is part of a project screening a large library of metabolites for potential effects on the protein glutamine
synthetase.

It is a CLI designed to take as input a file output by the Agilent BioTek Synergy Neo2 plate reader and output the $K_m$
and $V_{max}$ of each reaction that took place.

For more information on the math and the enzymology, see `kinetics_modeling.md`. (If you somehow got here without being
an enzymologist, you may want to read the Wikipedia article on Michaelis-Menten kinetics first.)

## Usage

### Example

`python main.py 'input.txt' 'output.csv'` will take the data from the file `input.txt` and write data to the
file `output.csv`.

By default, this program assumes that you are running identical trials in groups of 4 adjacent wells, e.g. A1, A2, B1,
and B2. It will group these and average the concentrations of NADH in each well, discarding any outlier. If you do not
want this behavior, use the `--single-line` flag.

## Development

I recommend using `venv` or a similar tool to set up a virtual environment so you can install the requirements there.

To run tests, run `python -m unittest` or, better yet, `coverage -m unittest` (which, followed by `coverage -m` will
give a list of files with their total test coverage).

R_SQUARED_CUTOFF = 0.95
BYPASS_GRUBBS_TEST = True
SUPPRESS_REJECTED_FITS = False

# constants for non-linear curve fitting
# you probably only want to change these if you're changing the enzyme
# (e.g. running data for PK/LDH or ASS1)
ENZYME_CONCENTRATION = 1.14e-6  # see Benchling for [E]_0
STARTING_KCAT_ESTIMATION = 1.5
STARTING_K_M_ESTIMATION = 5e-5  # 50 µM

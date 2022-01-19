#!/usr/bin/env python
'''
CLEESE toolbox v1.0
mar 2018, J.J. Burred <jjburred@jjburred.com> for IRCAM/CNRS

Example configuration script.
'''

# main parameters
main_pars = {
    'outPath': './sounds/',   # output root folder
    'numFiles': 10,     # number of output files to generate (for random modifications)
    'chain': True,      # apply transformation in series (True) or parallel (False)
    'transf': ['eq'],   # transformations to apply
    'generateExpFolder': True  # generate experiment folder with name based on current time
}

# global analysis parameters
ana_pars = {
    'anaWinLen':   0.04,    # analysis window length in s (not to be confused with the BPF processing window lengths)
    'oversampling':   8,    # number of hops per analysis window
}


# parameters for random EQ
eq_pars = {
    'winLen': 0.1,
    'numWin': 1,
    'winUnit': 'n',
    'std': 5,
    'trunc': 1,
    'BPFtype': 'ramp',
    'trTime': 0.05,
    'scale': 'mel',   # mel, linear
    'numBands': 25
}

pars = {
    'main_pars': main_pars,
    'ana_pars': ana_pars,
    'eq_pars': eq_pars,
}

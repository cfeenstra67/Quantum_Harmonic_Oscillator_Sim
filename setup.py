#!/usr/local/bin/python3

import cx_Freeze as cx

executables=[cx.Executable('QM_demo.py')]

cx.setup(name='QM Demo',
    options={'build_exe':{'packages':['wx','numpy','matplotlib','sympy']}},
    description='Simulation intended for use as a demonstration in a Quantum Mechanics course.',
    executables=executables)
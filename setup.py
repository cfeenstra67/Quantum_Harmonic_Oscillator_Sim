#!/usr/local/bin/python3

from distutils.core import setup
import py2exe

setup(name='QM Demo',
    description='Simulation intended for use as a demonstration in a Quantum Mechanics course.',
    author='Cameron Feenstra',
    console=['QM_demo'])
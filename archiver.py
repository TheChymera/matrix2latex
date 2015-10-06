#!/usr/bin/env python
'''Utility script for creating a versioned .tar.gz of the documenentation and
the code for either matlab or python.
'''
import os

def callSystem(command):
    print '>' + command
    ret = os.system(command)
    if ret != 0:
        print 'Command failed, exiting'
        exit(1)

version = '1.0.0'

# Ensure tests pass
callSystem('cd test;nosetests-2.7 test.py')
callSystem('cd test;python testVersionCompatibility.py')
# Re-create doc if neccesary
callSystem('cd doc;latexmk -pdf doc.tex')

include_common = ' doc README.md '

python_name = 'archive/matrix2latexPython'
include_files = 'matrix2latex setup.py' + include_common
callSystem('git archive --format=tar --prefix={name}{v}/ HEAD {include} | gzip > {name}-{v}.tar.gz'.format(name=python_name,
                                                                                                           v=version,
                                                                                                           include=include_files))

matlab_name = 'archive/matrix2latexMatlab'
include_files = 'src_matlab' + include_common
callSystem('git archive --format=tar --prefix={name}{v}/ HEAD {include} | gzip > {name}-{v}.tar.gz'.format(name=matlab_name,
                                                                                                           v=version,
                                                                                                           include=include_files))

callSystem('git add {p_name}-{v}.tar.gz {m_name}-{v}.tar.gz'.format(p_name=python_name,
                                                                    m_name=matlab_name,
                                                                    v=version))

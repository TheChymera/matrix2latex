# Tries to run testsuit with python version
# python<major>.<minor>
# where major and minor varies between 2-3 and 0-10.
# (expand this if you have say python1.11 or python4.0)

import os
from subprocess import call
from matrix2latex import matrix2latex

table = list()
cl = list()

for major in range(2, 3+1):
    for minor in range(0, 10):
        python = 'python%d.%d' % (major, minor)

        if call(python + " -c ''", shell=True, stderr=file(os.devnull, "w")) == 0:
            ret = call(python + " test.py", shell=True)

            print(python)            
            print(ret)
            if ret == 0: table.append(["True"])
            else: table.append(["False"])
            cl.append(python)
compatibleTable = matrix2latex(table, 'doc/compatibleTable', columnLabels=cl, rowLabels=['Compatible'])
print compatibleTable

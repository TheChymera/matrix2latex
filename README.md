[![Build Status](https://travis-ci.org/TheChymera/matrix2latex.svg?branch=master)](https://travis-ci.org/TheChymera/matrix2latex)
Matrix2LaTeX
============
Takes a Python or MATLAB matrix and outputs a LaTeX table, a LaTeX matrix, or a complete LaTeX document (and optionally calls `latex` for compilation).
A number of configuration options are available. 
The default table output is geared towards the standard recommended by IEEE, and uses the latex package booktabs.
Check out the [documentation](https://github.com/TheChymera/matrix2latex/raw/master/doc/doc.pdf "doc.pdf") for more example output and usage.

Example
-------
The following python code:
```python
from matrix2latex import matrix2latex
m = [[1, 1], [2, 4], [3, 9]] # python nested list
t = matrix2latex(m)
print t
```
or equivalent matlab code:
```matlab
m = [1, 1; 2, 4; 3, 9];
filename = '' % do not write to file
t = matrix2latex(m, filename)
```
produces
```latex
\begin{table}[ht]
  \begin{center}
    \begin{tabular}{cc}
      \toprule
        $1$ & $1$\\
        $2$ & $4$\\
        $3$ & $9$\\
      \bottomrule
    \end{tabular}
  \end{center}
\end{table}
```

![alt text](https://github.com/TheChymera/matrix2latex/raw/master/simpleExample.png "Example table, latex output.")

Various options are available to change the latex environment (e.g. to a matrix) or to provide
header, footer, caption, label, format and/or alignment. Please see the [documentation](https://github.com/TheChymera/matrix2latex/raw/master/doc/doc.pdf "doc.pdf") for details.

History
-------
Inspired by the work of koehler@in.tum.de who has written
a similar package only for matlab
http://www.mathworks.com/matlabcentral/fileexchange/4894-matrix2latex

This project was moved from https://code.google.com/p/matrix2latex/
after code.google.com was discontinued.

Future goals
------------
Feel free to contribute to any of the following improvements
or open an [issue](https://github.com/TheChymera/matrix2latex/issues) if you want something done.

* Clean up the code (object oriented?)
* Make the matlab version identical to the python version
* Add support for more advanced tables. Highlights and multirow.
* Command line interface (say, read in a csv, take arguments on the command line)
* Additional languages (R/perl/julia?)

Author
------
Øystein Bjørndal

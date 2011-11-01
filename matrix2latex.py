from numpy import *
import sys
import os.path
from StringIO import StringIO

# my stuff:
import fixEngineeringNotation
from error import *                     # error handling
# For sagetex the function must return string instead of writing to file or to stdout
#from myString import StringWithWrite

def matrix2latex(matr, filename=None, *environments, **keywords):
    r'''
A pdf version of this documentation is available as doc<date>.pdf
Takes a python matrix or nested list and converts to a LaTeX table or matrix.
Author: ob@cakebox.net, inspired by the work of koehler@in.tum.de who has written
a similar package for matlab
\url{http://www.mathworks.com/matlabcentral/fileexchange/4894-matrix2latex}

This software is published under the GNU GPL, by the free software
foundation. For further reading see: 
\url{http://www.gnu.org/licenses/licenses.html#GPL}

The following packages and definitions are recommended in the latex preamble 
% scientific notation, 1\e{9} will print as 1x10^9
\providecommand{\e}[1]{\ensuremath{\times 10^{#1}}}
\usepackage{amsmath} % needed for pmatrix
\usepackage{booktabs} % Fancy tables
...
\begin{document}
...

Arguments:
  
matrix
  A numpy matrix or a nested list
  TODO:
\begin{itemize}
\item Any python structure that looks like a rektangular matrix.
\item Remove dependency on numpy (might be more portable to other systems)
\end{itemize}

Filename
  File to place output, extension .tex is added automatically. File can be included in a LaTeX
  document by \verb!\input{filename}!. If filename is None or not a string, output will be returned in a string
  
*environments
  Use 
matrix2latex(m, None, "align*", "pmatrix", ...) for matrix.
  This will give
  \begin{align*}
    \begin{pmatrix}
      1 & 2 \\
      3 & 4
    \end{pmatrix}
  \end{align*}
  Use 
matrix2latex(m, "test", "table", "center", "tabular" ...) for table.
  Table is default so given no arguments: table, center and tabular will be used.
  The above command is then equivalent to \\
matrix2latex(m, "test", ...)

Example

  from matrix2latex import matrix2latex
  m = [[1, 2, 3], [1, 4, 9]] # python nested list
  t = matrix2latex(m)
  print t

\begin{lstlisting}
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
\end{lstlisting}


**keywords
rowLabels
    A row at the top used to label the columns.
    Must be a list of strings.

Using the same example from above we can add row labels

rl = ['$x$', '$x^2$']
t = matrix2latex(m, rowLabels=rl)



columnLabels
    A column used to label the rows.
    Must be a list of strings

transpose
Flips the table around in case you messed up. Equivalent to
matrix2latex(m.H, ...)
if m is a numpy matrix.
Note the use of columnLabels in the example.
cl = ['$x$', '$x^2$']
t = matrix2latex(m, columnLabels=cl, transpose=True)



caption
    Use to define a caption for your table.
    Inserts \verb!\caption! after \verb!\end{tabular}!.
Always use informative captions!

t = matrix2latex(m, rowLabels=rl, 
                 caption='Nice table!')



label
Used to insert \verb!\label{tab:...}! after \verb!\end{tabular}!
Default is filename without extension.

We can use label='niceTable' but if we save it to file
the default label is the filename, so:

matrix2latex(m, 'niceTable', rowLabels=rl, 
                 caption='Nice table!')

can be referenced by \verb!\ref{tab:niceTable}!. Table \ref{tab:niceTable}
was included in latex by \verb!\input{niceTable}!.

format
Printf syntax format, e.g. $%.2f$. Default is $%g$.
  This format is then used for all the elements in the table.

m = [[1, 2, 3], [1, 1/2, 1/3]]
rl = ['$x$', '$1/x$']
t = matrix2latex(m, rowLabels=rl,
                 format='%.2f')

  
formatColumn
A list of printf-syntax formats, e.g. [$%.2f$, $%g$]
Must be of same length as the number of columns.
Format i is then used for column i.
This is useful if some of your data should be printed with more significant figures
than other parts

t = matrix2latex(m, rowLabels=rl,
                 formatColumn=['%g', '%.2f'])


alignment
Used as an option when tabular is given as enviroment.
\verb!\begin{tabular}{alignment}!
A latex alignment like c, l or r.
Can be given either as one per column e.g. "ccc".
Or if only a single character is given e.g. "c",
it will produce the correct amount depending on the number of columns.
Default is "r".

Note that many of these options only has an effect when typesetting a table,
if the correct environment is not given the arguments are simply ignored.

The options presented by this program represents what I need when creating a table,
if you need a more sophisticated table you must either change the python code
(feel free to submit a patch) or manually adjust the output afterwards.
\url{http://en.wikibooks.org/wiki/LaTeX/Tables} gives an excellent overview
of some advanced table techniques.
    '''
    #
    # Check for numpy matrix
    #
    if not isinstance(matr, matrix):
        matr = matrix(matr).H
    if 'transpose' in keywords:
        if keywords['transpose']:
            matr = matr.H
    #
    # Define matrix-size
    # 
    m = size(matr, 0)
    n = size(matr, 1)
    assert m > 0 and n > 0,\
           "Expected positive matrix dimensions, got %g by %g matrix" % (m, n)
    if "formatColumns" in keywords:
        n += 1
    #
    # Default values
    #
    # Keywords
    formatNumber = "$%g$"
    formatColumn = None

    if "formatColumns" in keywords:
        alignment = "c" + "c"*(n-1)    # c|cccc
    else:
        alignment = "c"*n               # cccc
    
    rowLabels = None
    columnLabels = None
    caption = None
    label = None

    #
    # User-defined values
    # 
    for key in keywords:
        value = keywords[key]
        if key == "format":
            assertKeyFormat(value)
            formatNumber = value
            formatColumn = None         # never let both formatColumn and formatNumber to be defined
        elif key == "formatColumn":
            formatColumn = value
            formatNumber = None
        elif key == "alignment":
            if len(value) == 1:
                if "formatColumns" in keywords: alignment = value+"" + value*(n-1) # r|rrrr
                else: alignment = value*n # rrrr
            else:
                alignment = value
            assertKeyAlignment(alignment, n)
        elif key == "rowLabels":
            assertListString(value, "rowLabels")
            rowLabels = list(value)
        elif key == "columnLabels":
            assertListString(value, "columnLabels")
            columnLabels = list(value)
            alignment = "r" + alignment
        elif key == "caption":
            assertStr(value, "caption")
            caption = value
        elif key == "label":
            assertStr(value, "label")
            if value.startswith('tab:'):
                label = value[len('tab:'):] # this will be added later in the code, avoids 'tab:tab:' as label
            else:
                label = value
        elif key == "transpose":
            pass                        # already taken care of (top of function)
        else:
            sys.stderr.write("Error: key not recognized '%s'\n" % key)
            sys.exit(2)

    # Environments
    if len(environments) == 0:          # no environment give, assume table
        environments = ("table", "center", "tabular")

    if formatColumn == None:
        formatColumn = list()
        for j in range(0, n):
            formatColumn.append(formatNumber)

    if columnLabels != None and rowLabels != None and len(rowLabels) == n:
        rowLabels.insert(0, "")

    # 
    # Set outputFile
    # 
    if isinstance(filename, str):
        if not filename.endswith('.tex'): # assure propper file extension
            filename += '.tex'
        f = open(filename, 'w')
        if label == None:
            label = os.path.basename(filename) # get basename
            label = label.replace(".tex", "")  # remove extension. TODO: bug with filename=foo.texFoo.tex
    else:                               # if filename is not given or of invalid type, 
        f = StringIO()#StringWithWrite()
        #f = sys.stdout         # print to screen

    #
    # Begin block
    # 
    for ixEnv in range(0, len(environments)):
        f.write("\t"*ixEnv)
        f.write(r"\begin{%s}" % environments[ixEnv])
        # special environments:
        if environments[ixEnv] == "table":
            f.write("[ht]")
        elif environments[ixEnv] == "center":
            if caption != None:
                f.write("\n"+"\t"*ixEnv)
                f.write("\\caption{%s}" % fixEngineeringNotation.fix(caption))
            if label != None:
                f.write("\n"+"\t"*ixEnv)
                f.write("\\label{tab:%s}" % label)
        elif environments[ixEnv] == "tabular":
            f.write("{" + alignment + "}\n")
            f.write("\t"*ixEnv)
            f.write(r"\toprule")
        # newline
        f.write("\n")
    tabs = len(environments)            # number of \t to use

    # 
    # Table block
    # 

    # Row labels
    if rowLabels != None:
        f.write("\t"*tabs)
        for j in range(0, len(rowLabels)):
            f.write(r"%s" % rowLabels[j])
            if j != len(rowLabels)-1:
                f.write(" & ")
            else:
                f.write(r"\\"+ "\n")
                f.write("\t"*tabs)
                f.write(r"\midrule" + "\n")
                
    # Values
    for i in range(0, m):
        f.write("\t"*tabs)
        for j in range(0, n):

            if j == 0:                  # first row
                if columnLabels != None:
                    f.write("%s & " % columnLabels[i])
                    
            if '%s' not in formatColumn[j]:
                try:
                    e = float(matr[i, j])            # current element
                except ValueError: # can't convert to float, use string
                    e = matr[i, j]
                    formatColumn[j] = '%s'
                except TypeError:       # raised for None
                    e = None
            else:
                e = matr[i, j]

            if e == None:
                f.write("NaN")
            elif e == inf:
                f.write(r"$\infty$")
            else:
                fcj = formatColumn[j]
                formated = fcj % e
                formated = fixEngineeringNotation.fix(formated, table=True) # fix 1e+2
                f.write(formated)
            if j != n-1:                # not last row
                f.write(" & ")
            else:                       # last row
                f.write(r"\\")
                f.write("\n")

    #
    # End block
    #
    for ixEnv in range(0, len(environments)):
        ixEnv = len(environments)-1 - ixEnv # reverse order
        # special environments:
        if environments[ixEnv] == "center":
            pass
        elif environments[ixEnv] == "tabular":
            f.write("\t"*ixEnv)
            f.write(r"\bottomrule"+"\n")
        f.write("\t"*ixEnv)
        f.write(r"\end{%s}" % environments[ixEnv])
        if ixEnv != 0:
            f.write("\n")

    # Return string representation of file
    if isinstance(f, StringIO):
        ret = f.getvalue()
    else:
        ret = ''
        
    f.close()

    return ret

if __name__ == '__main__':
    m = matrix('1 2 4;3 4 6')
    m = matrix('1 2 4;2 2 1;2 1 2')
    print(matrix2latex(m))
    print(matrix2latex(m, 'tmp.tex'))
    print(matrix2latex(m, None, "table", "center", "tabular", format="$%.2f$", alignment='lcr'))
    cl = ["a", "b", "c"]
    rl = ['d', 'e', 'f', 'g']
    print(matrix2latex(m, None, format="$%.2g$", alignment='lcr',
                 columnLabels=cl,caption="test", label="2", rowLabels=rl))
    print(matrix2latex(matrix(m), None, "align*", "pmatrix", format="%g", alignment='c'))
    print(matrix2latex(m, None, columnLabels=cl, caption="Hello", label="la"))
    print(matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s'))

    m = [[1,None,None], [2,2,1], [2,1,2]]
    print(matrix2latex(m, transpose=True))

    # TODO:
#     m = [[1], [2,2,1], [2,1,2]]
#     print matrix2latex(m, transpose=True)

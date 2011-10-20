from numpy import *
import sys
# my stuff:
import fixEngineeringNotation
from error import *                     # error handling
# For sagetex the function must return string instead of writing to file or to stdout
from myString import StringWithWrite

def matrix2latex(matr, filename=None, *environments, **keywords):
    r'''
    TODO: update documentation (lots of undocumented features)
    Takes a python matrix or nested list and converts to a LaTeX table or matrix.
    Author: ob@cakebox.net

    This software is published under the GNU GPL, by the free software
    foundation. For further reading see: http://www.gnu.org/licenses/licenses.html#GPL

    Argument:
    
    matrix:
    A numpy matrix or a nested list
    TODO:
    Any python structure that looks like a rektangular matrix.
    
    filename:
    File to place output, extension .tex is added automatically. File can be included in a LaTeX
    document by \input{filename}. If filename is None or not a string, output will be returned in a string
    
    *environments:
    Use matrix2latex(m, None, "align*", "pmatrix", ...) for matrix.
    This will give
    \begin{align*}
    \t\begin{pmatrix}
    \t\t...
    \t\end{pmatrix}
    \end{align*}
    Use matrix2latex(m, "test", "table", "center", "tabular" ...) for table.
    Table is default so given no arguments: table, center and tabular will be used.
    The above command is then equivalent to
    matrix2latex(m, "test", ...)
    
    **keywords:
    format:
    Printf-syntax format, e.g. $%.2f$. Default is $%g$.
    This format is then used for all the elements in the table.
    
    formatColumn:
    A list of printf-syntax formats, e.g. [$%.2f$, $%g$]
    Must be of same length as the number of columns.
    Format i is then used for column i.
    
    alignment:
    Used as an option when tabular is given as enviroment.
    \begin{tabular}{alignment}
    A latex alignment like c, l or r.
    Can be given either as one per column e.g. "ccc".
    Or if only a single character is given e.g. "c",
    it will produce the correct amount depending on the number of columns.
    Default is "r".

    rowLabels:
    A row at the top used to label the columns.
    Must be a list of strings.

    columnLabels:
    A column used to label the rows.
    Must be a list of strings

    caption:
    Use to define a caption for your table.
    Inserts \caption after \end{tabular}.

    label:
    Used to insert \label{...} after \end{tabular}
    Default is filename without extension.
    
    Example: todo: test
    m = matrix("1 2 4;3 4 6") # or
    m = [[1, 2, 4], [3, 4, 6]]
    matrix2latex(m, "test", "table", "center", "tabular", format="$%.2f$", alignment="lcr")
    produces:
    \begin{table}[ht]
      \begin{center}
        \begin{tabular}{lcr}
          $1.00$ & $2.00$ & $4.00$\\
          $3.00$ & $4.00$ & $6.00$\\
        \end{tabular}
      \end{center}
    \end{table}
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
            label = filename.replace(".tex", "")
    else:                               # if filename is not given or of invalid type, 
        f = StringWithWrite()
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
                f.write("\\label{%s}" % label)
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
        f.write("\n")

    # Return string representation of file
    try:
        f.close()
    except AttributeError:
        pass
    return f.__str__()

if __name__ == '__main__':
    from numpy import *
    m = matrix('1 2 4;3 4 6')
    m = matrix('1 2 4;2 2 1;2 1 2')
    print matrix2latex(m),
    print matrix2latex(m, 'tmp.tex')
    print matrix2latex(m, None, "table", "center", "tabular", format="$%.2f$", alignment='lcr')
    cl = ["a", "b", "c"]
    rl = ['d', 'e', 'f', 'g']
    print matrix2latex(m, None, format="$%.2g$", alignment='lcr',
                 columnLabels=cl,caption="test", label="2", rowLabels=rl)
    print matrix2latex(matrix(m), None, "align*", "pmatrix", format="%g", alignment='c')
    print matrix2latex(m, None, columnLabels=cl, caption="Hello", label="la")
    print matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s')

    m = [[1,None,None], [2,2,1], [2,1,2]]
    print matrix2latex(m, transpose=True)

"""This file is part of matrix2latex.

matrix2latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

matrix2latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with matrix2latex. If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import os.path
import warnings
import math
import re
def isnan(e):
    try:
        return math.isnan(e)
    except (TypeError, AttributeError):
        return e == float("nan")

from fixEngineeringNotation import fix
from error import *                     # error handling
from IOString import IOString
# Definitions
# Matrix environments where alignment can be utilized. CHECK: Note alignment[0] used!
matrix_alignment = ["pmatrix*","bmatrix*","Bmatrix*","vmatrix*","Vmatrix*"] # Needs mathtools package
# Table environments where alignment can be utilized
table_alignment = ["tabular", "longtable"]
    
def matrix2latex(matr, filename=None, *environments, **keywords):
    r'''
    Takes a python matrix or nested list and converts to a LaTeX table or matrix.
    Author: ob@cakebox.net, inspired by the work of koehler@in.tum.de who has written
    a `similar package for 
    matlab <http://www.mathworks.com/matlabcentral/fileexchange/4894-matrix2latex>`_

    The following packages and definitions are recommended in the latex preamble

    .. code-block:: latex

      \providecommand{\e}[1]{\ensuremath{\times 10^{#1}}} % scientific notation, 1\e{9} will print as 1x10^9
      \usepackage{amsmath} % needed for pmatrix
      \usepackage{booktabs} % Fancy tables
      ...
      \begin{document}
      ...

    :param list matr: The numpy matrix/array or a nested list to convert.

    :param str filename: File to place output, extension .tex is added automatically. File can be included in a LaTeX
      document by ``\input{filename}``. If filename is None
      or not a string it is ignored.

    :arg environments: A list specifing the begin and end block.
        Example: ``matrix2latex(m, None, "align*", "pmatrix")`` gives the matrix

        .. code-block:: latex

            \begin{align*}
                \begin{pmatrix}
                   1 & 2 \\
                   3 & 4
                \end{pmatrix}
            \end{align*}

        The default is generating a table using the ``table``, ``center`` and ``tabular``
        environment, hence
        ``matrix2latex(m, "test", "table", "center", "tabular" ...)``
        can be written as
        ``matrix2latex(m, "test", ...)``

    :key headerRow:
        A row at the top used to label the columns.
        Must be a list of strings. Can be a nested list for multiple headings.
        If two or more items are repeated, a multicolumn is inserted, so:
        ``headerRow=['a', 'a']``
        will produces ``\multicolumn{2}{c}{Item}`` with an appropriate cmidrule beneath.
        To avoid this behavior ensure each consecutive item is unique, for instance:
        ``headerRow=['a', 'a ']``
        will produces the expected ``a & a`` (note the space after the second ``a``).

    :key headerColumn:
        A column used to label the rows. 
        Must be a list of strings

    :key transpose:
        Flips the table around in case you messed up. Equivalent to
        ``matrix2latex(m.H, ...)``
        if m is a numpy matrix.

    :key caption:
        Use to define a caption for your table.
        Inserts ``\caption`` after ``\begin{center}``,
        note that without the center environment the caption is currently ignored.

    :key label:
        Used to insert ``\label{tab:...}`` after ``\end{tabular}``
        Default is filename without extension.

    :key format:
        Printf syntax format, e.g. ``$%.2f$``. Default is ``$%g$``.
        This format is then used for all the elements in the table.

    :key formatColumn:
        A list of printf-syntax formats, e.g. ``[$%.2f$, $%g$]``
        Must be of same length as the number of columns.
        Format i is then used for column i.
        This is useful if some of your data should be printed with more significant figures
        than other parts.

    :key alignment:
        Used as an option when tabular is given as enviroment.
        ``\begin{tabular}{alignment}``
        A latex alignment like ``c``, ``l`` or ``r``.
        Can be given either as one per column e.g. ``"ccc"``.
        Or if only a single character is given e.g. ``"c"``,
        it will produce the correct amount depending on the number of columns.
        Default is ``"r"``.

    :key position:
        Used for the table environment to specify the optional parameter "position specifier"
        Default is ``'[' + 'htp' + ']'``
        If you want to place your table manually, do not use the table environment.

    Note that many of these options only has an effect when typesetting a table,
    if the correct environment is not given the arguments are simply ignored.
    
    :return str table:
      Returns the latex formated output as a string.
    '''
    headerRow = None
    headerColumn = None

    #
    # Convert to list
    #
    # If pandas
    try:
        headerColumn = list(matr.index)
    except (AttributeError, TypeError):
        pass
    try:
        headerRow = [list(matr.columns)]
    except (AttributeError, TypeError):
        pass
    try:
        matr = matr.to_records(index=False)
    except AttributeError:
        pass
    # If numpy (vops: must be placed below pandas check)
    try:
        matr = matr.tolist()
    except AttributeError:
        pass # lets hope it looks like a list

    #
    # Define matrix-size
    # 
    m = len(matr)
    try:
        n = len(matr[0]) # may raise TypeError
        for row in matr:
            n = max(n, len(row)) # keep max length
    except TypeError: # no length in this dimension (vector...)
        # convert [1, 2] to [[1], [2]]
        newMatr = list()
        [newMatr.append([matr[ix]]) for ix in range(m)]
        matr = newMatr
        m = len(matr)
        n = len(matr[0])
    except IndexError:
        m = 0
        n = 0
    #assert m > 0 and n > 0, "Expected positive matrix dimensions, got %g by %g matrix" % (m, n)
#   Bug with transpose:
#     # If header and/or column labels are longer use those lengths
#     try:
#         m = max(m, len(keywords['headerColumn'])) # keep max length
#     except KeyError:
#         pass
#     try:
#         n = max(n, len(keywords['headerRow'])) # keep max length
#     except KeyError:
#         pass
    
    #
    # Default values
    #

    # Keywords
    formatNumber = "$%g$"
    formatColumn = None
    if n != 0:
        alignment = "c"*n               # cccc
    else:
        alignment = "c"

    caption = None
    label = None
    position = "htp"            # position specifier for floating table environment

    # 
    # Conflicts
    #
    if "format" in keywords and "formatColumn" in keywords:
        warnings.warn('Specifying both format and formatColumn is not supported, using formatColumn')
        del keywords["format"]
        
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
                alignment = value*n # rrrr
            else:
                alignment = value
            assertKeyAlignment(alignment, n)
        elif key == "headerRow":
            if value == None:
                headerRow = None
            else:
                if not(type(value[0]) == list):
                    value = [value]         # just one header
                #assertListString(value, "headerRow") # todo: update
                headerRow = list(value)
        elif key == "headerColumn":
            if value == None:
                headerColumn = None
            else:
                assertListString(value, "headerColumn")
                headerColumn = list(value)
        elif key == "caption":
            assertStr(value, "caption")
            caption = value
        elif key == "label":
            assertStr(value, "label")
            if value.startswith('tab:'):
                label = value[len('tab:'):] # this will be added later in the code, avoids 'tab:tab:' as label
            else:
                label = value
        elif key == "filename":
            assertStr(value, "filename")
            filename = value
        elif key == "position":
            assertStr(value, "position")
            position = value
        elif key == "environments":
            environments = value
        elif key == "transpose":
            newMatr = list(zip(*matr))
#             for j in range(0, n):
#                 row = list()
#                 for i in range(0, m):
#                     row.append(matr[i][j])
#                 newMatr.append(row)
            copyKeywords = dict(keywords) # can't del original since we are inside for loop.
            del copyKeywords['transpose']
            # Recursion!
            return matrix2latex(newMatr, filename, *environments, **copyKeywords)
        else:
            raise ValueError("Error: key not recognized '%s'" % key)

    if headerColumn != None:
        alignment = "r" + alignment

    # Environments
    if environments is None:    # environments=None passed, do not add any environments.
        environments = []
    elif len(environments) == 0: # no environment give, assume table
        environments = ("table", "center", "tabular")

    if formatColumn == None:
        formatColumn = list()
        for j in range(0, n):
            formatColumn.append(formatNumber)

    if headerColumn != None and headerRow != None and len(headerRow[0]) == n:
        for i in range(len(headerRow)):
            headerRow[i].insert(0, "")

    # 
    # Set outputFile
    # 
    f = None
    if isinstance(filename, str) and filename != '':
        if not filename.endswith('.tex'): # assure propper file extension
            filename += '.tex'
        f = open(filename, 'w')
        if label == None:
            label = os.path.basename(filename) # get basename
            label = label[:-len(".tex")]  # remove extension

    f = IOString(f)
    #
    # Begin block
    # 
    for ixEnv in range(0, len(environments)):
        f.write("\t"*ixEnv)
        f.write(r"\begin{%s}" % environments[ixEnv])
        # special environments:
        if environments[ixEnv] == "table":
            f.write("[" + position + "]")
        elif environments[ixEnv] == "center":
            if caption != None:
                f.write("\n"+"\t"*ixEnv)
                f.write(r"\caption{%s}" % fix(caption))
            if label != None:
                f.write("\n"+"\t"*ixEnv)
                f.write(r"\label{tab:%s}" % label)
        elif environments[ixEnv] in table_alignment:
            f.write("{" + alignment + "}\n")
            f.write("\t"*ixEnv)
            f.write(r"\toprule")
        elif environments[ixEnv] in matrix_alignment:
            f.write("[" + alignment[0] + "]\n") #These environment you can add
        # newline
        f.write("\n")
    tabs = len(environments)            # number of \t to use

    # 
    # Table block
    # 

    # Row labels
    if headerRow != None:
        for row in range(len(headerRow)): # for each header
            i = 0
            start, end = list(), list() # of cmidrule
            f.write("\t"*tabs)    
            while i < len(headerRow[row]): # for each element (skipping repeating ones)
                j = 1
                # check for legal index then check if current element is equal to next (repeating)
                repeating = i+j < len(headerRow[row]) and headerRow[row][i] == headerRow[row][i + j]
                if repeating:
                    while repeating:        # figure out how long it repeats (j)
                        j += 1
                        repeating = i+j < len(headerRow[row]) and headerRow[row][i] == headerRow[row][i + j]
                    f.write(r'\multicolumn{%d}{c}{%s}' % (j, headerRow[row][i])) # multicol heading
                    start.append(i);end.append(j+i)
                    i += j                 # skip ahed
                else:
                    f.write('{%s}' % headerRow[row][i]) # normal heading
                    i += 1
                if i < len(headerRow[row]): # if not last element
                    f.write(' & ')
                    
            f.write(r'\\')
            for s, e in zip(start, end):
                f.write(r'\cmidrule(r){%d-%d}' % (s+1, e))
            f.write('\n')
        if len(start) == 0:             # do not use if cmidrule is used on last header
            f.write('\t'*tabs)
            f.write('\\midrule\n')

    # Values
    for i in range(0, m):
        f.write("\t"*tabs)
        for j in range(0, n):

            if j == 0:                  # first row
                if headerColumn != None:
                    try:
                        f.write("{%s} & " % headerColumn[i])
                    except IndexError:
                        f.write('&')

            try: # get current element
                if '%s' not in formatColumn[j]:
                    try:
                        e = float(matr[i][j]) # current element
                    except ValueError: # can't convert to float, use string
                        formatColumn[j] = '%s'
                        e = matr[i][j]
                    except TypeError:       # raised for None
                        e = None
                else:
                    e = matr[i][j]
            except IndexError:
                e = None
                
            if e == None or isnan(e):#e == float('NaN'):
                f.write("{-}")
            elif e == float('inf'):
                f.write(r"$\infty$")
            elif e == float('-inf'):
                f.write(r"$-\infty$")                
            else:
                fcj = formatColumn[j]

                formated = fcj % e
                formated = fix(formated, table=True) # fix 1e+2
                f.write('%s' % formated)
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

    f.close()
    return f.__str__()

if __name__ == '__main__':
#     m = matrix('1 2 4;3 4 6')
#     m = matrix('1 2 4;2 2 1;2 1 2')
    m = [[1, 2, 3], [3, 4, 5]]
    print(matrix2latex(m))
    print(matrix2latex(m, 'tmp.tex'))
    print(matrix2latex(m, None, "table", "center", "tabular", format="$%.2f$", alignment='lcr'))
    cl = ["a", "b", "c"]
    rl = ['d', 'e', 'f', 'g']
    print(matrix2latex(m, None, format="$%.2g$", alignment='lcr',
                 headerColumn=cl,caption="test", label="2", headerRow=rl))
    print(matrix2latex(m, None, "align*", "pmatrix", format="%g", alignment='c'))
    print(matrix2latex(m, None, headerColumn=cl, caption="Hello", label="la"))
    print(matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s'))

    m = [[1,None,None], [2,2,1], [2,1,2]]
    print(matrix2latex(m, transpose=True))

    # TODO:
#     m = [[1], [2,2,1], [2,1,2]]
#     print matrix2latex(m, transpose=True)

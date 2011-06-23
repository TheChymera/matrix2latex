import sys

def matrix2latex(matrix, filename=None, *environments, **keywords):
    #
    # Define matrix-size
    # 
    m = size(matrix, 0)                 # rows
    n = size(matrix, 1)                 # columns

    #
    # Default values
    #
    # Keywords
    formatNumber = "$%g$"
    alignment = "c"*n

    # Environments
    if len(environments) == 0:          # no environment give, assume table
        environments = ("table", "center", "tabular")
    
    #
    # User-defined values
    # 
    for key in keywords:
        value = keywords[key]
        if key == "format":
            assert isinstance(value, str), \
                   "expected type of format is str, got %s" % type(value)
            assert r"%" in value, \
                   "expected a format str, got %s" % value
            formatNumber = value
        elif key == "alignment":
            assert isinstance(value, str), \
                   "expected type of alignment is str, got %s" % type(value)
            assert ("c" in value or "l" in value or "r" in value), \
                   "expected legal alignment c, l or r, got %s" % value
            if len(value) == 1:
                alignment = value*n
            elif len(value) != n:
                sys.stderr.write("Error: to few alignments given '%s'\n" % alignment)
                exit(1)
            else:
                alignment = value
    # 
    # Set outputFile
    # 
    if isinstance(filename, str):
        if not filename.endswith('.tex'): # assure propper file extension
            filename += '.tex'
        f = open(filename, 'w')
    else:                               # if filename is not given or of invalid type, 
        f = sys.stdout         # print to screen

    #
    # Begin block
    # 
    for ixEnv in range(0, len(environments)):
        f.write("\t"*ixEnv)
        f.write(r"\begin{%s}" % environments[ixEnv])
        # special environments:
        if environments[ixEnv] == "table":
            f.write("[ht]")
        elif environments[ixEnv] == "tabular":
            f.write("{" + alignment + "}")
            
        f.write("\n")
    tabs = len(environments)            # number of \t to use
    
    for i in range(0, m):
        f.write("\t"*tabs)
        for j in range(0, n):
            f.write(formatNumber % matrix[i, j])
            if j != n-1:
                f.write(" & ")
            else:
                f.write(r"\\")
                f.write("\n")

    #
    # End block
    #
    for ixEnv in range(0, len(environments)):
        ixEnv = len(environments)-1 - ixEnv # reverse order
        f.write("\t"*ixEnv)
        f.write(r"\end{%s}" % environments[ixEnv])
        f.write("\n")
        
if __name__ == '__main__':
    from numpy import *
    m = matrix('1 2 4;3 4 6')
#     matrix2latex(m, "tmp/test", "table", "center", "tabular", format="$%.2f$")
    matrix2latex(m, None, "table", "center", "tabular", format="$%.2f$", alignment='lcr')
#     matrix2latex(m, None)

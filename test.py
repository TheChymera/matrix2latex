# tests for matrix2latex.py
from matrix2latex import matrix2latex
# from numpy import matrix
# m = matrix('1 2 3;4 5 6')
m = [[1, 2, 3], [4, 5, 6]]

def assertEqual(x, y):
    # assert each line is equal, ignoring leading and trailing spaces
    x = x.split('\n')
    y = y.split('\n')
    for a, b in map(None, x, y):
        if a.strip() != b.strip():
            print(a,b)
            raise AssertionError

def test_simple():
    t = matrix2latex(m)
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{ccc}
		\toprule
			$1$ & $2$ & $3$\\
			$4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_transpose():
    t = matrix2latex(m, transpose=True)
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{ccc}
		\toprule
			$1$ & $4$\\
			$2$ & $5$\\
			$3$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_file():
    matrix2latex(m, 'tmp.tex')
    f = open('tmp.tex')
    content = f.read()
    f.close()
    assertEqual(content, r"""\begin{table}[ht]
	\begin{center}
        \label{tab:tmp}
		\begin{tabular}{ccc}
		\toprule
			$1$ & $2$ & $3$\\
			$4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_environment1():
    t = matrix2latex(m, None, "table", "center", "tabular")
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{ccc}
		\toprule
			$1$ & $2$ & $3$\\
			$4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")
 
def test_environment2():
    t = matrix2latex(m, None, "foo", "bar")
    assertEqual(t, r"""\begin{foo}
		\begin{bar}
			$1$ & $2$ & $3$\\
			$4$ & $5$ & $6$\\
		\end{bar}
	\end{foo}""")
   
def test_labels1():
    cl = ["a", "b"]
    rl = ["c", "d", "e"]
    t = matrix2latex(m, None, columnLabels=cl, rowLabels=rl)
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{rccc}
		\toprule
			 & c & d & e\\
			\midrule
			a & $1$ & $2$ & $3$\\
			b & $4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_labels2():
    # only difference from above test is names, note how above function
    # handles having too few rowLabels
    cl = ["a", "b"]
    rl = ["names", "c", "d", "e"]
    t = matrix2latex(m, None, columnLabels=cl, rowLabels=rl)
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{rccc}
		\toprule
			names & c & d & e\\
			\midrule
			a & $1$ & $2$ & $3$\\
			b & $4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_labels3():
    # pass in environment as dictionary
    e = dict()
    e['columnLabels'] = ["a", "b"]
    e['rowLabels'] = ["names", "c", "d", "e"]
    t = matrix2latex(m, None, **e)
    assertEqual(t, r"""\begin{table}[ht]
	\begin{center}
		\begin{tabular}{rccc}
		\toprule
			names & c & d & e\\
			\midrule
			a & $1$ & $2$ & $3$\\
			b & $4$ & $5$ & $6$\\
		\bottomrule
		\end{tabular}
	\end{center}
        \end{table}""")

def test_alignment1():
    t = matrix2latex(m, alignment='r')
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rrr}", t

def test_alignment2():
    t = matrix2latex(m, alignment='rcl')
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rcl}", t

def test_alignment3():
    t = matrix2latex(m, alignment='rcl', columnLabels=["a", "b"])
    t = t.split('\n')[2].strip()        # pick out only third line
    assert t == r"\begin{tabular}{rrcl}", t

#     print(matrix2latex(matrix(m), None, "align*", "pmatrix", format="%g", alignment='c'))
#     print(matrix2latex(m, None, columnLabels=cl, caption="Hello", label="la"))
#     print(matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s'))

#     m = [[1,None,None], [2,2,1], [2,1,2]]
#     print(matrix2latex(m, transpose=True))

if __name__ == '__main__':
    import test
    for d in test.__dict__:
        if 'test_' in d:
            eval(d+'()')

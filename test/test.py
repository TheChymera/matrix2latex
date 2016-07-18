#!/usr/bin/env python
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

# tests for matrix2latex.py
import os
import sys

sys.path.insert(0, '../')
from matrix2latex import matrix2latex

try:
    from test_syntaxError import *
except SyntaxError:
    pass

from test_util import *

m = [[1, 2, 3], [4, 5, 6]]


def test_simple():
    t = matrix2latex(m)
    assertEqual(t, "simple")

def test_transpose1():
    t = matrix2latex(m, transpose=True)
    assertEqual(t, "transpose1")

def test_transpose2():
    cl = ["a", "b"]
    t = matrix2latex(m, transpose=True, headerRow=cl)
    assertEqual(t, "transpose2")

def test_file():
    matrix2latex(m, 'tmp.tex')
    f = open('tmp.tex')
    content = f.read()
    f.close()
    assertEqual(content, "file")

def test_environment1():
    t = matrix2latex(m, None, "table", "center", "tabular")
    assertEqual(t, "environment1")
 
def test_environment2():
    t = matrix2latex(m, None, "foo", "bar")
    assertEqual(t, "environment2")
   
def test_labels1():
    cl = ["a", "b"]
    rl = ["c", "d", "e"]
    t = matrix2latex(m, None, headerColumn=cl, headerRow=rl)
    assertEqual(t, "labels1")

def test_labels2():
    # only difference from above test is names, note how above function
    # handles having too few headerRow
    cl = ["a", "b"]
    rl = ["names", "c", "d", "e"]
    t = matrix2latex(m, None, headerColumn=cl, headerRow=rl)
    assertEqual(t, "labels2")

def test_labels3():
    # pass in environment as dictionary
    e = dict()
    e['headerColumn'] = ["a", "b"]
    e['headerRow'] = ["names", "c", "d", "e"]
    t = matrix2latex(m, None, **e)
    assertEqual(t, "labels3")

def test_labels4():
    t = matrix2latex(m, None, caption="Hello", label="la")
    assertEqual(t, "labels4")
    
def test_alignment1():
    t = matrix2latex(m, alignment='r')
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rrr}", t

def test_alignment2():
    cl = ["a", "b"]
    rl = ["names", "c", "d", "e"]
    t = matrix2latex(m, alignment='r', headerColumn=cl, headerRow = rl)
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rrrr}", t

def test_alignment2b():
    rl = ["a", "b"]
    cl = ["names", "c", "d", "e"]
    t = matrix2latex(m, alignment='r', headerColumn=cl, headerRow = rl, transpose=True)
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rrr}", t

def test_alignment3():
    t = matrix2latex(m, alignment='rcl')
    t = t.split('\n')[2].strip()
    assert t == r"\begin{tabular}{rcl}", t

def test_alignment4():
    t = matrix2latex(m, alignment='rcl', headerColumn=["a", "b"])
    t = t.split('\n')[2].strip()        # pick out only third line
    assert t == r"\begin{tabular}{rrcl}", t

def test_alignment5():
    t = matrix2latex(m, alignment='r|c|l', headerColumn=["a", "b"])
    t = t.split('\n')[2].strip()        # pick out only third line
    assert t == r"\begin{tabular}{rr|c|l}", t

def test_alignment_withoutTable():
    t = matrix2latex(m, None, "align*", "pmatrix", format="$%.2f$", alignment='c')
    assertEqual(t, "alignment_withoutTable")

def test_numpy():
    try:
        import numpy as np
        for a in (np.matrix, np.array):
            t = matrix2latex(a(m), None, "align*", "pmatrix")
            assertEqual(t, "numpy")
    # Systems without numpy raises import error,
    # pypy raises attribute since matrix is not implemented, this is ok.
    except (ImportError, AttributeError):
        pass

def test_string():
    t = matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s')
    assertEqual(t, "string")

def test_none():
    m = [[1,None,None], [2,2,1], [2,1,2]]
    t = matrix2latex(m)
    assertEqual(t, "none")
    
    m2 = [[1,float('NaN'),float('NaN')], [2,2,1], [2,1,2]]
    t2 = matrix2latex(m)    
    assertEqual(t2, "none")

    t3 = matrix2latex(m, format='$%d$')
    assertEqual(t3, "none")

def test_infty1():
    try:
        import numpy as np
        m = [[1,np.inf,float('inf')], [2,2,float('-inf')], [-np.inf,1,2]]
        t = matrix2latex(m)
        assertEqual(t, "infty1")
    except (ImportError, AttributeError):
        pass

def test_infty2():
    # same as above but without numpy
    inf = float('inf')
    m = [[1,inf,float('inf')], [2,2,float('-inf')], [-inf,1,2]]
    t = matrix2latex(m)
    assertEqual(t, "infty1")

def test_multicolumn():
    hr = [['Item', 'Item', 'Item', 'Item', 'Price', 'Price', 'test', '', 'Money', 'Money', 'Money'],
          ['Animal', 'Description', '(\$)']]
    t = matrix2latex(m, headerRow=hr)
    t = t.split('\n')[4].strip()        # pick out only third line
    assert t == r"\multicolumn{4}{c}{Item} & \multicolumn{2}{c}{Price} & {test} & {} & \multicolumn{3}{c}{Money}\\\cmidrule(r){1-4}\cmidrule(r){5-6}\cmidrule(r){9-11}", t

def test_empty():
    t = matrix2latex([])
    assertEqual(t, 'empty')

def test_nicefloat():
    t = matrix2latex([123456e-10, 1e-15, 12345e5])
    assertEqual(t, 'nicefloat')

def test_nicefloat_4g():
    t = matrix2latex([123456e-10, 1e-15, 12345e5], format='$%.4g$')
    assertEqual(t, 'nicefloat_4g')

def test_non_rectangular():
    """Test a nested list with 'missing' elements"""
    t = matrix2latex([[1,2],
                      [1, 2, 3],
                      [5]])
    assertEqual(t, 'non_rectangular')
    
        
def test_pandas_dataframe():
    try:
        import pandas as pd
        import numpy as np
        m = [[1, 1], [2, 4], [3, 9]] # python nested list
        m = pd.DataFrame(m)
        #m = pd.DataFrame.from_csv('http://chymera.eu/data/test/r_data.csv', parse_dates=False, index_col=False)
        # print 'PANDAS\n', m
        # print 'PANDAS\n', m.to_records()
        t = matrix2latex(m)
        assertEqual(t, "pandas_dataframe")
    except ImportError:
        pass

def test_pandas_series():
    try:
        import pandas as pd
        import numpy as np
        s = pd.Series([2, 4, 2, 42, 5], index=['a', 'b', 'c', 'd', 'e'])
        # print 'PANDAS\n', s
        # print 'PANDAS\n', s.to_dict(), s.tolist(), hasattr(s, 'to_dict')
        t = matrix2latex(s)
        # print 'pandas Series', t
        t2 = matrix2latex(pd.DataFrame(s))
        # print 'pandas DataFrame', t2
        assertEqual(t, "pandas_series")
        assertEqual(t2, "pandas_series_dataFrame")
    except ImportError:
        pass

def test_pandas_columns():
    try:
        import pandas as pd
        import numpy as np
        d = {'one' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
             'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])}
        df = pd.DataFrame(d)
        t = matrix2latex(df)
        # print 'pandas', t, df.to_records()
        assertEqual(t, "pandas_columns")

        t = matrix2latex(df, headerRow=None, headerColumn=None)
        assertEqual(t, "pandas_columns_noHeaders")
    except ImportError:
        pass

def test_pandas_Panel():
    try:
        import pandas as pd
        import numpy as np
        panel = pd.Panel(np.random.randn(3, 5, 4), items=['one', 'two', 'three'],
                         major_axis=pd.date_range('1/1/2000', periods=5),
                         minor_axis=['a', 'b', 'c', 'd'])
        frame = panel.to_frame()
        # TODO: Needs support for multiple headerColumns
        #t = matrix2latex(frame) 
        #print t
        #assert False
    except ImportError:
        pass

if __name__ == '__main__':
    import test
    for d in sorted(test.__dict__):
        if 'test_' in d:
            print('RUNNING', d)
            eval(d+'()')

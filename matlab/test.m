%This file is part of matrix2latex.
%
%matrix2latex is free software: you can redistribute it and/or modify
%it under the terms of the GNU General Public License as published by
%the Free Software Foundation, either version 3 of the License, or
%(at your option) any later version.
%
%matrix2latex is distributed in the hope that it will be useful,
%but WITHOUT ANY WARRANTY; without even the implied warranty of
%MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%GNU General Public License for more details.
%
%You should have received a copy of the GNU General Public License
%along with matrix2latex. If not, see <http://www.gnu.org/licenses/>.

% tests for matrix2latex.m
function test()

m = [1, 2, 3; 4, 5, 6];

function assertEqual(output, name)
    fid = fopen('../common/test.tex');
    tline = fgetl(fid);
    found = false;
    answer = '';
    output = textscan(output, '%s', 'delimiter', '\n');
    output = output{1};
    ix = 1;
    while ischar(tline)
        if strcmp(tline, ['%%%', name])
            found = true;
        elseif regexpi(tline, '%%%', 'start')
            found = false;
        elseif found
            answer = [answer, tline];             % append
            a = strtrim(output{ix});
            b = strtrim(tline);
            if ~strcmp(a, b)
                output
                answer
                error('Invalid! "%s" ~= "%s"', a, b)
            end
            ix = ix + 1;
        end
        tline = fgetl(fid);             % prepare next loop
    end
    fclose(fid);
end

function test_simple()
    t = matrix2latex(m, '');
    assertEqual(t, 'simple');
end
test_simple()

function test_transpose1()
    t = matrix2latex(m, '', 'transpose', true);
    assertEqual(t, 'transpose1');
end
test_transpose1()

function test_transpose2()
    hr = {'a', 'b'};
    t = matrix2latex(m, '', 'transpose', true, 'headerRow', hr);
    assertEqual(t, 'transpose2');
end
test_transpose2()

function test_file()
    matrix2latex(m, 'tmp.tex');
    fid = fopen('tmp.tex');
    content = fread(fid, '*char');
    fclose(fid);
    assertEqual(content, 'file');
end
test_file()

function test_environment1()
    t = matrix2latex(m, '', 'environment', {'table', 'center', 'tabular'});
    assertEqual(t, 'environment1');
end
test_environment1()

function test_environment2()
    t = matrix2latex(m, '', 'environment', {'foo', 'bar'});
    assertEqual(t, 'environment2');
end
test_environment2()

function test_labels1()
    cl = {'a', 'b'};
    rl = {'c', 'd', 'e'};
    t = matrix2latex(m, '', 'headerRow', rl, 'headerColumn', cl);
    assertEqual(t, 'labels1');
end
test_labels1()

%{
function test_labels2()
    # only difference from above test is names, note how above function
    # handles having too few rowLabels
    cl = {'a', 'b'}
    rl = {'names', 'c', 'd', 'e'}
    t = matrix2latex(m, None, columnLabels=cl, rowLabels=rl)
    assertEqual(t, 'labels2')

function test_labels3()
    # pass in environment as dictionary
    e = dict()
    e['columnLabels'] = ['a', 'b']
    e['rowLabels'] = ['names', 'c', 'd', 'e']
    t = matrix2latex(m, None, **e)
    assertEqual(t, 'labels3')

function test_labels4()
    t = matrix2latex(m, None, caption='Hello', label='la')
    assertEqual(t, 'labels4')
    
function test_alignment1()
    t = matrix2latex(m, alignment='r')
    t = t.split('\n')[2].strip()
    assert t == r'\begin{tabular}{rrr}', t

function test_alignment2()
    cl = {'a', 'b'}
    rl = {'names', 'c', 'd', 'e'}
    t = matrix2latex(m, alignment='r', columnLabels=cl, rowLabels = rl)
    t = t.split('\n')[2].strip()
    assert t == r'\begin{tabular}{rrrr}', t

function test_alignment2b()
    rl = {'a', 'b'}
    cl = {'names', 'c', 'd', 'e'}
    t = matrix2latex(m, alignment='r', columnLabels=cl, rowLabels = rl, transpose=True)
    t = t.split('\n')[2].strip()
    assert t == r'\begin{tabular}{rrr}', t

function test_alignment3()
    t = matrix2latex(m, alignment='rcl')
    t = t.split('\n')[2].strip()
    assert t == r'\begin{tabular}{rcl}', t

function test_alignment4()
    t = matrix2latex(m, alignment='rcl', columnLabels={'a', 'b'})
    t = t.split('\n')[2].strip()        # pick out only third line
    assert t == r'\begin{tabular}{rrcl}', t

function test_alignment5()
    t = matrix2latex(m, alignment='r|c|l', columnLabels={'a', 'b'})
    t = t.split('\n')[2].strip()        # pick out only third line
    assert t == r'\begin{tabular}{rr|c|l}', t

function test_alignment_withoutTable()
    t = matrix2latex(m, None, 'align*', 'pmatrix', format='$%.2f$', alignment='c')
    assertEqual(t, 'alignment_withoutTable')

function test_numpy()
    try:
        import numpy as np
        for a in (np.matrix, np.array):
            t = matrix2latex(a(m), None, 'align*', 'pmatrix')
            assertEqual(t, 'numpy')
    # Systems without numpy raises import error,
    # pypy raises attribute since matrix is not implemented, this is ok.
    except (ImportError, AttributeError):
        pass

function test_string()
    t = matrix2latex([['a', 'b', '1'], ['1', '2', '3']], format='%s')
    assertEqual(t, 'string')

function test_none()
    m = [[1,None,None], [2,2,1], [2,1,2]]
    t = matrix2latex(m)
    assertEqual(t, 'none')
    
    m2 = [[1,float('NaN'),float('NaN')], [2,2,1], [2,1,2]]
    t2 = matrix2latex(m)    
    assertEqual(t2, 'none')

    t3 = matrix2latex(m, format='$%d$')
    assertEqual(t3, 'none')

function test_infty1()
    try:
        import numpy as np
        m = [[1,np.inf,float('inf')], [2,2,float('-inf')], [-np.inf,1,2]]
        t = matrix2latex(m)
        assertEqual(t, 'infty1')
    except (ImportError, AttributeError):
        pass

function test_infty2()
    # same as above but without numpy
    inf = float('inf')
    m = [[1,inf,float('inf')], [2,2,float('-inf')], [-inf,1,2]]
    t = matrix2latex(m)
    assertEqual(t, 'infty2')
    %}
end
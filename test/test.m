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
path(path, '../src_matlab')
m = [1, 2, 3; 4, 5, 6];

function assertLine(output, b, lineNr)
    output = textscan(output, '%s', 'delimiter', '\n');
    a = output{1}{lineNr};
    a = strtrim(a);
    b = strtrim(b);
    if ~strcmp(a, b)
        error('Invalid! "%s" ~= "%s"', a, b)
    end
end
function assertEqual(output, name)
    fid = fopen('test.tex');
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

function test_labels2()
    % only difference from above test is 'names', note how above function
    % handles having too few rowLabels
    cl = {'a', 'b'};
    rl = {'names', 'c', 'd', 'e'};
    t = matrix2latex(m, '', 'headerRow', rl, 'headerColumn', cl);
    assertEqual(t, 'labels2');
end
test_labels2()

% Not possible in matlab
%function test_labels3()
%    % pass in environment as dictionary
%    e = dict()
%    e['columnLabels'] = ['a', 'b']
%    e['rowLabels'] = ['names', 'c', 'd', 'e']
%    t = matrix2latex(m, None, **e)
%    assertEqual(t, 'labels3')
%test_labels3()

function test_labels4()
    t = matrix2latex(m, '', 'caption', 'Hello', 'label', 'la');
    assertEqual(t, 'labels4');
end
test_labels4()

function test_alignment1()
    t = matrix2latex(m, '', 'alignment', 'r');
    assertLine(t, '\begin{tabular}{rrr}', 3);
end
test_alignment1()

function test_alignment2()
    cl = {'a', 'b'};
    rl = {'names', 'c', 'd', 'e'};
    t = matrix2latex(m, '', 'alignment', 'r', 'headerColumn', cl, 'headerRow', rl);
    assertLine(t, '\begin{tabular}{rrrr}', 3);
end
test_alignment2()

function test_alignment2b()
    rl = {'a', 'b'};
    cl = {'names', 'c', 'd', 'e'};
    t = matrix2latex(m, '', 'alignment', 'r', 'headerColumn', cl, 'headerRow', ...
                     rl, 'transpose', true);
    assertLine(t, '\begin{tabular}{rrr}', 3);
end
test_alignment2b()

function test_alignment3()
    t = matrix2latex(m, '', 'alignment', 'rcl');
    assertLine(t, '\begin{tabular}{rcl}', 3);
end
test_alignment3()

function test_alignment4()
    t = matrix2latex(m, '', 'alignment', 'rcl', 'headerColumn', {'a', 'b'});
    assertLine(t, '\begin{tabular}{rrcl}', 3);
end
test_alignment4()

function test_alignment5()
    t = matrix2latex(m, '', 'alignment', 'r|c|l', 'headerColumn', {'a', 'b'});
    assertLine(t, '\begin{tabular}{rr|c|l}', 3);
end
test_alignment5()

function test_alignment_withoutTable()
    t = matrix2latex(m, '', 'environment', {'align*', 'pmatrix'}, ...
                     'format', '$%.2f$', 'alignment', 'c');
    assertEqual(t, 'alignment_withoutTable');
end
test_alignment_withoutTable()

% numpy, not an issue
%function test_numpy()
%    try:
%        import numpy as np
%        for a in (np.matrix, np.array):
%            t = matrix2latex(a(m), None, 'align*', 'pmatrix')
%            assertEqual(t, 'numpy')
%    % Systems without numpy raises import error,
%    % pypy raises attribute since matrix is not implemented, this is ok.
%    except (ImportError, AttributeError):
%        pass

function test_string()
    t = matrix2latex({'a', 'b', '1'; '1', '2', '3'}, '', 'format', '%s');
    assertEqual(t, 'string');
end
test_string()

function test_none()
    m = [1,nan,nan; 2,2,1; 2,1,2];
    t = matrix2latex(m, '');
    assertEqual(t, 'none');
    
    t3 = matrix2latex(m, '', 'format', '$%d$');
    assertEqual(t3, 'none');
end
test_none()

% numpy, not an issue
%function test_infty1()
%    try:
%        import numpy as np
%        m = [[1,np.inf,float('inf')], [2,2,float('-inf')], [-np.inf,1,2]]
%        t = matrix2latex(m)
%        assertEqual(t, 'infty1')
%    except (ImportError, AttributeError):
%        pass

function test_infty2()
    m = [1,inf, inf;, 2,2, -inf; -inf,1,2];
    t = matrix2latex(m, '');
    assertEqual(t, 'infty1');
end
test_infty2()

function test_multicolumn()
    hr = {{'Item', 'Item', 'Item', 'Item', 'Price', 'Price', 'test', '', 'Money', 'Money', 'Money'},
          {'Animal', 'Description', '(\$)'}}
    t = matrix2latex(m, '', 'headerRow', hr)
    assertLine(t, '\multicolumn{4}{c}{Item} & \multicolumn{2}{c}{Price} & test &  & \multicolumn{3}{c}{Money}\\\cmidrule(r){1-4}\cmidrule(r){5-6}\cmidrule(r){9-11}', 5)
end
%test_multicolumn()

function test_empty()
    t = matrix2latex([], '');
    assertEqual(t, 'empty');
end
test_empty()

function test_nicefloat()
    t = matrix2latex([123456e-10; 1e-15;12345e5], '');
    assertEqual(t, 'nicefloat');
end
test_nicefloat();

function test_nicefloat_4g()
    t = matrix2latex([123456e-10; 1e-15; 12345e5], '', 'format', '$%.4g$');
    assertEqual(t, 'nicefloat_4g');
end
test_nicefloat_4g();

function test_non_rectangular()
    t = matrix2latex([1, 2;
                      1, 2, 3;
                      5]);              % not legal matlab, no need
                                        % to test/support.
    assertEqual(t, 'nicefloat_4g');
end
%test_non_rectangular();

% end of file:
end
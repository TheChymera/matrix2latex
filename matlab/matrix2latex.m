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

function table = matrix2latex(matrix, filename, varargin)
% This is a modified version of M. Koehler's matrix2latex
% Options for formatColumns, caption and label have been added. Code has been cleaned.
%
% function: matrix2latexTable(...)
% Author:   M. Koehler, oystebjo
% Contact:  koehler@in.tum.de, oystebjo@student.matnat.uio.no
%
% This software is published under the GNU GPL, by the free software
% foundation. For further reading see: http://www.gnu.org/licenses/licenses.html#GPL
%
% Usage:
% matrix2late(matrix, filename, varargs)
% where
%   - matrix is a 2 dimensional numerical or cell array
%   - filename is a valid filename, without extension, in which the resulting latex code will
%   be stored. If filename == '' tex code will be printed to screen
%   - varargs is one ore more of the following (denominator, value) combinations
%      + 'rowLabels', array -> Can be used to label the rows of the
%      resulting latex table
%      + 'columnLabels' or 'headerRow', array -> Can be used to label the columns of the
%      resulting latex table
%      + 'alignment', 'value' -> Can be used to specify the alginment of
%      the table within the latex document. Valid arguments are: 'l', 'c',
%      and 'r' for left, center, and right, respectively
%      + 'format', 'value' -> Can be used to format the input data. 'value'
%      has to be a valid format string, similar to the ones used in
%      fprintf('format', value);
%      + 'formatColumns', 'values' -> values must be a vector with same 
%      length as nr of columns, se format above.
%      + 'size', 'value' -> One of latex' recognized font-sizes, e.g. tiny,
%      HUGE, Large, large, LARGE, etc.
%      + 'caption', 'value' -> if excluded no caption will be set.
%      + 'label', 'value' -> defaults to filename.
%
% Example input:
%   matrix = [1.5 1.764; 3.523 0.2];
%   rowLabels = {'row 1', 'row 2'};
%   headerRow = {'col 1', 'col 2'};
%   matrix2latexTable(matrix, 'out', 'rowLabels', rowLabels, 'headerRow', headerRow, 'alignment', 'c', 'format', '%-6.2f', 'size', 'tiny');
%
% The resulting latex file can be included into any latex document by:
% /input{out.tex}
%
% Enjoy life!!!

    if (rem(nargin,2) == 1 || nargin < 2)
        error('%s: Incorrect number of arguments', mfilename);
    end

    rowLabels = [];
    headerRow = [];
    alignment = 'c';
    format = '$%g$';
    textsize = [];
    caption = [];
    label = [];

    for j=1:2:(nargin-2)
        pname = varargin{j};
        pval = varargin{j+1};
        if strcmpi(pname, 'rowlabels')
            rowLabels = pval;
            if isnumeric(rowLabels)
                rowLabels = cellstr(num2str(rowLabels(:)));
            end
        elseif strcmpi(pname, 'columnLabels') || strcmpi(pname, 'headerRow')
            headerRow = pval;
            if isnumeric(headerRow)
                headerRow = cellstr(num2str(headerRow(:)));
            end
        elseif strcmpi(pname, 'alignment')
            okAlignment = {'l', 'c', 'r'};
            if ~isempty(strmatch(pval, okAlignment, 'exact'))
                alignment = pval;
            else
                alignment = 'c';
                warning('%s: Unkown alignment %s. Using l', mfilename, pval);
            end
        elseif strcmpi(pname, 'format')
            format = lower(pval);
        elseif strcmpi(pname, 'formatColumns')
            if size(pval) ~= size(matrix, 2)
                error('%s: Format columns has wrong length %d', mfilename, size(pval))
            else
                format = pval;
            end
        elseif strcmpi(pname, 'size')
            okSize = {'tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', ...
                      'LARGE', 'huge', 'Huge'};
            if ~isempty(strmatch(pval, okSize, 'exact'))
                textsize = pval;
            else
                warning('%s: Unknown size %s', mfilename, pval)
            end
        elseif strcmpi(pname, 'caption')
            caption = pval;
        elseif strcmpi(pname, 'label')
            label = ['tab:', pval];
        elseif strcmpi(pname, 'transpose')
            matrix = matrix';
        else
            error('%s: unknown parameter name %s', mfilename, pname)
        end
    end
    
    if filename ~= 1
        if (length(filename) < 4) || ~strcmp(filename(end-3:end), '.tex')
            filename = [filename, '.tex'];
        end
        %fid = fopen(filename, 'w');
        if isempty(label)
            label = ['tab:', filename(1:end-4)];
        end
        %else
        %fid = 1; % fprintf will print to standard output
    end
        
        %if isempty(matrix)
        % return;
        %end
        table = '';
        width = size(matrix, 2);
        height = size(matrix, 1);

        if isnumeric(matrix)
            matrix = num2cell(matrix);
            for h=1:height
                for w=1:width
                    if(~isempty(format))
                        if iscellstr(format) % if formatColumns
                            matrix{h, w} = num2str(matrix{h, w}, format{w});
                        end
                        matrix{h, w} = num2str(matrix{h, w}, format);
                    else
                        matrix{h, w} = num2str(matrix{h, w});
                    end
                    matrix{h, w} = fixEngineeringNotation(matrix{h, w});
                end
            end
        end
        
        if(~isempty(textsize))
            table = [table, sprintf('\\begin{%s}\n', textsize)];
        end

        table = [table, sprintf('\\begin{table}[ht]\n')];
        table = [table, sprintf('\t\\begin{center}\n')];
        if ~isempty(caption)
            table = [table, sprintf('\t\\caption{%s}\n', caption)];
        end
        if ~isempty(label)
            table = [table, sprintf('\t\\label{%s}\n', label)];
        end
        table = [table, sprintf('\t\t\\begin{tabular}{')];

        if(~isempty(rowLabels))
            table = [table, sprintf('c')];
        end
        for i=1:width
            table = [table, sprintf('%c', alignment)];
        end
        table = [table, sprintf('}')];
        
        %table = [table, sprintf('\\hline\n')];
        table = [table, sprintf('\n\t\t\t\\toprule\n')];
        
        if(~isempty(headerRow))
            if(~isempty(rowLabels))
                table = [table, sprintf('&')];
            end
            table = [table, sprintf('\t\t\t')];
            for w=1:width-1
                table = [table, sprintf('%s & ', headerRow{w})];
                %\textbf{%s}&', headerRow{w})];
            end
            table = [table, sprintf('%s\\\\\n', headerRow{width})];
            table = [table, sprintf('\t\t\t\\midrule\n')];
        end
        
        for h=1:height
            table = [table, sprintf('\t\t\t')];
            if(~isempty(rowLabels))
                %table = [table, sprintf('%s&', rowLabels{h})];
                table = [table, sprintf('\\text{%s}&', rowLabels{h})];
            end
            for w=1:width-1
                table = [table, sprintf('%s & ', matrix{h, w})];
            end
            table = [table, sprintf('%s\\\\\n', matrix{h, width})];
        end
        table = [table, sprintf('\t\t\t\\bottomrule\n')];

        table = [table, sprintf('\t\t\\end{tabular}\n')];
        table = [table, sprintf('\t\\end{center}\n')];
        table = [table, sprintf('\\end{table}\n')];
        
        if(~isempty(textsize))
            table = [table, sprintf('\\end{%s}', textsize)];
        end

        if ~isempty(filename) % if we should write to file
            fid = fopen(filename, 'w');
            fwrite(fid, table);
            fclose(fid);
        end
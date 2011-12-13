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
%      + 'headerColumn', array -> Can be used to label the rows of the
%      resulting latex table
%      + 'headerRow', array -> Can be used to label the columns of the
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
%   headerColumn = {'row 1', 'row 2'};
%   headerRow = {'col 1', 'col 2'};
%   matrix2latexTable(matrix, 'out', 'headerColumn', headerColumn, 'headerRow', headerRow, 'alignment', 'c', 'format', '%-6.2f', 'size', 'tiny');
%
% The resulting latex file can be included into any latex document by:
% /input{out.tex}
%
% Enjoy life!!!

    if (rem(nargin,2) == 1 || nargin < 2)
        error('%s: Incorrect number of arguments', mfilename);
    end

    table = '';
    width = size(matrix, 2);
    height = size(matrix, 1);

    headerColumn = [];
    headerRow = [];
    alignment = repmat('c', 1, width);
    format = '$%g$';
    textsize = [];
    caption = [];
    label = [];
    environment = {'table', 'center', 'tabular'};

    for j=1:2:(nargin-2)
        pname = varargin{j};
        pval = varargin{j+1};
        if strcmpi(pname, 'headerColumn')
            headerColumn = pval;
            if isnumeric(headerColumn)
                headerColumn = cellstr(num2str(headerColumn(:)));
            end
            alignment = ['r', alignment];
        elseif strcmpi(pname, 'headerRow')
            headerRow = pval;
            if isnumeric(headerRow)
                headerRow = cellstr(num2str(headerRow(:)));
            end
        elseif strcmpi(pname, 'alignment')
            okAlignment = {'l', 'c', 'r'};
            if ~isempty(strmatch(pval, okAlignment, 'exact'))
                if length(pval) == 1
                    alignment = repmat(pval, 1, width);
                else
                    alignment = pval;
                end
            else
                alignment = repmat('c', 1, width);
                warning('%s: Unkown alignment %s. Using c', mfilename, pval);
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
            if pval
                matrix = matrix';
                varargin{j+1} = false; % set transpose to false
                table = matrix2latex(matrix, filename, varargin{:});
                return;
            end
        elseif strcmpi(pname, 'environment')
            environment = pval;
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

        for ix = 1:length(environment)
            e = environment{ix};
            table = [table, sprintf(repmat('\t',1,ix-1))];
            if strcmpi(e, 'table')
                table = [table, sprintf('\\begin{%s}[ht]\n', e)];
            elseif strcmpi(e, 'tabular')
                table = [table, sprintf('\\begin{%s}{', e)];
                table = [table, sprintf('%s}\n', alignment)];

                table = [table, sprintf(repmat('\t',1,ix-1))];
                table = [table, sprintf('\\toprule\n')];
            elseif strcmpi(e, 'center')
                table = [table, sprintf('\\begin{%s}\n', e)];
                if ~isempty(caption)
                    table = [table, sprintf('\t\\caption{%s}\n', caption)];
                end
                if ~isempty(label)
                    table = [table, sprintf('\t\\label{%s}\n', label)];
                end
            else
                table = [table, sprintf('\\begin{%s}\n', e)];
            end
        end
        
        if(~isempty(headerRow))
            table = [table, sprintf('\t\t\t')];
            if ~isempty(headerColumn) && ~isempty(headerRow) && ...
                    length(headerRow) == width
                table = [table, sprintf('& ')];
            end
            for w=1:length(headerRow)-1
                table = [table, sprintf('%s & ', headerRow{w})];
                %\textbf{%s}&', headerRow{w})];
            end
            if width ~= length(headerRow)
                table = [table, sprintf('%s\\\\\n', ...
                                        headerRow{width+1})];
            else
                table = [table, sprintf('%s\\\\\n', ...
                                        headerRow{width})];
            end
            table = [table, sprintf('\t\t\t\\midrule\n')];
        end
        
        for h=1:height
            table = [table, sprintf('\t\t\t')];
            if(~isempty(headerColumn))
                table = [table, sprintf('%s & ', headerColumn{h})];
            end
            for w=1:width-1
                table = [table, sprintf('%s & ', matrix{h, w})];
            end
            table = [table, sprintf('%s\\\\\n', matrix{h, width})];
        end

        for ix = length(environment):-1:1
            e = environment{ix};
            table = [table, sprintf(repmat('\t',1,ix-1))];
            if strcmpi(e, 'tabular')
                table = [table, sprintf('\\bottomrule\n')];
                table = [table, sprintf(repmat('\t',1,ix-1))];
            end
            table = [table, sprintf('\\end{%s}\n', e)];
        end

        if(~isempty(textsize))
            table = [table, sprintf('\\end{%s}', textsize)];
        end

        if ~isempty(filename) % if we should write to file
            fid = fopen(filename, 'w');
            fwrite(fid, table);
            fclose(fid);
        end
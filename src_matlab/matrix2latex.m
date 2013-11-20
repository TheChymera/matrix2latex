function table = matrix2latex(matrix, filename, varargin)
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
%
% A detailed pdf version of this documentation is available as doc<date>.pdf
%Takes a python matrix or nested list and converts to a LaTeX table or matrix.
%Author: ob@cakebox.net, inspired by the work of koehler@in.tum.de who has written
%a similar package for matlab
%\url{http://www.mathworks.com/matlabcentral/fileexchange/4894-matrix2latex}
%
%The following packages and definitions are recommended in the latex preamble 
%% scientific notation, 1\e{9} will print as 1x10^9
%\providecommand{\e}[1]{\ensuremath{\times 10^{#1}}}
%\usepackage{amsmath} % needed for pmatrix
%\usepackage{booktabs} % Fancy tables
%...
%\begin{document}
%...
% \input{table}
% ...
%\end{document}
%
%Arguments:
%  
%matrix
%  A matrix or a cell array
%
%Filename
%  File to place output, extension .tex is added automatically. File can be included in a LaTeX
%  document by \input{filename}. Output will always be returned in a string. If filename is None,
%  empty string or not a string it is ignored.
%  
%
%**keywords
%%environments
%  Use 
%matrix2latex(m, '', 'environmnet' {"align*", "pmatrix"}, ...) for matrix.
%  This will give
%  \begin{align*}
%    \begin{pmatrix}
%      1 & 2 \\
%      3 & 4
%    \end{pmatrix}
%  \end{align*}
%  Use 
%matrix2latex(m, 'test', 'environemnt', {"table", "center", "tabular"} ...) for table.
%  Table is default so given no arguments: table, center and tabular will be used.
%  The above command is then equivalent to \\
%matrix2latex(m, 'test', ...)
%
%%headerRow
%    A row at the top used to label the columns.
%    Must be a list of strings.
%
%%headerColumn
%    A column used to label the rows.
%    Must be a list of strings
%
%%transpose
%Flips the table around in case you messed up. Equivalent to
%matrix2latex(m', ...)
%if m is a matrix.
%
%caption
%    Use to define a caption for your table.
%    Inserts \caption after \begin{center},
%    note that without the center environment the caption is currently ignored.
%
%label
%Used to insert \verb!\label{tab:...}! after \verb!\end{tabular}!
%Default is filename without extension.
%
%
%%format
%Printf syntax format, e.g. $%.2f$. Default is $%g$.
%  This format is then used for all the elements in the table.
%
%%formatColumn
%A list of printf-syntax formats, e.g. {$%.2f$, $%g$}
%Must be of same length as the number of columns.
%Format i is then used for column i.
%This is useful if some of your data should be printed with more significant figures
%than other parts
%
%%alignment
%Used as an option when tabular is given as enviroment.
%\begin{tabular}{alignment}
%A latex alignment like c, l or r.
%Can be given either as one per column e.g. "ccc".
%Or if only a single character is given e.g. "c",
%it will produce the correct amount depending on the number of columns.
%Default is "r".
%
%Note that many of these options only has an effect when typesetting a table,
%if the correct environment is not given the arguments are simply ignored.
%
    if (rem(nargin,2) == 1 || nargin < 2)
        error('%s: Incorrect number of arguments', mfilename);
    end

    table = '';
    width = size(matrix, 2);
    height = size(matrix, 1);

    headerColumn = [];
    headerRow = [];
    if width ~= 0
        alignment = repmat('c', 1, width);
    else
        alignment = 'c';
    end

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
            %okAlignment = {'l', 'c', 'r'};
            %if ~isempty(strmatch(pval, okAlignment, 'exact'))
            if length(pval) == 1
                alignment = repmat(pval, 1, width);
            else
                alignment = pval;
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
                    if isnan(matrix{h, w})
                        matrix{h, w} = '{-}';
                    elseif matrix{h, w} == inf
                        matrix{h, w} = '$\infty$';
                    elseif matrix{h, w} == -inf
                        matrix{h, w} = '$-\infty$';
                    elseif(~isempty(format))
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
                table = [table, sprintf('\\begin{%s}[htp]\n', e)];
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
                table = [table, sprintf('{} & ')];
            end
            for w=1:length(headerRow)-1
                table = [table, sprintf('{%s} & ', headerRow{w})];
                %\textbf{%s}&', headerRow{w})];
            end
            if width ~= length(headerRow)
                table = [table, sprintf('{%s}\\\\\n', ...
                                        headerRow{width+1})];
            else
                table = [table, sprintf('{%s}\\\\\n', ...
                                        headerRow{width})];
            end
            table = [table, sprintf('\t\t\t\\midrule\n')];
        end
        
        for h=1:height
            table = [table, sprintf(repmat('\t',1,height))];
            if(~isempty(headerColumn))
                table = [table, sprintf('{%s} & ', headerColumn{h})];
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
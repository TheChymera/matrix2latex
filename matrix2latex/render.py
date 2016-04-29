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
import os
import shutil
import warnings
import tempfile
import subprocess
from matrix2latex import matrix2latex

_latex_documentclass = r'\documentclass[varwidth=true, border=2pt, convert=true]{standalone}'
_latex_preamble = r"""\providecommand{\e}[1]{\ensuremath{\times 10^{#1}}}
\usepackage{amsmath}
\usepackage{booktabs}
"""
_latex_template = r"""%s
%s
\begin{document}
\pagenumbering{gobble}
%s
\end{document}
"""
def matrix2image(matr, filename=None, *args, **kwargs):
    r'''
    A wrapper around ``matrix2latex(*args, **kwargs)`` that creates a minimal LaTeX document code,
    compiles it, an removes the LaTeX traces.

    A number of options are available to support non-standard latex compilers (``pdflatex``, ``tex_options`` and ``output_format``),
    temporary file handling (``clean_latex`` and ``working_dir``) and
    customizing the latex template code (``latex_preamble``, ``latex_documentclass`` and ``latex_template``),
    These all have (hopefully) sensible default values, if you find something particularly lacking, open an issue!

    :param list matr: 
        The numpy matrix/array or a nested list to convert.
    :param str filename:
        Base-filename for the output image, defaults to 'rendered'
    :key clean_latex=True:
        Remove traces of the latex compilation. Use clean_latex=False and working_dir='tmp' to debug.
    :key working_dir=None:
        A temporary directory where the document is compiled, WARNING: will be removed as long as
        clean_latex is True, do not specify an existing directory. Defaults to tempfile.mkdtemp().
    :key latex_preamble:
        Defaults to ``render._latex_preamble``. To include additional preamble commands, use 
    
        ``latex_preamble = render._latex_preamble + r'\usepackage{my_package}'``
    :key latex_documentclass:
        Defaults to ``render._latex_documentclass``, for a4 page, call with ``latex_documentclass='\documentclass[a4paper]{article}'``.
    :key latex_template:
        The latex wrapper code, defaults to ``render._latex_template``, use at your own risk.
    :key tex='pdflatex':
        The tex renderer. Assumed to produce a '.pdf', if not, remember to also specify an appropriate output_format.
        If empty string or None, the document is not compiled.
    :key tex_options=['-interaction=nonstopmode', '-shell-escape']:
        Options passed to tex renderer
    :key output_format='.pdf':
        By default it is assumed ``tex='pdflatex'`` produces a '.pdf' and a '.png', 
        by default the '.pdf' is used, but you may also want to use ``output_format='.png'`` for the png image.
    :\*args:
        Additional arguments are passed to matrix2latex
    :\**kwargs:
        Additional keyword-arguments are passed to matrix2latex
    :returns working_dir, latex:
        A tuple of the working_dir and the latex document as a string. 
        The working_dir is None if the directory has been succesfully cleaned/removed.

    :raises IOError: if the expected output file was not created.
    :raises IOError: if removing files/directories in working_dir fails, this _will_ happend if working_dir suddenly contains folders.
    
    :raises subprocess.CalledProcessError: if the call to tex indicates a failure.

    :raises UserWarning: if working_dir is an existing directory and clean_latex=True.
    '''

    # Options
    if filename is None:
        filename = 'rendered'
    if filename.endswith(('.pdf', '.tex', '.png')):
        filename = filename[:-4]

    clean_latex = kwargs.pop('clean_latex', True)
    working_dir = kwargs.pop('working_dir', None)
    # in the case of working_dir=existing directory and clean_latex=True, keep a list of files that should not be cleaned
    existing_files = []
    if working_dir is None:
        working_dir = tempfile.mkdtemp(prefix='matrix2image')
    elif not os.path.exists(working_dir):
        os.makedirs(working_dir)
    else:
        if clean_latex:
            warnings.warn('The working directory already exists and clean_latex is True, I will try not to delete any of the files currently in working_dir=%s, but I make no promises.' % working_dir)
            # Note: there is a razy condition here, any files generated after this point will be deleted,
            # but at least we are not deleting family photos...
            # An alternative would be to clean only files known to be generated by pdflatex,
            # but odd tex compilers and packages can create odd files.
            existing_files = os.listdir(working_dir)

    latex_template = kwargs.pop('latex_template', _latex_template)
    latex_preamble = kwargs.pop('latex_preamble', _latex_preamble)
    latex_documentclass = kwargs.pop('latex_documentclass', _latex_documentclass)
    tex = kwargs.pop('tex', 'pdflatex')
    tex_options = kwargs.pop('tex_options', ['-interaction=nonstopmode', '-shell-escape'])
    output_format = kwargs.pop('output_format', '.pdf')

    # filenames
    tex_filename = os.path.basename(filename) + '.tex'
    tex_filename_full = os.path.join(working_dir, tex_filename)
    output_filename_final = filename + output_format
    output_filename_tmp = os.path.join(working_dir, os.path.basename(filename) + output_format)
    
    # call, do not write to file but get the latex-table as a string
    table = matrix2latex(matr, None, *args, **kwargs)
    
    # latex document
    latex = latex_template % (latex_documentclass, latex_preamble, table)
    with open(tex_filename_full, 'w') as f:
        f.write(latex)
    
    # compile document
    if tex is not None and tex != '': # I am sure there is a sexy way to write this test
        cmd = [tex]
        cmd.extend(tex_options)
        cmd.append(tex_filename)
        subprocess.check_call(cmd, cwd=working_dir)
    
        # we should now have a output_filename in the working directory
        if not(os.path.exists(output_filename_tmp)):
            raise IOError('Expected %s to exist after calling %s' % (output_filename_tmp, cmd))

        print output_filename_tmp, output_filename_final
        shutil.copyfile(output_filename_tmp, output_filename_final)

    if clean_latex:
        # only remove related files, then check if empty, then remove
        for p in os.listdir(working_dir):
            if p not in existing_files:
                try:
                    os.remove(os.path.join(working_dir, p)) # raises OSError if p is a directory, which is unexpected.
                except OSError as e:
                    raise OSError('Trouble removing file/directory:"%s", not cleaning. %s' % (p,e))

        # if empty:
        if len(os.listdir(working_dir)) == 0:
            shutil.rmtree(working_dir)
            working_dir = None # do not return path to non-existing directory
        else:
            warnings.warn('working_dir not empty, not cleaning %s' % working_dir)
    
    return working_dir, latex

if __name__ == '__main__':
    # m = [[1, 2, 3], [3, 4, 5]]
    # cl = ["a", "b", "c"]
    # rl = ['d', 'e', 'f', 'g']

    # matrix2image(m, 'rendered', 'tabular', format="$%.2g$", alignment='lcr',
    #              headerColumn=cl, caption="test", label="2", headerRow=rl)

    m = [[1, 1], [2, 4], [3, 9]]
    matrix2image(m, 'simpleExample', environments=['table', 'huge', 'center', 'tabular'], caption='hello',
                 clean_latex=True, working_dir='tmp')
    
    # matrix2image(m, 'simpleExample_a4', environments=['table', 'huge', 'center', 'tabular'], caption='hello',
    #              clean_latex=False, working_dir='tmp', latex_documentclass='\documentclass[a4paper]{article}'
    # )

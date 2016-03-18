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
from matrix2latex import matrix2latex
from subprocess import call

def simple(matrix, headerRow=None, headerColumn=None, Filename=None, font_size=None, clean_latex=True):
	"""A simple pagination function, that creates a minimal LaTeX document code for an input matrix,
	compiles it, and removes the LaTeX traces.

	Arguments:

	matrix
		A numpy matrix or a nested list

	Filename
		File to place output, extension .tex is added automatically. File can be included in a LaTeX
		document by \input{filename}. Output will always be returned in a string. If filename is None
		or not a string it is ignored.

	headerRow
		A row at the top used to label the columns.
		Must be a list of strings. Can be a nested list for multiple headings.
		If two or more items are repeated, a multicolumn is inserted, so:
		headerRow=['a', 'a']
		will produces "\multicolumn{2}{c}{Item}" with an appropriate cmidrule beneath.
		To avoid this behavior ensure each consecutive item is unique, for instance:
		headerRow=['a', 'a ']
		will produces the expected "a & a".

	headerColumn
		A column used to label the rows.
		Must be a list of strings

	font_size
		Specify the global (document and table) font size.
		Accepted values are integers from 1 to 10 - these are mapped on the available LaTeX font sizes
		https://en.wikibooks.org/wiki/LaTeX/Fonts

	clean_latex
		Used to optionally turn off the delete phase for LaTeX traces
		Must be bool
	"""

	latex_font_sizes = {
	1: "\\tiny",
	2: "\\scriptsize",
	3: "\\footnotesize",
	4: "\\small",
	5: "\\normalsize",
	6: "\\large",
	7: "\\Large",
	8: "\\LARGE",
	9: "\\huge",
	10: "\\Huge"
	}

	if not Filename:
		Filename = "_temp"

	table = matrix2latex(matrix, headerRow=headerRow, headerColumn=headerColumn, environments=['tabular'])

	#determine document font size
	if font_size:
		document_fontsize = latex_font_sizes[font_size]+"\n"
	else:
		document_fontsize = ""

	#add header elements (with the prepend operator "+"y in reverse order)
	tex = "\\sbox\mt{%\n" + table
	tex = document_fontsize + tex
	tex = "\\begin{document}\n" + tex
	tex = "\\pagenumbering{gobble}\n" + tex
	tex = "\\newsavebox\mt\n" + tex
	tex = "\\usepackage{booktabs}\n" + tex
	tex = "\\usepackage{geometry}\n\\geometry{a4paper,total={210mm,297mm},left=15mm,right=15mm,top=15mm,bottom=15mm}\n" + tex
	tex = "\\documentclass{article}\n" + tex

	#add footer elements
	tex = tex + "%\n}\n"
	tex = tex + \
"\\makeatletter\n" + \
"\\ifdim\\wd\\mt>\\textwidth\n" + \
"\\setlength\\@tempdima   {\\paperheight}%\n" + \
"\\setlength\\paperheight {\\paperwidth}%\n" + \
"\\setlength\\paperwidth  {\\@tempdima}%\n" + \
"\\setlength\\pdfpageheight{\\paperheight}%\n" + \
"\\setlength\\pdfpagewidth{\\paperwidth}%\n" + \
"\\setlength{\\textwidth}{\\paperwidth}%\n" + \
"\\addtolength{\\textwidth}{-3cm}%\n" + \
"\\setlength{\\hsize}{\\textwidth}%\n" + \
"\\fi\n" + \
"\\makeatother\n" + \
"\\begin{table}[htp]\\setlength{\\hsize}{\\textwidth}%\n" + \
"\\centering\n" + \
"\\usebox\\mt\n" + \
"\\end{table}\n" + \
"\\end{document}\n"

	file_ = open(Filename+".tex", 'w')
	file_.write(tex)
	file_.close()
	call(["pdflatex", Filename+".tex"])

	if clean_latex:
		all_files = os.listdir(".")
		latex_files = [one_file for one_file in all_files if Filename in one_file]
		non_pdf_latex_files = [latex_file for latex_file in latex_files if ".pdf" not in latex_file]
		for  non_pdf_latex_file in non_pdf_latex_files:
			os.remove(non_pdf_latex_file)


compilePDF:
	latexmk -pdf -pvc doc.tex

compileDVI:
	$(MAKE) clean
	latexmk -pvc doc.tex

compilePreview:
	latexmk -pdf doc.tex
	osascript -e "tell application \"Preview\" to activate"

compile:
	$(MAKE) clean
	rm -f doc.pdf doc.dvi # make sure they are recreated
	latexmk -pdf doc.tex # recreate pdf
	latexmk doc.tex      # recreate dvi
	$(MAKE) clean

clean:
	latexmk -c doc.tex
	rm -f *.aux *.log *~ *.out *.bbl

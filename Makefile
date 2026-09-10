# Project tasks. Run inside the project env (conda env `seaborn_portfolio`), e.g.:
#
#   conda run -n seaborn_portfolio make run
#   conda run -n seaborn_portfolio make site
#
#   make run     execute notebooks 1-6 in order, in place, so the committed
#                .ipynb files hold freshly generated output
#   make clean   strip all notebook output again
#   make site    regenerate docs/ (the static site) from the notebooks
#   make all     run, then site

NOTEBOOKS := 1_Relationships.ipynb 2_Distributions.ipynb 3_Comparing_Categories.ipynb \
	4_Matrices_And_Correlation.ipynb 5_Multiples_And_Grids.ipynb 6_Objects_Interface.ipynb

.PHONY: run clean site all

run:
	jupyter nbconvert --to notebook --execute --inplace \
		--ExecutePreprocessor.timeout=600 $(NOTEBOOKS)

clean:
	jupyter nbconvert --to notebook --clear-output --inplace $(NOTEBOOKS)

site:
	python build_site.py

all: run site

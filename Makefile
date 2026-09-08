# Run every notebook end to end.
#
#   make run     execute notebooks 1-6 in order, in place, so the committed
#                .ipynb files hold freshly generated output
#   make clean   strip all notebook output again
#
# Needs the project env (conda env `seaborn_portfolio`, see requirements.txt).
# Run inside that env, e.g.:  conda run -n seaborn_portfolio make run
# The raw `jupyter nbconvert` command in each target also works without make.

NOTEBOOKS := 1_Relationships.ipynb 2_Distributions.ipynb 3_Comparing_Categories.ipynb \
	4_Matrices_And_Correlation.ipynb 5_Multiples_And_Grids.ipynb 6_Objects_Interface.ipynb

.PHONY: run clean

run:
	jupyter nbconvert --to notebook --execute --inplace \
		--ExecutePreprocessor.timeout=600 $(NOTEBOOKS)

clean:
	jupyter nbconvert --to notebook --clear-output --inplace $(NOTEBOOKS)

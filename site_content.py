"""Hand-authored prose for the generated site (docs/).

build_site.py imports these; everything else on the site is parsed out of the
six notebooks.
"""

SITE_TITLE = "The Seaborn Portfolio"
TAGLINE = "Every Seaborn chart type, once — with a note on when to use it."

REPO_URL = "https://github.com/omri-sabag83/The-Seaborn-Portfolio"
GALLERY_URL = "https://seaborn.pydata.org/examples/index.html"
SEABORN_URL = "https://seaborn.pydata.org/"

# Short labels for the top nav bar (keyed by url slug).
NAV_LABELS = {
    "1-relationships": "Relationships",
    "2-distributions": "Distributions",
    "3-comparing-categories": "Comparing categories",
    "4-matrices-and-correlation": "Matrices & correlation",
    "5-multiples-and-grids": "Multiples & grids",
    "6-objects-interface": "Objects interface",
}

# Rendered (via mistune) into the top of the homepage. Keep each paragraph on a
# single line so inline **bold** / [links]() never straddle a newline.
INTRO_MD = f"""
A guided tour of the [Seaborn]({SEABORN_URL}) plotting library — **every chart type, once**, on a dataset chosen to show it at its best, each with a short note on when to reach for it.

## How this is organised

The charts are grouped by the **question you bring to your data**, not by Seaborn's module layout:

| The question | Group |
|---|---|
| How do two variables move together? | [**1 · Relationships**](1-relationships.html) |
| What is the shape of one variable? | [**2 · Distributions**](2-distributions.html) |
| How do groups compare? | [**3 · Comparing categories**](3-comparing-categories.html) |
| What structure is there across many variables? | [**4 · Matrices & correlation**](4-matrices-and-correlation.html) |
| One view repeated across subsets? | [**5 · Multiples & grids**](5-multiples-and-grids.html) |
| Building a plot from composable parts | [**6 · The objects interface**](6-objects-interface.html) |

This maps loosely onto Seaborn's own API sections, but the entry point is always "which chart answers my question", never "which module is it in".

## Taxonomy, not recipe book

Seaborn's own [example gallery]({GALLERY_URL}) is a *recipe book*: about 49 finished plots, each titled by how the result looks ("Scatterplot with varying point sizes"), with the same function recurring whenever a new styling trick is worth showing. It is where you go when you already know the chart you want.

This is a *taxonomy*. Each Seaborn plotting function appears **exactly once**, in the group that matches the question it answers, with a "best for" note covering the data shape it expects and when *not* to use it. The gallery's ~49 thumbnails cover about 25 functions; the ~40 figures here cover all 27 plotting functions plus the `seaborn.objects` grammar — no repeats.

Browse here to *choose* a chart; raid the gallery for styling.

## What is inside

27 classic plotting functions across five groups, plus 10 `seaborn.objects` compositions in the sixth — about 40 worked examples. Every figure and code snippet on this site is generated from the Jupyter notebooks in the [repository]({REPO_URL}); edit a notebook, rerun `build_site.py`, and this site updates.
"""

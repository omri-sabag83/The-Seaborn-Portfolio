# The Seaborn Portfolio

A hands-on tour of the [Seaborn](https://seaborn.pydata.org/) plotting library: for every
chart type, one clean example on a dataset chosen to show it at its best, plus a short note
on when to reach for it.

Inspired by the [Seaborn example gallery](https://seaborn.pydata.org/examples/index.html).

> **Status: work in progress.** The notebooks are being built one at a time. A consolidated
> gallery page and a fuller write-up will follow once they are complete.

## How this differs from the Seaborn gallery

Seaborn's [example gallery](https://seaborn.pydata.org/examples/index.html) is a *recipe
book*: ~49 finished plots, each with the code that made it, titled by how the result looks
("Scatterplot with varying point sizes"). It's where you go when you already know the chart
you want and need the styling incantation — so the same function recurs many times.

This project is a *taxonomy* instead. It asks **which** chart, not how to polish one: the
notebooks are organised by the question you're bringing to your data, and each Seaborn
function appears exactly once, on a dataset chosen to show its typical use, with a note on
when to reach for it. The gallery's ~49 thumbnails cover about 25 functions; the ~37
examples here cover all 27 plotting functions plus the objects interface, with no repeats.

The two are complementary: browse here to choose a chart, then raid the gallery for styling.

## Notebooks

| # | Notebook | Charts |
|---|---|---|
| 1 | `1_Relationships.ipynb` | scatterplot, lineplot, relplot, regplot, lmplot, residplot |
| 2 | `2_Distributions.ipynb` | histplot, kdeplot, ecdfplot, rugplot, displot |
| 3 | `3_Comparing_Categories.ipynb` | stripplot, swarmplot, boxplot, violinplot, boxenplot, pointplot, barplot, countplot, catplot |
| 4 | `4_Matrices_And_Correlation.ipynb` | heatmap, clustermap |
| 5 | `5_Multiples_And_Grids.ipynb` | FacetGrid, PairGrid, JointGrid, pairplot, jointplot |
| 6 | `6_Objects_Interface.ipynb` | the `seaborn.objects` grammar (Mark + Stat + Move) |

27 classic chart functions across notebooks 1–5, plus 10 objects-interface compositions in
notebook 6.

## Setup

```bash
conda create -n seaborn_portfolio python=3.13.5 -y
conda activate seaborn_portfolio
pip install -r requirements.txt
```

Run every notebook end to end: `conda run -n seaborn_portfolio make run`
(strip outputs again with `make clean`).

### Data

Most examples use Seaborn's built-in datasets (`sns.load_dataset(...)`). Two use Kaggle data —
[`camnugent/california-housing-prices`](https://www.kaggle.com/datasets/camnugent/california-housing-prices)
and [`camnugent/sandp500`](https://www.kaggle.com/datasets/camnugent/sandp500) — downloaded
on first run by `load_data.py` and cached under `data/` (git-ignored).

That first download needs Kaggle credentials. On kaggle.com go to **Settings → API →
Create New Token**; recent accounts get a single `KGAT_…` string — save it as
`~/.kaggle/access_token` (`chmod 600`). Older accounts get a `kaggle.json` file — put that
at `~/.kaggle/kaggle.json` instead. `kagglehub` reads either automatically. (Or set
`KAGGLE_USERNAME` + `KAGGLE_KEY`, or `KAGGLE_API_TOKEN`, in the environment.)

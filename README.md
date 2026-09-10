# The Seaborn Portfolio

A guided tour of the [Seaborn](https://seaborn.pydata.org/) plotting library: **every chart
type, once**, on a dataset chosen to show it at its best, each with a short note on when to
reach for it.

**→ Read it at <https://omri-sabag83.github.io/The-Seaborn-Portfolio/>** — a browsable
homepage where every chart is a card linking to its figure, code, and "best for" note.
(Served by GitHub Pages from [`docs/`](docs/), rebuilt on every push to `main`; you can also
just open `docs/index.html` locally.)

Inspired by Seaborn's own [example gallery](https://seaborn.pydata.org/examples/index.html).
Where that gallery is a *recipe book* — the same function shown many ways, titled by how the
result looks — this is a *taxonomy*: each plotting function appears exactly once, grouped by
the question it answers. The site's homepage explains the distinction.

## Notebooks

The six notebooks are the source of truth; the site is generated from them.

| # | Notebook | Charts |
|---|---|---|
| 1 | `1_Relationships.ipynb` | scatterplot, lineplot, relplot, regplot, lmplot, residplot |
| 2 | `2_Distributions.ipynb` | histplot, kdeplot, ecdfplot, rugplot, displot |
| 3 | `3_Comparing_Categories.ipynb` | stripplot, swarmplot, boxplot, violinplot, boxenplot, pointplot, barplot, countplot, catplot |
| 4 | `4_Matrices_And_Correlation.ipynb` | heatmap, clustermap |
| 5 | `5_Multiples_And_Grids.ipynb` | FacetGrid, PairGrid, JointGrid, pairplot, jointplot |
| 6 | `6_Objects_Interface.ipynb` | the `seaborn.objects` grammar (Mark + Stat + Move) |

27 classic plotting functions across notebooks 1–5, plus 10 `seaborn.objects` compositions in
notebook 6 — about 40 figures. `distplot` is deprecated and skipped.

## Setup

```bash
conda create -n seaborn_portfolio python=3.13.5 -y
conda activate seaborn_portfolio
pip install -r requirements.txt
```

`pandas` is pinned `<3`: Seaborn 0.13.2 mis-renders faceted figure-level plots
(`relplot` / `displot` / `catplot`) under pandas 3.x.

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

## Rebuilding

Run inside the `seaborn_portfolio` env (e.g. `conda run -n seaborn_portfolio make …`):

| Command | What it does |
|---|---|
| `make run` | execute all six notebooks in place, so the committed `.ipynb` hold fresh output |
| `make clean` | strip notebook outputs again |
| `make site` | regenerate `docs/` from the notebooks (`python build_site.py`) |
| `make all` | `run` then `site` |

Editing a notebook and rerunning `make run && make site` is the full update cycle. The site's
intro prose lives in `site_content.py`; everything else on the site is parsed from the
notebooks.

## Layout

```
1_*.ipynb … 6_*.ipynb   the notebooks (committed executed, with outputs)
images/                 exported figures, one set per notebook
build_site.py           notebook → docs/ generator
site_content.py         hand-authored site intro
docs/                   the generated site (GitHub Pages source)
data/                   Kaggle cache, git-ignored
CLAUDE.md               working conventions for this repo
```

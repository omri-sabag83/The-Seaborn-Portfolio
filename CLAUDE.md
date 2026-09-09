# CLAUDE.md — The Seaborn Portfolio

## What this project is

A personal walkthrough of the Seaborn library: for every chart type, one clean example on a
well-chosen dataset, plus a short written note on its best use cases. The goal is learning
*what charts exist and when to use each* — not fine styling. End state resembles
<https://seaborn.pydata.org/examples/index.html> (credited as inspiration in the README).

## Environment — do not install without asking

- Always use the conda env **`seaborn_portfolio`** (Python 3.13.5, matches `requirements.txt`).
  Never base anaconda, never `luke_barousse_course`.
- Run notebooks with: `conda run -n seaborn_portfolio make run` (or `make clean` to strip
  output). Per notebook: `conda run -n seaborn_portfolio jupyter nbconvert --to notebook
  --execute --inplace <notebook>`.
- **Any install / upgrade (conda, pip, kernel) is proposed to the user as exact commands —
  never run unprompted.**
- **`pandas` is pinned `<3` (currently 2.3.3).** seaborn 0.13.2 mis-renders faceted
  figure-level plots under pandas 3.x — `relplot` / `displot` / `catplot` draw the wrong
  subset under each facet title (confirmed 2026-09-09, notebook 3 `catplot`). Do not bump
  pandas to 3 unless seaborn ships a compatible release.

## Working rhythm

- **One notebook at a time**, in order 1 → 6. For each: write its cells, execute, export its
  PNGs, self-check, then stop for the user's review before anything is staged.
- **Nothing is staged, committed, or pushed without the user's explicit review and approval.**
  At each checkpoint show `git status` + the full diff and propose a commit message, then wait.
- Git: solo repo, direct-to-`main`, no branches, no PRs, no `gh` CLI.
- `README.md` stays a short stub until all notebooks are done. The consolidated
  "example gallery" final product is a separate phase the user will spec later.

## Notebook conventions

- Files `N_TitleCase.ipynb` at the repo root; `images/` at the repo root holds exported PNGs;
  notebooks are committed **executed, with outputs**.
- Cell 0 (markdown): `# N · <theme>` + the analytical question + a mini-table of the charts
  covered. Cell 1 (code): imports + `sns.set_theme(style="whitegrid")` (house style is set
  in-cell, there is no shared style module).
- Per chart, in order:
  1. `## <function_name>` — one line: what it draws, figure-level vs axes-level.
  2. Code cell: minimal idiomatic example; ends with
     `plt.savefig(f"images/<n>_<function>.png", dpi=150, bbox_inches="tight")`
     (notebook 6 uses `so.Plot(...).save("images/6_<n>_<name>.png", dpi=150)`).
  3. `**Best for:**` 2–4 bullets — data shape expected, the question it answers, what to
     read off it, when *not* to use it.
  4. A link to the official docs page for that function.

## Data

- Built-in datasets: load directly with `sns.load_dataset(...)` in the notebook.
- Two Kaggle datasets via `load_data.py` → `load_data("california_housing")` /
  `load_data("sp500")`; cached to `data/*.parquet` (git-ignored). First download needs Kaggle
  credentials — the newer `~/.kaggle/access_token` (a single `KGAT_…` string) or the classic
  `~/.kaggle/kaggle.json`; `kagglehub` reads either automatically. See the README.

## Chart coverage (target)

| Notebook | Charts |
|---|---|
| 1 Relationships | scatterplot, lineplot, relplot, regplot, lmplot, residplot |
| 2 Distributions | histplot, kdeplot, ecdfplot, rugplot, displot |
| 3 Comparing_Categories | stripplot, swarmplot, boxplot, violinplot, boxenplot, pointplot, barplot, countplot, catplot |
| 4 Matrices_And_Correlation | heatmap, clustermap |
| 5 Multiples_And_Grids | FacetGrid, PairGrid, JointGrid, pairplot, jointplot |
| 6 Objects_Interface | 10 `seaborn.objects` compositions (Mark [+ Stat] [+ Move]) |

27 classic functions (notebooks 1–5) + 10 compositions (notebook 6). `distplot` is
deprecated and skipped.

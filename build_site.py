"""Generate the static site in docs/ from the six notebooks.

The notebooks are the source of truth. Run this after any notebook change:

    python build_site.py          # or:  make site

Produces:
    docs/index.html                       homepage (intro + grouped thumbnail cards)
    docs/<n>-<slug>.html                  one page per notebook / group
    docs/assets/style.css                 base styles + Pygments defs
    docs/assets/full/*.png                full figures (copied from images/)
    docs/assets/thumbs/*.png              ~560px-wide thumbnails
    docs/.nojekyll                        tell GitHub Pages to serve files as-is

Dependencies (all already in requirements.txt): nbformat, mistune, pygments, Pillow.
"""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

import mistune
import nbformat
from PIL import Image
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

import site_content as sc

REPO = Path(__file__).resolve().parent
IMAGES = REPO / "images"
DOCS = REPO / "docs"
ASSETS = DOCS / "assets"
THUMBS = ASSETS / "thumbs"
FULL = ASSETS / "full"

THUMB_WIDTH = 560

# (notebook filename, url slug) in site order
NOTEBOOKS = [
    ("1_Relationships.ipynb", "1-relationships"),
    ("2_Distributions.ipynb", "2-distributions"),
    ("3_Comparing_Categories.ipynb", "3-comparing-categories"),
    ("4_Matrices_And_Correlation.ipynb", "4-matrices-and-correlation"),
    ("5_Multiples_And_Grids.ipynb", "5-multiples-and-grids"),
    ("6_Objects_Interface.ipynb", "6-objects-interface"),
]

_md = mistune.create_markdown(plugins=["table"])


# ----------------------------------------------------------------------- helpers
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[`*]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def strip_backticks(text: str) -> str:
    return text.replace("`", "").strip()


def first_line(text: str) -> str:
    return text.strip().splitlines()[0].strip()


def parse_table(md_block: str) -> list[list[str]]:
    """Return the rows (list of cells) of the first pipe-table found, minus the
    header and the `---` separator."""
    rows = []
    for line in md_block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells):  # separator row
            continue
        rows.append(cells)
    return rows[1:] if rows else []  # drop header row


def figure_from_code(code: str) -> str | None:
    """The images/<name>.png referenced by a savefig(...) / .save(...) call."""
    m = re.search(r"""(?:savefig|\.save)\(\s*(?:f?["'])([^"']+\.png)""", code)
    if not m:
        return None
    return Path(m.group(1)).name


def trim_code(code: str) -> str:
    """Drop the pure-boilerplate lines so the seaborn / objects call stands out."""
    out = []
    for line in code.splitlines():
        s = line.strip()
        if re.match(r"^fig,\s*ax\s*=\s*plt\.subplots\(", s):
            continue
        if re.search(r"\.savefig\(", s):
            continue
        if re.match(r"^\.save\(", s):  # trailing .save(...) in an so.Plot chain
            continue
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def highlight_code(code: str) -> str:
    return highlight(code, PythonLexer(), HtmlFormatter(nowrap=False))


def docs_url_from(md_block: str) -> str | None:
    m = re.search(r"\[[^\]]*docs\]\(([^)]+)\)", md_block or "")
    return m.group(1) if m else None


# ----------------------------------------------------------------- notebook parse
class Section:
    def __init__(self):
        self.heading = ""       # e.g. "`scatterplot`" or "1 · `so.Dot` — a scatter"
        self.name = ""          # card label
        self.oneliner = ""      # card sub-text (from the cell-0 table)
        self.anchor = ""
        self.desc_html = ""
        self.code_snippets: list[str] = []
        self.figures: list[str] = []          # basenames in images/
        self.bestfor_html = ""
        self.docs_url: str | None = None


def inline_md(text: str) -> str:
    """Render a short span of markdown, without the wrapping <p>."""
    return _md(text).strip().removeprefix("<p>").removesuffix("</p>")


class Group:
    def __init__(self):
        self.num = ""
        self.title = ""
        self.title_html = ""
        self.question = ""
        self.method_html = ""
        self.table_html = ""
        self.imports_code = ""
        self.sections: list[Section] = []
        self.trailing_html = ""   # nb6's closing prose section


def parse_notebook(path: Path) -> Group:
    nb = nbformat.read(path, as_version=4)
    cells = nb.cells
    g = Group()

    # --- cell 0: group header ------------------------------------------------
    head = cells[0].source
    m = re.search(r"^#\s*(\d+)\s*[·.]\s*(.+)$", head, re.M)
    g.num, g.title = m.group(1), m.group(2).strip()
    g.title_html = inline_md(g.title)
    mq = re.search(r"\*\*Analytical question:\*\*\s*(.+?)(?:\n\n|\Z)", head, re.S)
    g.question = " ".join(mq.group(1).split()) if mq else ""
    mm = re.search(r"\*\*Method:\*\*\s*(.+?)(?:\n\n|\Z)", head, re.S)
    g.method_html = _md(" ".join(mm.group(1).split())) if mm else ""
    table_rows = parse_table(head)
    # nb6's "Compositions" table is  # | Composition | Rebuilds  — the label is
    # the middle column, not the row number.
    numbered_table = bool(table_rows) and len(table_rows[0]) == 3
    name_col = 1 if numbered_table else 0

    # --- cell 1: imports ---------------------------------------------------
    g.imports_code = cells[1].source.strip()

    # --- remaining cells: sections + optional trailing prose --------------
    i = 2
    sec_index = 0
    while i < len(cells):
        c = cells[i]
        if c.cell_type == "markdown" and c.source.lstrip().startswith("## "):
            body = c.source.strip()
            heading_line = first_line(body)[3:].strip()
            rest = body[len(first_line(body)):].strip()

            # trailing prose section (nb6): no code before the next "## " / EOF
            nxt = cells[i + 1] if i + 1 < len(cells) else None
            if nxt is None or (
                nxt.cell_type == "markdown" and nxt.source.lstrip().startswith("## ")
            ):
                g.trailing_html = _md(body.replace("## ", "### ", 1))
                i += 1
                continue

            s = Section()
            s.heading = heading_line
            s.anchor = slugify(heading_line)
            s.desc_html = _md(rest) if rest else ""

            # card name / one-liner from the cell-0 table, by position
            if sec_index < len(table_rows):
                row = table_rows[sec_index]
                s.name = strip_backticks(row[name_col])
                s.oneliner = row[-1]
            else:
                s.name = strip_backticks(heading_line)
                s.oneliner = ""
            sec_index += 1

            # collect the consecutive code cells that follow
            i += 1
            while i < len(cells) and cells[i].cell_type == "code":
                code = cells[i].source.strip()
                fig = figure_from_code(code)
                if fig:
                    s.figures.append(fig)
                s.code_snippets.append(trim_code(code))
                i += 1

            # optional "**Best for**" note
            if i < len(cells) and cells[i].cell_type == "markdown" \
                    and cells[i].source.lstrip().startswith("**Best for"):
                note = cells[i].source.strip()
                s.bestfor_html = _md(note)
                s.docs_url = docs_url_from(note)
                i += 1

            g.sections.append(s)
        else:
            i += 1

    # rebuild the charts table as HTML (for the group page); link the name
    # column of each row to its chart section on the same page.
    if table_rows:
        header = ["Function", "Level", "Dataset", "In one line"]
        if numbered_table:                        # nb6: # | Composition | Rebuilds
            header = ["#", "Composition", "Rebuilds"]
        thead = "".join(f"<th>{html.escape(h)}</th>" for h in header)
        trows = ""
        for k, row in enumerate(table_rows):
            anchor = g.sections[k].anchor if k < len(g.sections) else None
            tds = ""
            for j, cell in enumerate(row):
                inner = inline_md(cell)
                if j == name_col and anchor:
                    inner = f'<a href="#{anchor}">{inner}</a>'
                tds += f"<td>{inner}</td>"
            trows += f"<tr>{tds}</tr>"
        g.table_html = f"<table><thead><tr>{thead}</tr></thead><tbody>{trows}</tbody></table>"

    return g


# ----------------------------------------------------------------------- rendering
def page_shell(title: str, body: str, rel: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel}assets/style.css">
</head>
<body>
{body}
</body>
</html>
"""


def nav_bar(groups: list[Group], current_slug: str | None, rel: str) -> str:
    links = [f'<a href="{rel}index.html"{"" if current_slug else " class=here"}>Home</a>']
    for (fname, slug), grp in zip(NOTEBOOKS, groups):
        cls = " class=here" if slug == current_slug else ""
        label = sc.NAV_LABELS.get(slug, grp.title)
        links.append(f'<a href="{rel}{slug}.html"{cls}>{grp.num}&nbsp;{html.escape(label)}</a>')
    return f'<nav class="topnav">{"".join(links)}</nav>'


def render_index(groups: list[Group]) -> str:
    intro = _md(sc.INTRO_MD)
    blocks = []
    for (fname, slug), g in zip(NOTEBOOKS, groups):
        cards = []
        for s in g.sections:
            if not s.figures:
                continue
            thumb = f"assets/thumbs/{s.figures[0]}"
            cards.append(
                f'<a class="card" href="{slug}.html#{s.anchor}">'
                f'<img loading="lazy" src="{thumb}" alt="{html.escape(s.name)}">'
                f'<span class="card-name">{html.escape(s.name)}</span>'
                f'<span class="card-one">{html.escape(s.oneliner)}</span>'
                f'</a>'
            )
        blocks.append(
            f'<section class="group">'
            f'<h2><a href="{slug}.html">{g.num} &middot; {g.title_html}</a></h2>'
            f'<p class="question">{html.escape(g.question)}</p>'
            f'<div class="grid">{"".join(cards)}</div>'
            f'</section>'
        )
    body = f"""
{nav_bar(groups, None, "")}
<header class="hero">
  <h1>{html.escape(sc.SITE_TITLE)}</h1>
  <p class="tagline">{html.escape(sc.TAGLINE)}</p>
</header>
<main>
<div class="intro">{intro}</div>
{"".join(blocks)}
</main>
<footer>Generated from the notebooks in
<a href="{sc.REPO_URL}">the repository</a> by <code>build_site.py</code>.</footer>
"""
    return page_shell(sc.SITE_TITLE, body, rel="")


def render_group(groups: list[Group], idx: int) -> str:
    fname, slug = NOTEBOOKS[idx]
    g = groups[idx]
    nb_url = f"{sc.REPO_URL}/blob/main/{fname}"

    secs = []
    for s in g.sections:
        figs = "".join(
            f'<img loading="lazy" src="assets/full/{f}" alt="{html.escape(s.name)}">'
            for f in s.figures
        )
        code = "".join(f'<div class="code">{highlight_code(c)}</div>'
                       for c in s.code_snippets if c.strip())
        note = f'<div class="bestfor">{s.bestfor_html}</div>' if s.bestfor_html else ""
        secs.append(
            f'<section class="chart" id="{s.anchor}">'
            f'<h2><a href="#{s.anchor}">{_md(s.heading).removeprefix("<p>").removesuffix("</p>")}</a></h2>'
            f'<div class="desc">{s.desc_html}</div>'
            f'<figure>{figs}</figure>'
            f'{code}'
            f'{note}'
            f'</section>'
        )

    trailing = f'<section class="chart trailing">{g.trailing_html}</section>' if g.trailing_html else ""

    body = f"""
{nav_bar(groups, slug, "")}
<main class="grouppage">
<header>
  <p class="crumb"><a href="index.html">Home</a> &rsaquo; {g.num} &middot; {g.title_html}</p>
  <h1>{g.num} &middot; {g.title_html}</h1>
  <p class="question">{html.escape(g.question)}</p>
  {g.table_html}
  <div class="method">{g.method_html}</div>
  <details class="imports"><summary>Imports for this notebook</summary>
  <div class="code">{highlight_code(g.imports_code)}</div></details>
</header>
{"".join(secs)}
{trailing}
<footer>Generated from <a href="{nb_url}"><code>{fname}</code></a> &mdash;
edit the notebook and rerun <code>build_site.py</code>.</footer>
</main>
"""
    return page_shell(f"{g.num} · {g.title} — {sc.SITE_TITLE}", body, rel="")


# --------------------------------------------------------------------------- CSS
BASE_CSS = """
:root{--fg:#1a1a1a;--muted:#666;--line:#e2e2e2;--bg:#fff;--accent:#3a6ea5;--soft:#f6f7f9}
*{box-sizing:border-box}
body{margin:0;color:var(--fg);background:var(--bg);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
main{max-width:960px;margin:0 auto;padding:0 20px 60px}
img{max-width:100%;height:auto}
h1{font-size:1.9rem;margin:.2em 0 .1em}
h2{font-size:1.35rem;margin:1.8em 0 .4em}
h3{font-size:1.05rem}
code{background:var(--soft);padding:.1em .35em;border-radius:4px;font-size:.9em}
pre{margin:0}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.92rem}
th,td{border:1px solid var(--line);padding:.4em .6em;text-align:left;vertical-align:top}
th{background:var(--soft)}

.topnav{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:.2em .9em;
  background:#fffdf7;border-bottom:1px solid var(--line);padding:.6em 20px;font-size:.85rem}
.topnav a{color:var(--muted)}
.topnav a.here{color:var(--fg);font-weight:600}

.hero{max-width:960px;margin:0 auto;padding:2.4em 20px 1em}
.hero h1{font-size:2.3rem;margin:0}
.tagline{color:var(--muted);font-size:1.1rem;margin:.3em 0 0}
.intro{border-bottom:1px solid var(--line);padding-bottom:1em;margin-bottom:1.5em}
.intro h2{font-size:1.2rem}

.group{margin:2.2em 0}
.group h2{margin-bottom:.1em}
.question{color:var(--muted);font-style:italic;margin:.2em 0 1em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}
.card{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:8px;
  overflow:hidden;background:var(--bg);transition:box-shadow .12s,border-color .12s}
.card:hover{border-color:var(--accent);box-shadow:0 2px 12px rgba(0,0,0,.09);text-decoration:none}
.card img{width:100%;aspect-ratio:4/3;object-fit:cover;background:var(--soft);border-bottom:1px solid var(--line)}
.card-name{font-weight:600;padding:.5em .7em 0}
.card-one{color:var(--muted);font-size:.82rem;padding:.2em .7em .7em}

.grouppage header{border-bottom:1px solid var(--line);padding-bottom:1em}
.crumb{color:var(--muted);font-size:.85rem;margin:1em 0 0}
.method{color:var(--muted);font-size:.92rem}
.imports{margin:1em 0}
.imports summary{cursor:pointer;color:var(--accent);font-size:.9rem}
.grouppage table td a{font-weight:600}

.chart{border-bottom:1px solid var(--line);padding:1.6em 0}
.chart:last-of-type{border-bottom:none}
.chart h2 a{color:var(--fg)}
.desc{color:#333}
figure{margin:1em 0;text-align:center}
figure img{border:1px solid var(--line);border-radius:6px}
.code{background:var(--soft);border:1px solid var(--line);border-radius:6px;
  padding:.8em 1em;overflow-x:auto;margin:1em 0;font-size:.86rem}
.code pre{font:.86rem/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.bestfor{background:#f4f8fb;border-left:3px solid var(--accent);border-radius:0 6px 6px 0;
  padding:.4em 1.1em;margin:1em 0}
.bestfor ul{margin:.5em 0;padding-left:1.2em}
.bestfor li{margin:.3em 0}
.trailing{background:var(--soft);border-radius:8px;padding:.5em 1.4em;margin-top:2em}

footer{margin-top:3em;padding-top:1.2em;border-top:1px solid var(--line);
  color:var(--muted);font-size:.85rem}
@media (max-width:520px){.hero h1{font-size:1.8rem}}
"""


# --------------------------------------------------------------------------- main
def build_thumb(src: Path, dst: Path) -> None:
    with Image.open(src) as im:
        if im.width <= THUMB_WIDTH:
            im.save(dst)
            return
        h = round(im.height * THUMB_WIDTH / im.width)
        im.convert("RGB").resize((THUMB_WIDTH, h), Image.LANCZOS).save(dst, quality=85)


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    for d in (ASSETS, THUMBS, FULL):
        d.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("")

    groups = [parse_notebook(REPO / fname) for fname, _ in NOTEBOOKS]

    # figures -> assets/full + assets/thumbs
    used = []
    for g in groups:
        for s in g.sections:
            used.extend(s.figures)
    missing = [f for f in used if not (IMAGES / f).exists()]
    if missing:
        raise SystemExit(f"missing figures in images/: {missing}")
    for f in used:
        shutil.copy2(IMAGES / f, FULL / f)
        build_thumb(IMAGES / f, THUMBS / f)

    # css
    pyg = HtmlFormatter().get_style_defs(".code")
    (ASSETS / "style.css").write_text(BASE_CSS + "\n" + pyg + "\n")

    # pages
    (DOCS / "index.html").write_text(render_index(groups))
    for idx, (_, slug) in enumerate(NOTEBOOKS):
        (DOCS / f"{slug}.html").write_text(render_group(groups, idx))

    n_charts = sum(len(g.sections) for g in groups)
    print(f"docs/ built: index + {len(NOTEBOOKS)} group pages, "
          f"{n_charts} chart sections, {len(used)} figures.")


if __name__ == "__main__":
    main()

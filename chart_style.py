"""Shared chart style: a thin black frame around every chart image.

Import once in a notebook (`import chart_style`). Every PNG that matplotlib produces (what
the notebook displays, and any chart saved to a .png file) gets a white margin and a thin
black frame around the whole image, including legends placed outside the axes. This makes
charts stand out on a white page (e.g. GitHub).
"""
import io
import os

import matplotlib.backend_bases as _bb
from PIL import Image, ImageOps

WHITE_MARGIN_PX = 8
FRAME_PX = 2

_print_figure = _bb.FigureCanvasBase.print_figure


def _framed_print_figure(self, filename, *args, **kwargs):
    fmt = kwargs.get("format")
    if fmt is None and isinstance(filename, (str, os.PathLike)):
        fmt = os.path.splitext(str(filename))[1].lstrip(".")
    if (fmt or "").lower() != "png":
        return _print_figure(self, filename, *args, **kwargs)
    buf = io.BytesIO()
    result = _print_figure(self, buf, *args, **{**kwargs, "format": "png"})
    img = Image.open(io.BytesIO(buf.getvalue()))
    img = ImageOps.expand(img, border=WHITE_MARGIN_PX, fill="white")
    img = ImageOps.expand(img, border=FRAME_PX, fill="black")
    img.save(filename, format="PNG")
    return result


_bb.FigureCanvasBase.print_figure = _framed_print_figure

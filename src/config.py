"""Shared paths and paper measurements.

Values below come from the real template
assets/img/wide-ruled-paper.png at 1700 x 2200.
Line centers run from y=140 to y=2064 with a 69 px gap.
Red margin sits near x=250.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAPER_PATH = ROOT / "assets" / "img" / "wide-ruled-paper.png"
FONT_PATH = ROOT / "assets" / "fonts" / "Papernotes.ttf"
OUTPUT_DIR = ROOT / "output"

# Writing area. Left starts right of the red margin line.
# Top starts at the second ruled line (y=208). The first
# line at y=140 sits under a tall header gap, so we skip it
# and use the 28 evenly spaced lines below it.
LEFT_X = 300
RIGHT_X = 1600
TOP_LINE_Y = 208
LINE_GAP = 69
LINES_PER_PAGE = 28

# Baseline sits this many pixels above the blue line.
# Room for descenders (p, g, y) plus a small gap,
# so text rests between rules instead of touching them.
BASELINE_OFFSET = 16

# Font sizes. Total glyph height stays under LINE_GAP here.
FONT_SIZE_DEFAULT = 44
FONT_SIZE_MIN = 28
FONT_SIZE_MAX = 56

INK_BLUE = (26, 42, 108)
INK_BLACK = (30, 30, 30)
INK_DEFAULT = INK_BLACK

INK_CHOICES = {
    "Black": INK_BLACK,
    "Dark blue": INK_BLUE,
}

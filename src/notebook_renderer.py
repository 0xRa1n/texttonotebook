"""Draw text onto the ruled paper template.

One line of text goes on one ruled line.
Extra lines spill onto a fresh copy of the template.
"""
from pathlib import Path
from PIL import Image, ImageFont

from src import config


def load_font(size):
    """Load Papernotes, fall back to a default font if missing."""
    try:
        return ImageFont.truetype(str(config.FONT_PATH), size)
    except OSError:
        return ImageFont.load_default()


def wrap_paragraph(paragraph, font, max_width):
    """Split one paragraph into lines that fit max_width pixels."""
    words = paragraph.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def text_to_lines(text, font):
    """Turn full text into wrapped lines, keeping blank lines."""
    max_width = config.RIGHT_X - config.LEFT_X
    out = []
    for paragraph in text.splitlines():
        if paragraph.strip() == "":
            out.append("")
        else:
            out.extend(wrap_paragraph(paragraph, font, max_width))
    return out


def draw_line_on_page(page, line_text, row, font, ink):
    """Draw one string so its baseline sits just above the ruled line."""
    ascent, _descent = font.getmetrics()
    line_y = config.TOP_LINE_Y + row * config.LINE_GAP
    top_y = line_y - ascent - config.BASELINE_OFFSET
    page.text((config.LEFT_X, top_y), line_text, font=font, fill=ink)


def render_pages(text, font_size=config.FONT_SIZE_DEFAULT, ink=None):
    """Render text to a list of PIL images, one per paper page."""
    ink = ink or config.INK_DEFAULT
    font = load_font(font_size)
    lines = text_to_lines(text, font)

    base = Image.open(config.PAPER_PATH).convert("RGB")
    pages = []
    page_image = None
    drawer = None

    # Lazy import keeps this module light until drawing starts.
    from PIL import ImageDraw

    for index, line_text in enumerate(lines):
        row = index % config.LINES_PER_PAGE
        if row == 0:
            page_image = base.copy()
            drawer = ImageDraw.Draw(page_image)
            pages.append(page_image)
        if line_text:
            draw_line_on_page(drawer, line_text, row, font, ink)

    if not pages:
        page_image = base.copy()
        pages.append(page_image)
    return pages


def save_pages(pages, folder=None, name="notebook"):
    """Save each page as PNG. Returns the list of file paths."""
    folder = Path(folder or config.OUTPUT_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, page in enumerate(pages, start=1):
        path = folder / f"{name}-page-{i}.png"
        page.save(path)
        paths.append(path)
    return paths


def save_pdf(pages, folder=None, name="notebook"):
    """Save all pages into one PDF. Returns the file path."""
    folder = Path(folder or config.OUTPUT_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.pdf"
    rgb_pages = [p.convert("RGB") for p in pages]
    rgb_pages[0].save(path, save_all=True, append_images=rgb_pages[1:])
    return path

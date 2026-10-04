# TextToNotebook

Type text or upload a photo of text, and get pages that look like notebook writing.

The app draws your text in the Papernotes font on top of the wide-ruled paper in `assets/img`. Long text flows onto more pages on its own.

## What you need

- Python 3.14
- pip

## Setup

```text
pip install -r requirements.txt
python app.py
```

The first photo read downloads OCR models once. After that, the app works offline.

## How to use

1. Type or paste text in the left box.
2. Or press Upload image for OCR to read text from a photo. Check the text after, since OCR can misread.
3. Pick ink color and font size.
4. Press Convert to notebook to see the preview.
5. Press Save PNG or Save PDF. Files go to the `output` folder.

Use Previous and Next to move between pages.

## Files

```text
app.py                  Main window and buttons
src/config.py           Paper size, line positions, font, ink colors
src/notebook_renderer.py Wraps text and draws it on the paper
src/ocr_reader.py       Reads text from a photo
assets/img/             Ruled paper template
assets/fonts/           Papernotes font
output/                Saved PNG and PDF files
requirements.txt        Needed packages
```

## Notes

- Each line of text sits on one ruled line. The top header line is skipped.
- Each page holds 28 lines. More text makes more pages.
- Default ink is black. Dark blue is also there.
- Previews are saved with `_preview` in the name. Final saves use the date and time.

"""Read text out of a photo with a local OCR engine.

Uses RapidOCR (ONNX). Models download once on first run,
then everything works offline.
"""


def extract_text(image_path):
    """Return plain text found in image_path, keeping line breaks."""
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    out = engine(str(image_path))
    # 1.2.x returns (result, boxes, elapse), newer returns (result, boxes)
    if isinstance(out, (list, tuple)):
        result = out[0]
    else:
        result = out
    if not result:
        return ""
    # result is a list of [box, text, score] rows
    lines = [row[1] for row in result if len(row) > 1 and row[1]]
    return "\n".join(lines)

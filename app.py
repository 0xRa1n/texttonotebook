"""TextToNotebook desktop app.

Left pane holds input and settings.
Right pane shows the rendered paper preview.
Plain solid colors only.
"""
import threading
from datetime import datetime

import flet as ft

from src import config
from src import notebook_renderer

ACCENT = "#1E3A8A"
PAGE_BG = "#FFFFFF"
PANEL_BG = "#F4F4F1"
TEXT_DARK = "#212121"
HINT_GRAY = "#616161"
BORDER_GRAY = "#9E9E9E"
TRACK_GRAY = "#BDBDBD"


def current_stamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def main(page: ft.Page):
    page.title = "TextToNotebook"
    page.bgcolor = PAGE_BG
    page.padding = 16

    pages = []
    preview_paths = []
    state = {"index": 0}

    status = ft.Text("Type text, or upload a photo to read it first.", color=TEXT_DARK)
    text_input = ft.TextField(
        label="Type or paste text",
        hint_text="Type or paste text",
        multiline=True,
        min_lines=12,
        max_lines=16,
        expand=False,
        color=TEXT_DARK,
        cursor_color=ACCENT,
        border_color=BORDER_GRAY,
        focused_border_color=ACCENT,
        text_style=ft.TextStyle(color=TEXT_DARK),
        label_style=ft.TextStyle(color=HINT_GRAY),
        hint_style=ft.TextStyle(color=HINT_GRAY),
    )
    font_slider = ft.Slider(
        min=config.FONT_SIZE_MIN,
        max=config.FONT_SIZE_MAX,
        value=config.FONT_SIZE_DEFAULT,
        label="Font size: {value}",
        active_color=ACCENT,
        inactive_color=TRACK_GRAY,
    )
    ink_dropdown = ft.Dropdown(
        label="Ink color",
        value="Black",
        color=TEXT_DARK,
        border_color=BORDER_GRAY,
        focused_border_color=ACCENT,
        text_style=ft.TextStyle(color=TEXT_DARK),
        label_style=ft.TextStyle(color=HINT_GRAY),
        hint_style=ft.TextStyle(color=HINT_GRAY),
        options=[ft.dropdown.Option(name) for name in config.INK_CHOICES],
    )
    page_label = ft.Text("Page 0 of 0", color=TEXT_DARK)
    preview_empty = ft.Text(
        "Preview appears here after you press Convert.", color=HINT_GRAY
    )
    preview = ft.Image(
        src=str(config.PAPER_PATH),
        width=520,
        fit=ft.BoxFit.CONTAIN,
        border_radius=4,
        visible=False,
    )

    def pick_ink():
        return config.INK_CHOICES.get(ink_dropdown.value, config.INK_DEFAULT)

    def show_page(index):
        if not preview_paths:
            return
        state["index"] = max(0, min(index, len(preview_paths) - 1))
        preview.src = str(preview_paths[state["index"]])
        preview.visible = True
        preview_empty.visible = False
        page_label.value = f"Page {state['index'] + 1} of {len(preview_paths)}"
        page.update()

    def do_convert(_e):
        text = text_input.value or ""
        if not text.strip():
            status.value = "Nothing to convert. Type some text first."
            page.update()
            return
        status.value = "Drawing text on paper..."
        page.update()
        # Unique preview name each run so the image view
        # never shows a cached copy of the previous color.
        for old in config.OUTPUT_DIR.glob("_preview-*.png"):
            try:
                old.unlink()
            except OSError:
                pass
        stamp = current_stamp()
        fresh = notebook_renderer.render_pages(
            text,
            font_size=int(font_slider.value),
            ink=pick_ink(),
        )
        paths = notebook_renderer.save_pages(
            fresh, folder=config.OUTPUT_DIR, name=f"_preview-{stamp}"
        )
        pages.clear()
        pages.extend(fresh)
        preview_paths.clear()
        preview_paths.extend(paths)
        status.value = f"Done. {len(pages)} page(s). Use Save for final files."
        show_page(0)
        page.update()

    def do_save_png(_e):
        if not pages:
            do_convert(_e)
            if not pages:
                return
        name = f"notebook-{current_stamp()}"
        saved = notebook_renderer.save_pages(pages, name=name)
        status.value = f"Saved {len(saved)} PNG file(s) to output folder."
        page.update()

    def do_save_pdf(_e):
        if not pages:
            do_convert(_e)
            if not pages:
                return
        path = notebook_renderer.save_pdf(pages, name=f"notebook-{current_stamp()}")
        status.value = f"Saved PDF to {path.name}."
        page.update()

    def run_ocr(image_path):
        try:
            from src import ocr_reader

            found = ocr_reader.extract_text(image_path)
        except Exception as err:
            status.value = f"OCR failed: {err}"
            page.update()
            return
        if not found.strip():
            status.value = "No text found in that image. Try a clearer photo."
        else:
            text_input.value = found
            status.value = "Photo text loaded. Check it, then press Convert."
        page.update()

    def on_upload_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        status.value = "Reading photo..."
        page.update()
        thread = threading.Thread(
            target=run_ocr, args=(e.files[0].path,), daemon=True
        )
        thread.start()

    picker = ft.FilePicker(on_result=on_upload_result)
    page.services.append(picker)

    convert_btn = ft.FilledButton(
        "Convert to notebook", on_click=do_convert,
        style=ft.ButtonStyle(color="white", bgcolor=ACCENT),
    )
    upload_btn = ft.OutlinedButton(
        "Upload image for OCR",
        style=ft.ButtonStyle(color=TEXT_DARK),
        on_click=lambda _: picker.pick_files(
            dialog_title="Pick a photo with text",
            allowed_extensions=["png", "jpg", "jpeg"],
        ),
    )
    save_png_btn = ft.OutlinedButton(
        "Save PNG", on_click=do_save_png,
        style=ft.ButtonStyle(color=TEXT_DARK),
    )
    save_pdf_btn = ft.OutlinedButton(
        "Save PDF", on_click=do_save_pdf,
        style=ft.ButtonStyle(color=TEXT_DARK),
    )
    prev_btn = ft.TextButton(
        "Previous", on_click=lambda _: show_page(state["index"] - 1),
        style=ft.ButtonStyle(color=ACCENT),
    )
    next_btn = ft.TextButton(
        "Next", on_click=lambda _: show_page(state["index"] + 1),
        style=ft.ButtonStyle(color=ACCENT),
    )

    left = ft.Container(
        bgcolor=PANEL_BG,
        border_radius=8,
        padding=16,
        width=420,
        content=ft.Column(
            [
                text_input,
                upload_btn,
                ft.Text("Settings", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(f"Font: Papernotes", color=TEXT_DARK),
                font_slider,
                ink_dropdown,
                convert_btn,
                ft.Row([save_png_btn, save_pdf_btn]),
                status,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    right = ft.Container(
        bgcolor=PANEL_BG,
        border_radius=8,
        padding=16,
        expand=True,
        content=ft.Column(
            [
                ft.Row([prev_btn, page_label, next_btn]),
                preview_empty,
                preview,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.add(ft.Row([left, right], expand=True, vertical_alignment=ft.CrossAxisAlignment.START))


ft.run(main)

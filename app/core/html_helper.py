from pathlib import Path
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def serve_html_with_base(relative_file_path: str, base_href: str) -> HTMLResponse:
    """Reads an HTML file from disk, injects a <base> tag to correctly resolve relative assets,
    and returns it as an HTMLResponse. This allows serving pages under clean URLs without exposing
    the .html file extension or breaking relative asset links."""
    file_path = BASE_DIR / relative_file_path
    if not file_path.exists():
        return HTMLResponse(content=f"Page not found: {relative_file_path}", status_code=404)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Inject the <base> tag right after the <head> tag
    if "<head>" in content:
        content = content.replace("<head>", f'<head><base href="{base_href}">')
    elif "<HEAD>" in content:
        content = content.replace("<HEAD>", f'<HEAD><base href="{base_href}">')

    return HTMLResponse(content=content)

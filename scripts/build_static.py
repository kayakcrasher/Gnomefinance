"""Build a static copy of the dashboard for GitHub Pages.

    python scripts/build_static.py          # writes ./site

GitHub Pages can't run Python, so this renders the Flask page once and
switches it to browser mode (static/browser_backend.js): prices and
balances are fetched straight from public APIs, and holdings are saved in
the visitor's browser.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gnomefinance.chains import default_chains  # noqa: E402
from gnomefinance.web_app import create_app  # noqa: E402


class TemplateOnlyService:
    """The page only needs the chain names, never live data."""

    chains = default_chains()


def build(out_dir):
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)

    app = create_app(TemplateOnlyService())
    app.config["STATIC_SITE"] = True

    with app.test_client() as client:
        html = client.get("/").get_data(as_text=True)

    # Pages serves from /<repo>/, so make asset links relative.
    html = html.replace('"/static/', '"static/')

    shutil.copytree(ROOT / "src" / "gnomefinance" / "static", out_dir / "static")
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / ".nojekyll").write_text("")
    print(f"Static site written to {out_dir}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")

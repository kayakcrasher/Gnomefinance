import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_static_site(tmp_path):
    spec = importlib.util.spec_from_file_location("build_static", ROOT / "scripts" / "build_static.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.build(tmp_path / "site")

    html = (tmp_path / "site" / "index.html").read_text()
    assert 'src="static/browser_backend.js"' in html
    assert "window.GNOME_ASSETS" in html
    assert '"/static/' not in html  # links must be relative for /<repo>/ hosting
    assert (tmp_path / "site" / "static" / "app.js").exists()

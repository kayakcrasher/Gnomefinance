"""Start the GNOMEfinance web dashboard:  python web_run.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from gnomefinance.web_app import create_app, start_web_app  # noqa: E402

# For production servers:  gunicorn web_run:app
app = create_app()

if __name__ == "__main__":
    start_web_app()

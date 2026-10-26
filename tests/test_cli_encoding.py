"""Command-line tools must not crash on Windows code-page consoles (CI found this). Run: python -m pytest -q"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_utf8_stdio_survives_a_legacy_code_page():
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    code = "from app.config import utf8_stdio; utf8_stdio(); print('FY23→FY24 −1.37 pp')"
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert "→".encode() in result.stdout


def test_every_command_line_entry_point_sets_utf8_output():
    for path in [*ROOT.glob("app/*.py"), *ROOT.glob("bench/*.py")]:
        text = path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' in text:
            main_block = text.split('if __name__ == "__main__":', 1)[1]
            assert re.search(r"utf8_stdio\(\)", main_block), f"{path.name} prints without utf8_stdio()"

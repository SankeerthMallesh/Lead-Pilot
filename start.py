"""One-command setup and start.   Run:  python start.py   (Windows: py start.py)

First run: installs everything, creates your settings and login, then opens the app.
Next runs: just starts the app.
"""
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import venv
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
URL = "http://127.0.0.1:8000"


def run(*cmd: str, **kw) -> None:
    subprocess.run([str(c) for c in cmd], cwd=ROOT, check=True, **kw)


def set_env(key: str, value: str) -> None:
    env = ROOT / ".env"
    text = env.read_text()
    line = f"{key}={value}"
    text = re.sub(rf"^{key}=.*$", lambda _m: line, text, flags=re.M) if re.search(rf"^{key}=", text, re.M) \
        else text + f"\n{line}\n"
    env.write_text(text)


def ask(question: str) -> str:
    try:
        return input(question).strip()
    except EOFError:
        return ""


def main() -> None:
    if sys.version_info < (3, 12):
        sys.exit("LeadPilot needs Python 3.12 or newer. Install it from python.org, then run this again.")

    if not PY.exists():
        print("Step 1/4: installing (about a minute, first time only)...")
        venv.create(VENV, with_pip=True)
        run(PY, "-m", "pip", "install", "-q", "-e", ".")
    if Path(sys.executable).resolve() != PY.resolve():
        os.execv(str(PY), [str(PY), str(ROOT / "start.py"), *sys.argv[1:]])

    first_run = not (ROOT / ".env").exists()
    if first_run:
        print("Step 2/4: settings")
        (ROOT / ".env").write_text((ROOT / ".env.example").read_text())
        set_env("SECRET_KEY", secrets.token_urlsafe(48))
        key = ask("Paste your Anthropic API key (needed to check posts), or press Enter to add it later: ")
        if key:
            set_env("ANTHROPIC_API_KEY", key)
        brave = ask("Paste your Brave Search key for steadier searching, or press Enter to skip: ")
        if brave:
            set_env("BRAVE_API_KEY", brave)

    run(PY, "-m", "alembic", "upgrade", "head", stdout=subprocess.DEVNULL)

    has_user = subprocess.run(
        [str(PY), "-c", "from app.db import SessionLocal;from app.models.user import User;"
         "import sys;sys.exit(0 if SessionLocal().query(User).count() else 1)"],
        cwd=ROOT).returncode == 0
    if not has_user:
        print("\nStep 3/4: create your login")
        run(PY, "scripts/create_admin.py")
        if ask("Add a demo client so you can try it right away? (y/n): ").lower().startswith("y"):
            run(PY, "scripts/seed.py")

    print(f"\nStep 4/4: starting LeadPilot at {URL}\nPress Ctrl+C here to stop it.\n")
    threading.Thread(target=lambda: (time.sleep(2.5), webbrowser.open(URL)), daemon=True).start()
    try:
        run(PY, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

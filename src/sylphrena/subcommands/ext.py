import os
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

from sylphrena.utils.io import fatal


def _tool() -> str:
    """scripts/ext.py of the shell that is installed (the shell owns the extension contract)."""
    home = Path.home()
    candidates = [
        os.environ.get("SYLPHRENA_EXT_TOOL", ""),
        str(home / ".config/quickshell/sylphrena/scripts/ext.py"),
        "/etc/xdg/quickshell/sylphrena/scripts/ext.py",
        "/usr/share/sylphrena/scripts/ext.py",
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    # The running shell knows where it is installed
    if shutil.which("qs"):
        try:
            r = subprocess.run(
                ["qs", "-c", "sylphrena", "ipc", "call", "extensions", "tools"],
                capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL,
            )
            path = Path(r.stdout.strip()) / "ext.py"
            if r.returncode == 0 and path.is_file():
                return str(path)
        except (OSError, subprocess.SubprocessError):
            pass
    fatal("cannot find the Sylphrena shell's scripts/ext.py (is the shell installed?)")


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        # The tool does the work (list | info | inspect | install <zip> | remove <id> [--purge] | enable | disable | rescan)
        os.execv(sys.executable, [sys.executable, _tool(), *self.args.ext_args])

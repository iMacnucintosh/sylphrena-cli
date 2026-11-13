"""Scripts that belong to the installed Sylphrena shell (scripts/ext.py, scripts/installer.py…).

The shell owns installing, updating and the extension contract; the CLI only finds its scripts and runs them.
"""

import os
import shutil
import subprocess
from pathlib import Path

from sylphrena.utils.io import fatal

INSTALL_HELP = "https://github.com/iMacnucintosh/sylphrena-shell#install"


def _scripts_dirs() -> list[Path]:
    home = Path.home()
    dirs = [
        home / ".config/quickshell/sylphrena/scripts",  # a clone (development)
        Path("/etc/xdg/quickshell/sylphrena/scripts"),  # the package
        Path("/usr/share/sylphrena/scripts"),
    ]
    # The running shell knows where it is installed
    if shutil.which("qs"):
        try:
            r = subprocess.run(
                ["qs", "-c", "sylphrena", "ipc", "call", "extensions", "tools"],
                capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL,
            )
            if r.returncode == 0 and r.stdout.strip():
                dirs.append(Path(r.stdout.strip()))
        except (OSError, subprocess.SubprocessError):
            pass
    return dirs


def shell_script(name: str, env: str = "") -> str:
    """Path of the shell's scripts/<name>; `env` names a variable that may point at it directly."""
    if env and os.environ.get(env) and Path(os.environ[env]).is_file():
        return os.environ[env]
    for d in _scripts_dirs():
        if (d / name).is_file():
            return str(d / name)
    fatal(f"cannot find the Sylphrena shell's scripts/{name}: is the shell installed? See {INSTALL_HELP}")

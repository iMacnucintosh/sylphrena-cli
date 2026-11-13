import shutil
import subprocess
import sys

from sylphrena.utils.paths import config_dir

# Sylphrena's packages are built from git (-git); the plain names are checked too
PKGS = ("sylphrena-shell", "sylphrena-cli", "quickshell")
INDENT = "    "


def _header(text: str, suffix: str = "") -> None:
    suffix = f" {suffix}" if suffix else ""
    if sys.stdout.isatty():
        print(f"\033[1;36m{text}\033[0m{suffix}")
    else:
        print(f"{text}{suffix}")


def _rows(pairs: list[tuple[str, str]]) -> None:
    dim = sys.stdout.isatty()
    width = max((len(key) for key, _ in pairs), default=0)
    for key, value in pairs:
        if dim:
            value = f"\033[2m{value}\033[0m"
        print(f"{INDENT}{key.ljust(width)}  {value}")


def _package_version(name: str) -> str | None:
    for pkg in (name, f"{name}-git"):
        r = subprocess.run(["pacman", "-Q", pkg], capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout.split()) > 1:
            return r.stdout.split()[1]
    return None


def print_packages() -> None:
    if not shutil.which("pacman"):
        _header("Packages:", "not on Arch")
        return
    _header("Packages:")
    _rows([(pkg, _package_version(pkg) or "not installed") for pkg in PKGS])


def _shell_version() -> str:
    for helper in ("/usr/lib/sylphrena/version", "/usr/lib/caelestia/version"):
        try:
            return subprocess.check_output([helper, "-s"], text=True).strip()
        except FileNotFoundError:
            continue
    raise FileNotFoundError("/usr/lib/sylphrena/version")


def print_version() -> None:
    print_packages()

    print()
    try:
        shell_ver = _shell_version()
        _header("Shell:")
        print(f"{INDENT}{shell_ver}")
    except FileNotFoundError:
        _header("Shell:", "version helper not available")

    print()
    if shutil.which("qs"):
        qs_ver = subprocess.check_output(["qs", "--version"], text=True).strip()
        _header("Quickshell:")
        print(f"{INDENT}{qs_ver}")
    else:
        _header("Quickshell:", "not in PATH")

    local_shell_dir = config_dir / "quickshell/sylphrena"
    if (local_shell_dir / ".git").exists():
        print()
        _header("Local copy of the shell found:")
        r = subprocess.run(["git", "-C", local_shell_dir, "describe", "--tags", "--match", "v0.*", "--always"],
                           capture_output=True, text=True)
        b = subprocess.run(["git", "-C", local_shell_dir, "branch", "--show-current"], capture_output=True, text=True)
        _rows([("Version", r.stdout.strip() or "unknown"), ("Branch", b.stdout.strip() or "detached")])

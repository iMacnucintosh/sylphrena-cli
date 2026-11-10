import json
import os
import signal
import subprocess
import time
from argparse import Namespace

from sylphrena.utils.io import fatal, warn
from sylphrena.utils.paths import c_cache_dir



def _shell_env() -> dict[str, str]:
    """Environment for the shell. A user-local plugin build (~/.local/lib/qt6/qml/Sylphrena, as left
    by `cmake --install` with prefix ~/.local) must win over the system package's: Qt looks for it
    through QT_ADDITIONAL_PACKAGES_PREFIX_PATH, which cannot be set from shell.qml without hardcoding
    the user's home."""
    import os
    from pathlib import Path

    env = dict(os.environ)
    local = Path.home() / ".local/lib/qt6/qml"
    if (local / "Sylphrena").is_dir():
        current = env.get("QT_ADDITIONAL_PACKAGES_PREFIX_PATH", "")
        if str(local) not in current.split(":"):
            env["QT_ADDITIONAL_PACKAGES_PREFIX_PATH"] = f"{local}:{current}" if current else str(local)
    return env


def _no_thp() -> None:
    """Disable transparent huge pages for the shell process (inherited across exec)."""
    try:
        import ctypes

        ctypes.CDLL(None, use_errno=True).prctl(41, 1, 0, 0, 0)  # PR_SET_THP_DISABLE
    except Exception:
        pass

class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.show:
            # Print the ipc
            self.print_ipc()
        elif self.args.log:
            # Print the log
            self.print_log()
        elif self.args.kill:
            # Kill the shell
            self.stop_instances()
        elif self.args.restart:
            # Restart the shell. Wait for the old instances to exit first,
            # otherwise `-n` will silently skip the relaunch
            self.stop_instances()
            self.start_shell()
        elif self.args.message:
            # Send a message
            self.message(*self.args.message)
        else:
            # Start the shell
            self.start_shell()

    def shell(self, *args: str) -> str:
        return subprocess.check_output(["qs", "-c", "sylphrena", *args], text=True)

    def start_shell(self) -> None:
        # The shell is started without transparent huge pages: with THP "always" (Arch default)
        # its many half-used heap areas got backed by 2 MB pages, ~180 MB more resident memory.
        args = ["qs", "-c", "sylphrena", "-n"]
        if self.args.log_rules:
            args.extend(["--log-rules", self.args.log_rules])
        if self.args.daemon:
            args.append("-d")
            subprocess.run(args, preexec_fn=_no_thp, env=_shell_env())
        else:
            shell = subprocess.Popen(
                args, stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=_no_thp, env=_shell_env()
            )

            # Ensure stdout is not None for the type checker
            if shell.stdout:
                for line in shell.stdout:
                    if self.filter_log(line):
                        print(line, end="")

    def list_instances(self) -> list[dict]:
        proc = subprocess.run(["qs", "-c", "sylphrena", "list", "-j"], check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            fatal(f"failed to list shell instances: {(proc.stderr or proc.stdout).strip()}")

        # `qs list` exits 0 and prints a plain text notice instead of JSON when
        # there are no instances, so only treat that exact case as empty
        out = proc.stdout.strip()
        if out.startswith("No running instances"):
            return []

        try:
            return json.loads(out)
        except json.JSONDecodeError:
            fatal(f"failed to parse shell instance list: {out}")

    def instance_pids(self) -> list[int]:
        return [instance["pid"] for instance in self.list_instances()]

    def wait_for_exit(self, timeout: float) -> bool:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if not self.list_instances():
                return True
            time.sleep(0.1)
        return False

    def stop_instances(self) -> None:
        pids = self.instance_pids()
        if not pids:
            return

        # Without `--pid`, `qs kill` only kills one instance, so ask each one to
        # exit. A kill that fails is not fatal here: the force kill below is the
        # fallback for any instance that does not go away.
        for pid in pids:
            subprocess.run(["qs", "-c", "sylphrena", "kill", "--pid", str(pid)], check=False, stdout=subprocess.DEVNULL)

        # Teardown is not instant, so wait for the instances to actually disappear
        if self.wait_for_exit(5):
            return

        # Some instances are stuck; force kill them to ensure they are stopped
        warn("shell did not exit gracefully, killing")
        for pid in self.instance_pids():
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        if not self.wait_for_exit(2):
            fatal("an instance of the shell is still running")

    def filter_log(self, line: str) -> bool:
        return f"Cannot open: file://{c_cache_dir}/imagecache/" not in line

    def print_ipc(self) -> None:
        print(self.shell("ipc", "show"), end="")

    def print_log(self) -> None:
        if self.args.log_rules:
            log = self.shell("log", "-r", self.args.log_rules)
        else:
            log = self.shell("log")
        # FIXME: remove when logging rules are added/warning is removed
        for line in log.splitlines():
            if self.filter_log(line):
                print(line)

    def message(self, *args: list[str]) -> None:
        print(self.shell("ipc", "call", *args), end="")

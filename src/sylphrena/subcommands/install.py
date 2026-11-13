import os
import sys
from argparse import Namespace

from sylphrena.utils.shell_tools import shell_script


class Command:
    """The Sylphrena installer (the shell's scripts/installer.py): what is missing on this computer, then installs it.
    `sylph update` runs it with --update: only brings what is installed up to date."""

    args: Namespace
    update = False

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        installer = shell_script("installer.py")
        extra = ["--update"] if self.update else []
        os.execv(sys.executable, [sys.executable, installer, *extra, *self.args.installer_args])

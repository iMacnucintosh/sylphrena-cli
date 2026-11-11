import os
import subprocess

from sylphrena.utils.dots.manifest import Manifest
from sylphrena.utils.dots.packages import PackageInstaller
from sylphrena.utils.dots.source import DotsSource
from sylphrena.utils.io import info, log, warn
from sylphrena.utils.paths import dots_dir


def build_local_packages(installer: PackageInstaller, source: DotsSource, paths: list[str]) -> dict[str, list[str]]:
    """Build and install each local PKGBUILD dir, returning {path: installed package names}."""

    built: dict[str, list[str]] = {}
    for path in paths:
        directory = source.working_path(path)
        if not directory.is_dir():
            warn(f"missing in repo, skipping: {path}")
            continue
        log(f"Building {path}...")
        built[path] = installer.build_install(directory)
    return built


def run_hooks(manifest: Manifest, kind: str) -> None:
    """Run the global + enabled components' hooks of the given kind (e.g. "post_install")."""

    hooks = manifest.enabled_hooks(kind)
    if not hooks:
        return

    print()
    log(f"Running {kind.replace('_', '-')} hooks...")
    # SYLPHRENA_DOTS is the new name; CAELESTIA_DOTS is kept so existing
    # install hooks in the dots repo keep working.
    env = {**os.environ, "SYLPHRENA_DOTS": str(dots_dir), "CAELESTIA_DOTS": str(dots_dir)}
    for hook in hooks:
        info(f"Running hook: {hook}")
        result = subprocess.run(hook, shell=True, env=env)
        if result.returncode != 0:
            warn(f"hook exited with {result.returncode}")

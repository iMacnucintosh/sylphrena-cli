import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from sylphrena.utils.io import warn

config_dir: Path = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
data_dir: Path = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share"))
state_dir: Path = Path(os.getenv("XDG_STATE_HOME", Path.home() / ".local/state"))
cache_dir: Path = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
pictures_dir: Path = Path(os.getenv("XDG_PICTURES_DIR", Path.home() / "Pictures"))
videos_dir: Path = Path(os.getenv("XDG_VIDEOS_DIR", Path.home() / "Videos"))

APP_NAME = "sylphrena"
LEGACY_APP_NAME = "caelestia"


def _env_path(name: str, default: Path) -> Path:
    """Read SYLPHRENA_<name>, falling back to the pre-rename CAELESTIA_<name>."""
    value = os.getenv(f"SYLPHRENA_{name}") or os.getenv(f"CAELESTIA_{name}")
    return Path(value) if value else default


def _app_dir(base: Path) -> Path:
    """Prefer the Sylphrena dir; fall back to the pre-rename one until it is migrated."""
    new_dir = base / APP_NAME
    old_dir = base / LEGACY_APP_NAME
    if new_dir.exists() or not old_dir.exists():
        return new_dir
    return old_dir


c_config_dir: Path = _app_dir(config_dir)
c_data_dir: Path = _app_dir(data_dir)
c_state_dir: Path = _app_dir(state_dir)
c_cache_dir: Path = _app_dir(cache_dir)

user_config_path: Path = c_config_dir / "cli.json"
cli_data_dir: Path = Path(__file__).parent.parent / "data"
templates_dir: Path = cli_data_dir / "templates"
user_templates_dir: Path = c_config_dir / "templates"
theme_dir: Path = c_state_dir / "theme"

config_backup_dir: Path = config_dir.parent / f"{config_dir.name}.bak"
dots_dir: Path = c_state_dir / "dots"
dots_state_path: Path = c_state_dir / "dots-state.json"

scheme_path: Path = c_state_dir / "scheme.json"
scheme_data_dir: Path = cli_data_dir / "schemes"
scheme_cache_dir: Path = c_cache_dir / "schemes"

wallpapers_dir: Path = _env_path("WALLPAPERS_DIR", pictures_dir / "Wallpapers")
wallpaper_path_path: Path = c_state_dir / "wallpaper/path.txt"
wallpaper_link_path: Path = c_state_dir / "wallpaper/current"
wallpaper_thumbnail_path: Path = c_state_dir / "wallpaper/thumbnail.jpg"
wallpapers_cache_dir: Path = c_cache_dir / "wallpapers"

screenshots_dir: Path = _env_path("SCREENSHOTS_DIR", pictures_dir / "Screenshots")
screenshots_cache_dir: Path = c_cache_dir / "screenshots"

recordings_dir: Path = _env_path("RECORDINGS_DIR", videos_dir / "Recordings")
recording_path: Path = c_state_dir / "record/recording.mp4"
recording_notif_path: Path = c_state_dir / "record/notifid.txt"


def compute_hash(path: Path | str) -> str:
    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    f = tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False)
    try:
        with f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(f.name, path)
    except BaseException:
        os.unlink(f.name)
        raise


def atomic_dump(path: Path, content: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(content))


def get_config() -> dict[str, Any]:
    try:
        return json.loads(user_config_path.read_text())
    except json.JSONDecodeError:
        warn("failed to parse config, invalid JSON")
    except FileNotFoundError:
        pass
    return {}

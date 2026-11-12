import re
import shutil
import subprocess
import time
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from sylphrena.utils import hypr
from sylphrena.utils.i18n import tr
from sylphrena.utils.notify import close_notification, notify
from sylphrena.utils.paths import get_config, recording_notif_path, recording_path, recordings_dir

RECORDER = "gpu-screen-recorder"
# Freedesktop icon name (Papirus has media-record / gpu-screen-recorder).
RECORD_ICON = "media-record"

# Handles the stopped notification actions in a tiny detached shell process so
# `sylph record` can exit as soon as the recording is saved.
# Args: path uri directory title body watch_label open_label delete_label
_STOPPED_NOTIF_HANDLER = r"""
path=$1
uri=$2
directory=$3
title=$4
body=$5
watch_label=$6
open_label=$7
delete_label=$8

action=$(notify-send -a Sylphrena -i media-record \
    --action=watch="$watch_label" \
    --action=open="$open_label" \
    --action=delete="$delete_label" \
    "$title" \
    "$body") || exit 0

case "$action" in
    watch)
        exec xdg-open "$path"
        ;;
    open)
        if ! dbus-send --session \
            --dest=org.freedesktop.FileManager1 \
            --type=method_call \
            /org/freedesktop/FileManager1 \
            org.freedesktop.FileManager1.ShowItems \
            "array:string:$uri" \
            "string:"; then
            exec xdg-open "$directory"
        fi
        ;;
    delete)
        rm -f -- "$path"
        ;;
esac
"""


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.pause:
            subprocess.run(["pkill", "-USR2", "-f", RECORDER], stdout=subprocess.DEVNULL)
        elif self.proc_running():
            self.stop()
        else:
            self.start()

    def proc_running(self) -> bool:
        return subprocess.run(["pidof", RECORDER], stdout=subprocess.DEVNULL).returncode == 0

    def intersects(self, a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
        return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]

    def start(self) -> None:
        args = ["-w"]

        monitors = hypr.message("monitors")
        if self.args.region:
            if self.args.region == "slurp":
                region = subprocess.check_output(
                    ["slurp", "-f", "%wx%h+%x+%y"],
                    text=True,
                    stdin=subprocess.DEVNULL,
                )
            else:
                region = self.args.region.strip()
            args += ["region", "-region", region]

            m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", region)
            if not m:
                raise ValueError(f"Invalid region: {region}")

            w, h, x, y = map(int, m.groups())
            r = x, y, w, h
            max_rr = 0
            for monitor in monitors:
                if self.intersects((monitor["x"], monitor["y"], monitor["width"], monitor["height"]), r):
                    rr = round(monitor["refreshRate"])
                    max_rr = max(max_rr, rr)
            args += ["-f", str(max_rr)]
        else:
            focused_monitor = next(monitor for monitor in monitors if monitor["focused"])
            if focused_monitor:
                args += [
                    focused_monitor["name"],
                    "-f",
                    str(round(focused_monitor["refreshRate"])),
                ]

        if self.args.sound:
            args += ["-a", "default_output"]

        config = get_config()
        try:
            if "record" in config and "extraArgs" in config["record"]:
                args += config["record"]["extraArgs"]
        except TypeError as e:
            raise ValueError(f"Config option 'record.extraArgs' should be an array: {e}")

        recording_path.parent.mkdir(parents=True, exist_ok=True)
        # The recorder outlives this command, so it must not inherit our stdio
        proc = subprocess.Popen(
            [RECORDER, *args, "-o", str(recording_path)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        notif = notify("-p", "-i", RECORD_ICON, tr("Recording started"), tr("Recording..."))
        recording_notif_path.write_text(notif)

        try:
            if proc.wait(1) != 0:
                close_notification(notif)
                notify(
                    "-i",
                    RECORD_ICON,
                    tr("Recording failed"),
                    tr(
                        "An error occurred attempting to start recorder. Command `{cmd}` failed with exit code {code}",
                        cmd=" ".join(proc.args),
                        code=proc.returncode,
                    ),
                )
        except subprocess.TimeoutExpired:
            pass

    def stop(self) -> None:
        # Start killing recording process
        subprocess.run(["pkill", "-f", RECORDER], stdout=subprocess.DEVNULL)

        # Wait for recording to finish to avoid corrupted video file
        while self.proc_running():
            time.sleep(0.1)

        # Move to recordings folder
        new_path = recordings_dir / f"recording_{datetime.now().strftime('%Y%m%d_%H-%M-%S')}.mp4"
        recordings_dir.mkdir(exist_ok=True, parents=True)
        shutil.move(recording_path, new_path)

        # Close start notification
        try:
            close_notification(recording_notif_path.read_text())
        except IOError:
            pass

        if self.args.clipboard:
            file_uri = Path(new_path).resolve().as_uri() + "\n"
            subprocess.run(["wl-copy", "--type", "text/uri-list"], input=file_uri.encode())

        recording = new_path.resolve()
        body = tr("Recording saved in {path}", path=str(recording))

        # The action notification's lifetime is the user's interaction with it,
        # not this command's, so hand it off to a detached lightweight handler
        subprocess.Popen(
            [
                "sh",
                "-c",
                _STOPPED_NOTIF_HANDLER,
                "sh",
                str(recording),
                recording.as_uri(),
                str(recording.parent),
                tr("Recording stopped"),
                body,
                tr("Watch"),
                tr("Open"),
                tr("Delete"),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd="/",
        )

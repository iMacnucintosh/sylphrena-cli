# sylphrena-cli

The main control script for **[Sylphrena](https://github.com/iMacnucintosh/sylphrena-shell)**, a Material You
shell for Hyprland. It started as the CLI of the [Caelestia](https://github.com/caelestia-dots/shell) dotfiles.

The command is `sylph`.

<details><summary id="dependencies">External dependencies</summary>

- [`libnotify`](https://gitlab.gnome.org/GNOME/libnotify) - sending notifications
- [`swappy`](https://github.com/jtheoof/swappy) - screenshot editor
- [`grim`](https://gitlab.freedesktop.org/emersion/grim) - taking screenshots
- [`dart-sass`](https://github.com/sass/dart-sass) - discord theming
- [`wl-clipboard`](https://github.com/bugaevc/wl-clipboard) - copying to clipboard
- [`slurp`](https://github.com/emersion/slurp) - selecting an area
- [`gpu-screen-recorder`](https://git.dec05eba.com/gpu-screen-recorder/about) - screen recording
- `glib2` - closing notifications
- [`cliphist`](https://github.com/sentriz/cliphist) - clipboard history
- [`fuzzel`](https://codeberg.org/dnkl/fuzzel) - clipboard history/emoji picker
- [`ffmpeg`](https://ffmpeg.org) - video wallpaper detection and colour generation

</details>

## Installation

It comes with Sylphrena: [its installer](https://github.com/iMacnucintosh/sylphrena-shell#install) installs this
CLI (the `sylphrena-cli-git` package) along with the shell, and keeps it up to date.

### Manual installation

Install all [dependencies](#dependencies), then install
[`python-build`](https://github.com/pypa/build),
[`python-installer`](https://github.com/pypa/installer),
[`python-hatch`](https://github.com/pypa/hatch) and
[`python-hatch-vcs`](https://github.com/ofek/hatch-vcs).

e.g. via an AUR helper (yay)

```sh
yay -S libnotify swappy grim dart-sass wl-clipboard slurp gpu-screen-recorder ffmpeg glib2 cliphist fuzzel python-build python-installer python-hatch python-hatch-vcs
```

Now, clone the repo, `cd` into it, build the wheel via `python -m build --wheel` and install it via
`python -m installer dist/*.whl`. Then, to install the `fish` completions, copy the
`completions/sylph.fish` file to `/usr/share/fish/vendor_completions.d/sylph.fish`.

```sh
git clone https://github.com/iMacnucintosh/sylphrena-cli.git
cd sylphrena-cli
python -m build --wheel
sudo python -m installer dist/*.whl
sudo cp completions/sylph.fish /usr/share/fish/vendor_completions.d/sylph.fish
```

### Additional steps

#### Auto folder colour theming

For automatic Papirus folder icon colour syncing, you must have
[`papirus-folders`](https://github.com/PapirusDevelopmentTeam/papirus-folders) installed, and
`papirus-folders` must be able to run with `sudo` without a password prompt.

You can allow this by creating a sudoers file:

```sh
echo "$USER ALL=(ALL) NOPASSWD: $(which papirus-folders)" | sudo tee /etc/sudoers.d/papirus-folders
sudo chmod 440 /etc/sudoers.d/papirus-folders
```

#### Chromium-based browser theming

For live Chromium-based browser theming, the CLI must be allowed to create certain directories in
`/etc` and write to them via `sudo` without a password prompt.

You can allow this by creating a sudoers file:

```fish
# Fish shell
for dir in /etc/chromium/policies/managed /etc/brave/policies/managed /etc/opt/chrome/policies/managed
    echo "$USER ALL=(ALL) NOPASSWD: $(which mkdir) -p $dir" | sudo tee -a /etc/sudoers.d/sylphrena-chromium
    echo "$USER ALL=(ALL) NOPASSWD: $(which tee) $dir/sylphrena.json" | sudo tee -a /etc/sudoers.d/sylphrena-chromium
end
sudo chmod 440 /etc/sudoers.d/sylphrena-chromium
```

```sh
# Bash/other shells
for dir in /etc/chromium/policies/managed /etc/brave/policies/managed /etc/opt/chrome/policies/managed; do
    echo "$USER ALL=(ALL) NOPASSWD: $(which mkdir) -p $dir" | sudo tee -a /etc/sudoers.d/sylphrena-chromium
    echo "$USER ALL=(ALL) NOPASSWD: $(which tee) $dir/sylphrena.json" | sudo tee -a /etc/sudoers.d/sylphrena-chromium
done
sudo chmod 440 /etc/sudoers.d/sylphrena-chromium
```

## Usage

All subcommands/options can be explored via the help flag.

```
$ sylph -h
usage: sylph [-h] [-v] COMMAND ...

Main control script for the Sylphrena Shell

options:
  -h, --help     show this help message and exit
  -v, --version  print the current version

subcommands:
  valid subcommands

  COMMAND        the subcommand to run
    shell        start or message the shell
    toggle       toggle a special workspace
    scheme       manage the colour scheme
    screenshot   take a screenshot
    record       start a screen recording
    clipboard    open clipboard history
    emoji        emoji/glyph utilities
    wallpaper    manage the wallpaper
    resizer      window resizer daemon
    install      install Sylphrena: what is missing on this computer (`sylph install --help`)
    update       bring Sylphrena and what it installed up to date (`sylph update --help`)
    ext          manage the shell's extensions or run their commands
```

`sylph install` and `sylph update` run the shell's own installer (`scripts/installer.py`); `sylph ext` runs its
extension tool (`scripts/ext.py`). Their options are the ones of those scripts.

### User templates

Custom user templates can be defined in `~/.config/sylphrena/templates/`.

#### Template syntax

`{{ <color>.<format> }}`

- `<color>` is a theme color role derived from the Material You color system (e.g. `primary`, `secondary`, `background`)
- `<format>` is the output format: `hex`, `rgb`, `hsl`, or a single channel (`red`, `green`, `blue`, `hue`, `saturation`, `lightness`)

#### Examples

- `{{ primary.hex }}` outputs `3f4ba2`
- `{{ primary.rgb }}` outputs `rgb(193, 132, 207)`
- `{{ primary.red }}` outputs `193`
- `{{ primary.hsl }}` outputs `hsl(268,41%,66%)`
- `{{ primary.hue }}` outputs `268`

Output files are written to `~/.local/state/sylphrena/theme/`. You can symlink them to your desired
locations.

## Configuring

All configuration options are in `~/.config/sylphrena/cli.json`.

<details><summary>Example configuration</summary>

```json
{
    "record": {
        "extraArgs": []
    },
    "wallpaper": {
        "postHook": "echo $WALLPAPER_PATH $SCHEME_NAME $SCHEME_FLAVOUR $SCHEME_MODE $SCHEME_VARIANT $SCHEME_COLOURS"
    },
    "theme": {
        "enableTerm": true,
        "enableHypr": true,
        "enableDiscord": true,
        "enableSpicetify": true,
        "enablePandora": true,
        "enableFuzzel": true,
        "enableBtop": true,
        "enableNvtop": true,
        "enableHtop": true,
        "enableGtk": true,
        "enableQt": true,
        "enableWarp": true,
        "enableChromium": true,
        "enableZed": true,
        "enableCava": true,
        "iconTheme": "Papirus-Dark",
        "iconThemeLight": "Papirus-Light",
        "iconThemeDark": "Papirus-Dark",
        "postHook": "echo $SCHEME_NAME $SCHEME_FLAVOUR $SCHEME_MODE $SCHEME_VARIANT $SCHEME_COLOURS"
    },
    "toggles": {
        "communication": {
            "discord": {
                "enable": true,
                "match": [{ "class": "discord" }],
                "command": ["discord"],
                "move": true
            },
            "whatsapp": {
                "enable": true,
                "match": [{ "class": "whatsapp" }],
                "move": true
            }
        },
        "music": {
            "spotify": {
                "enable": true,
                "match": [{ "class": "Spotify" }, { "initialTitle": "Spotify" }, { "initialTitle": "Spotify Free" }],
                "command": ["spicetify", "watch", "-s"],
                "move": true
            }
        },
        "sysmon": {
            "btop": {
                "enable": true,
                "match": [{ "class": "btop", "title": "btop", "workspace": { "name": "special:sysmon" } }],
                "command": ["kitty", "-a", "btop", "-T", "btop"]
            }
        },
        "todo": {
            "todoist": {
                "enable": true,
                "match": [{ "class": "Todoist" }],
                "command": ["todoist"],
                "move": true
            }
        }
    }
}
```

</details>

## Differences from upstream

This is the CLI of the Sylphrena fork. Renames applied on top of
[`caelestia-dots/cli`](https://github.com/caelestia-dots/cli):

| Upstream | Sylphrena |
| --- | --- |
| command `caelestia` | command `sylph` |
| package `caelestia` | package `sylphrena` |
| `~/.config/caelestia` | `~/.config/sylphrena` |
| `~/.local/state/caelestia` | `~/.local/state/sylphrena` |
| `~/.cache/caelestia` | `~/.cache/sylphrena` |
| `CAELESTIA_*` env vars | `SYLPHRENA_*` (old ones still read) |
| Quickshell instance `caelestia` | Quickshell instance `sylphrena` |
| theme files `caelestia.*` | theme files `sylphrena.*` |

`install` and `update` no longer deploy the Caelestia dotfiles: they run Sylphrena's installer.

## Licence

GPL-3.0-only, same as upstream. Original work © the Caelestia contributors.

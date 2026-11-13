set -l seen '__fish_seen_subcommand_from'
set -l has_opt '__fish_contains_opt'

set -l commands shell toggle scheme screenshot record clipboard emoji wallpaper resizer install update ext
set -l not_seen "not $seen $commands"

# Disable file completions
complete -c sylph -f

# Add help for any command
complete -c sylph -s 'h' -l 'help' -d 'Show help'

# Subcommands
complete -c sylph -n $not_seen -a 'shell' -d 'Start the shell or message it'
complete -c sylph -n $not_seen -a 'toggle' -d 'Toggle a special workspace'
complete -c sylph -n $not_seen -a 'scheme' -d 'Manage the colour scheme'
complete -c sylph -n $not_seen -a 'screenshot' -d 'Take a screenshot'
complete -c sylph -n $not_seen -a 'record' -d 'Start a screen recording'
complete -c sylph -n $not_seen -a 'clipboard' -d 'Open clipboard history'
complete -c sylph -n $not_seen -a 'emoji' -d 'Emoji/glyph utilities'
complete -c sylph -n $not_seen -a 'wallpaper' -d 'Manage the wallpaper'
complete -c sylph -n $not_seen -a 'resizer' -d 'Window resizer'
complete -c sylph -n $not_seen -a 'install' -d 'Install Sylphrena (what is missing)'
complete -c sylph -n $not_seen -a 'update' -d 'Bring Sylphrena up to date'
complete -c sylph -n $not_seen -a 'ext' -d 'Extensions: manage them or run their commands'

# Extensions: `sylph ext <Tab>` offers the actions and the installed extensions, `sylph ext <id> <Tab>` its commands
# (read from the manifests: the shell does not need to run)
function __sylph_ext_manifests
    for dir in $XDG_DATA_HOME/sylphrena/extensions ~/.local/share/sylphrena/extensions ~/.config/quickshell/sylphrena/extensions /etc/xdg/quickshell/sylphrena/extensions
        test -d $dir; and for m in $dir/*/manifest.json
            echo $m
        end
    end
end
function __sylph_extensions
    for m in (__sylph_ext_manifests)
        python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); print(m["id"]+"\t"+m.get("name", m["id"]))' $m 2>/dev/null
    end
end
function __sylph_ext_commands
    for m in (__sylph_ext_manifests)
        python3 -c 'import json,sys
m=json.load(open(sys.argv[1]))
if m.get("id") == sys.argv[2]:
    for c in m.get("contributes", {}).get("commands", []):
        print(c["name"]+"\t"+c.get("description", ""))' $m $argv[1] 2>/dev/null
    end
end
function __sylph_ext_at -a n
    set -l t (commandline -opc)
    test (count $t) -eq $n; and test "$t[2]" = ext
end
set -l ext_verbs list info inspect install install-hub update-hub remove enable disable rescan
complete -c sylph -n '__sylph_ext_at 2' -a "$ext_verbs" -d 'Action'
complete -c sylph -n '__sylph_ext_at 2' -a '(__sylph_extensions)'
complete -c sylph -n '__sylph_ext_at 3; and contains -- (commandline -opc)[3] remove enable disable update-hub' -a '(__sylph_extensions)'
complete -c sylph -n '__sylph_ext_at 3; and not contains -- (commandline -opc)[3] list info inspect install install-hub update-hub remove enable disable rescan' -a '(__sylph_ext_commands (commandline -opc)[3])'
complete -c sylph -n '__sylph_ext_at 3; and contains -- (commandline -opc)[3] install inspect' -F

# Shell
set -l commands mpris drawers wallpaper notifs
set -l not_seen "$seen shell && not $seen $commands"
complete -c sylph -n $not_seen -s 'd' -l 'daemon' -d 'Start the shell detached'
complete -c sylph -n $not_seen -s 'r' -l 'restart' -d 'Kill and restart the shell'
complete -c sylph -n $not_seen -s 's' -l 'show' -d 'Print all IPC commands'
complete -c sylph -n $not_seen -s 'l' -l 'log' -d 'Print the shell log'
complete -c sylph -n $not_seen -l 'log-rules' -d 'Log rules to apply'
complete -c sylph -n $not_seen -a 'mpris' -d 'Mpris control'
complete -c sylph -n $not_seen -a 'drawers' -d 'Toggle drawers'
complete -c sylph -n $not_seen -a 'wallpaper' -d 'Wallpaper control (for internal use)'
complete -c sylph -n $not_seen -a 'notifs' -d 'Notification control'

set -l commands getActive play pause playPause stop next previous list
set -l not_seen "$seen shell && $seen mpris && not $seen $commands"
complete -c sylph -n $not_seen -a 'play' -d 'Play media'
complete -c sylph -n $not_seen -a 'pause' -d 'Pause media'
complete -c sylph -n $not_seen -a 'playPause' -d 'Play/pause media'
complete -c sylph -n $not_seen -a 'next' -d 'Skip to next song'
complete -c sylph -n $not_seen -a 'previous' -d 'Go to previous song'
complete -c sylph -n $not_seen -a 'stop' -d 'Stop media'
complete -c sylph -n $not_seen -a 'list' -d 'List media players'
complete -c sylph -n $not_seen -a 'getActive' -d 'Get a property from the active MPRIS player'

set -l commands trackTitle trackArtist trackAlbum position length identity
set -l not_seen "$seen shell && $seen mpris && $seen getActive && not $seen $commands"
complete -c sylph -n $not_seen -a 'trackTitle' -d 'Track title'
complete -c sylph -n $not_seen -a 'trackArtist' -d 'Track artist'
complete -c sylph -n $not_seen -a 'trackAlbum' -d 'Track album'
complete -c sylph -n $not_seen -a 'position' -d 'Track position'
complete -c sylph -n $not_seen -a 'length' -d 'Track length'
complete -c sylph -n $not_seen -a 'identity' -d 'Player identity'

set -l commands list toggle
set -l not_seen "$seen shell && $seen drawers && not $seen $commands"
complete -c sylph -n $not_seen -a 'list' -d 'List togglable drawers'
complete -c sylph -n $not_seen -a 'toggle' -d 'Toggle a drawer'

set -l commands (sylph shell drawers list 2> /dev/null)
complete -c sylph -n "$seen shell && $seen drawers && $seen toggle && not $seen $commands" -a "$commands" -d 'drawer'

set -l commands list get set
set -l not_seen "$seen shell && $seen wallpaper && not $seen $commands"
complete -c sylph -n $not_seen -a 'list' -d 'List wallpapers'
complete -c sylph -n $not_seen -a 'get' -d 'Get current wallpaper path'
complete -c sylph -n $not_seen -a 'set' -d 'Change wallpaper'
complete -c sylph -n "$seen shell && $seen wallpaper && $seen set" -F

complete -c sylph -n "$seen shell && $seen notifs && not $seen clear" -a 'clear' -d 'Clear popup notifications'

# Toggles
set -l commands communication music specialws sysmon todo
complete -c sylph -n "$seen toggle && not $seen drawers && not $seen $commands" -a "$commands" -d 'toggle'

# Scheme
set -l commands list get set
set -l not_seen "$seen scheme && not $seen $commands"
complete -c sylph -n $not_seen -a 'list' -d 'List available schemes'
complete -c sylph -n $not_seen -a 'get' -d 'Get scheme properties'
complete -c sylph -n $not_seen -a 'set' -d 'Set the current scheme'

complete -c sylph -n "$seen scheme && $seen list" -s 'n' -l 'names' -d 'List scheme names'
complete -c sylph -n "$seen scheme && $seen list" -s 'f' -l 'flavours' -d 'List scheme flavours'
complete -c sylph -n "$seen scheme && $seen list" -s 'm' -l 'modes' -d 'List scheme modes'
complete -c sylph -n "$seen scheme && $seen list" -s 'v' -l 'variants' -d 'List scheme variants'

complete -c sylph -n "$seen scheme && $seen get" -s 'n' -l 'name' -d 'Get scheme name'
complete -c sylph -n "$seen scheme && $seen get" -s 'f' -l 'flavour' -d 'Get scheme flavour'
complete -c sylph -n "$seen scheme && $seen get" -s 'm' -l 'mode' -d 'Get scheme mode'
complete -c sylph -n "$seen scheme && $seen get" -s 'v' -l 'variant' -d 'Get scheme variant'

complete -c sylph -n "$seen scheme && $seen set" -l 'notify' -d 'Send a notification on error'
complete -c sylph -n "$seen scheme && $seen set" -s 'r' -l 'random' -d 'Switch to a random scheme'
complete -c sylph -n "$seen scheme && $seen set" -s 'n' -l 'name' -d 'Set scheme name' -a "$(sylph scheme list -n)" -r
complete -c sylph -n "$seen scheme && $seen set" -s 'f' -l 'flavour' -d 'Set scheme flavour' -a "$(sylph scheme list -f)" -r
complete -c sylph -n "$seen scheme && $seen set" -s 'm' -l 'mode' -d 'Set scheme mode' -a "$(sylph scheme list -m)" -r
complete -c sylph -n "$seen scheme && $seen set" -s 'v' -l 'variant' -d 'Set scheme variant' -a "$(sylph scheme list -v)" -r

# Screenshot
complete -c sylph -n "$seen screenshot" -s 'r' -l 'region' -d 'Capture region'
complete -c sylph -n "$seen screenshot" -s 'f' -l 'freeze' -d 'Freeze while selecting region'

# Record
complete -c sylph -n "$seen record" -s 'r' -l 'region' -d 'Capture region'
complete -c sylph -n "$seen record" -s 's' -l 'sound' -d 'Capture sound'
complete -c sylph -n "$seen record" -s 'c' -l 'clipboard' -d 'Copy recording path to clipboard'

# Clipboard
complete -c sylph -n "$seen clipboard" -s 'd' -l 'delete' -d 'Delete from cliboard history'

# Wallpaper
complete -c sylph -n "$seen wallpaper" -s 'p' -l 'print' -d 'Print the scheme for a wallpaper' -rF
complete -c sylph -n "$seen wallpaper" -s 'r' -l 'random' -d 'Switch to a random wallpaper' -rF
complete -c sylph -n "$seen wallpaper" -s 'f' -l 'file' -d 'The file to switch to' -rF
complete -c sylph -n "$seen wallpaper" -s 'n' -l 'no-filter' -d 'Do not filter by size'
complete -c sylph -n "$seen wallpaper" -s 't' -l 'threshold' -d 'The threshold to filter by' -r
complete -c sylph -n "$seen wallpaper" -s 'N' -l 'no-smart' -d 'Disable smart mode switching'

# Emoji
complete -c sylph -n "$seen emoji" -s 'p' -l 'picker' -d 'Open emoji/glyph picker'
complete -c sylph -n "$seen emoji" -s 'f' -l 'fetch' -d 'Fetch emoji/glyph data from remote'

# Resizer
complete -c sylph -n "$seen resizer" -s 'd' -l 'daemon' -d 'Start in daemon mode'
complete -c sylph -n "$seen resizer" -a 'pip' -d 'Quick pip mode'
complete -c sylph -n "$seen resizer" -a 'active' -d 'Select the active window'

# Install / update: the Sylphrena installer's options
for c in install update
    complete -c sylph -n "$seen $c" -l 'dry-run' -d 'Show what it would do, change nothing'
    complete -c sylph -n "$seen $c" -s 'y' -l 'yes' -d 'Accept the defaults'
    complete -c sylph -n "$seen $c" -l 'main' -d 'Build the latest commit instead of the latest release'
    complete -c sylph -n "$seen $c" -l 'verbose' -d 'Show the output of every command'
    complete -c sylph -n "$seen $c" -l 'help' -d 'The installer\'s help'
end
complete -c sylph -n "$seen install" -l 'no-login-screen' -d 'Leave the login screen as it is'
complete -c sylph -n "$seen install" -l 'list' -d 'What it found, as JSON'

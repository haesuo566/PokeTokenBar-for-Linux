#!/usr/bin/env bash
# Installs a PokeTokenBar launcher for this user: an application-menu entry,
# an icon, and (with --autostart) a Startup-equivalent entry that launches the
# tray on login. Run from anywhere; it locates the repo from this script's
# own path, so `requirements.txt` must already be installed for the Python
# interpreter you want it to run with (the one currently on PATH by default).
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-python3}"

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
APPS_DIR="$DATA_HOME/applications"
ICON_DIR="$DATA_HOME/icons/hicolor/256x256/apps"
AUTOSTART_DIR="$CONFIG_HOME/autostart"

mkdir -p "$APPS_DIR" "$ICON_DIR"

echo "icon      -> $ICON_DIR/poketokenbar.png"
PYTHONPATH="$REPO_ROOT" "$PYTHON" -c "
from poketokenbar.app import _draw_egg
_draw_egg(256).save('$ICON_DIR/poketokenbar.png')
"

DESKTOP_FILE="$APPS_DIR/poketokenbar.desktop"
echo "launcher  -> $DESKTOP_FILE"
sed \
    -e "s|^Exec=.*|Exec=env PYTHONPATH=$REPO_ROOT $PYTHON -m poketokenbar|" \
    -e "s|^Icon=.*|Icon=$ICON_DIR/poketokenbar.png|" \
    "$SCRIPT_DIR/poketokenbar.desktop" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

if [[ "${1:-}" == "--autostart" ]]; then
    mkdir -p "$AUTOSTART_DIR"
    echo "autostart -> $AUTOSTART_DIR/poketokenbar.desktop"
    cp "$DESKTOP_FILE" "$AUTOSTART_DIR/poketokenbar.desktop"
fi

command -v update-desktop-database >/dev/null && update-desktop-database "$APPS_DIR" || true
command -v gtk-update-icon-cache >/dev/null && \
    gtk-update-icon-cache -f -t "$DATA_HOME/icons/hicolor" 2>/dev/null || true

echo "done      -> search your application menu for \"PokeTokenBar\""

# PokeTokenBar for Linux

Raise a Pokémon with the Claude Code tokens you're already burning — in your
Linux system tray.

A Linux port of [PokeTokenBar for Windows](https://github.com/NMHK-134711/PokeTokenBar-for-Windows),
itself a from-scratch implementation of the idea behind
[chattymin/PokeTokenBar](https://github.com/chattymin/PokeTokenBar) (macOS,
Swift 6, menu-bar only). No Swift (or Windows-specific) code is ported; the
data sources and the game rules are the same Python, with the tray, the
floating pet's window shaping, and the data directory swapped for their Linux
equivalents — see [Porting notes](#porting-notes-from-the-windows-version)
below. The app also still runs unmodified on Windows.

[chattymin/PokeTokenBar](https://github.com/chattymin/PokeTokenBar) 위 깃허브 내용을 리눅스에서도 즐기고싶어 만든 코드입니다.
기능과 내용을 리눅스에서 작동하도록 새로 코딩해 구현하였습니다.

UI는 한국어가 기본입니다 (설정에서 English로 바꿀 수 있습니다).

<table>
<tr>
<td width="50%"><img src="docs/home.png" alt="Home tab: a shiny Dragonair being raised, today's tokens and cost, the 5-hour window with a countdown"></td>
<td width="50%"><img src="docs/pokedex.png" alt="Pokedex: a grid of owned species with rarity-coloured borders and page navigation"></td>
</tr>
<tr>
<td align="center"><b>Home</b> — what you're raising, and what it cost</td>
<td align="center"><b>Pokédex</b> — 24 per page, rarity-coloured, click to pin</td>
</tr>
</table>

## Install

**System packages first.** The tray icon and the floating pet need two things
most distros don't install by default: Tk (tkinter), and a tray-icon backend —
either GTK's AppIndicator (any desktop that speaks the StatusNotifierItem
protocol: KDE Plasma, GNOME-with-the-AppIndicator-extension, Cinnamon, XFCE,
LXQt, Budgie, ...) or an Xorg fallback pystray also understands.

```bash
# Arch / Manjaro
sudo pacman -S tk python-gobject libayatana-appindicator

# Debian / Ubuntu
sudo apt install python3-tk gir1.2-ayatanaappindicator3-0.1 python3-gi

# Fedora
sudo dnf install python3-tkinter libappindicator-gtk3 python3-gobject
```

These three are system packages (they wrap GObject introspection data and a
compiled Tk), not pip packages, which is why they are not in
`requirements.txt`. pystray falls back to a plain Xorg tray icon if no
AppIndicator implementation is found, and the floating pet still works without
one of its own — see [Porting notes](#porting-notes-from-the-windows-version).

**Then the app itself:**

```bash
pip install -r requirements.txt
python3 -m poketokenbar
```

Requires Python 3.10+.

**Application-menu launcher (optional).** `packaging/linux/install.sh` draws
the egg icon, writes a `.desktop` entry into your user application menu, and
(with `--autostart`) a copy that launches on login:

```bash
./packaging/linux/install.sh            # adds it to your app launcher
./packaging/linux/install.sh --autostart  # + starts it on login
```

It runs `python3 -m poketokenbar` with this checkout on `PYTHONPATH`, so
`requirements.txt` must already be installed for whichever `python3` is first
on your `PATH`; set `PYTHON=/path/to/venv/bin/python3` before the command to
point it at a virtualenv instead.

**The tray icon starts hidden**, same as upstream on Windows: most desktops
put a brand-new tray icon in an overflow drawer — look for a `>` or `v`
chevron near the clock — and let you drag it out from there to keep it
visible.

**On Windows**, `build.py` still produces a standalone `PokeTokenBar.exe` via
PyInstaller (`pip install pyinstaller && python build.py`), and `run.pyw` is
still the windowless double-click launcher; neither changed in this port.

## What it does

Every token you spend in Claude Code incubates an egg. The egg hatches into a
Gen 1–5 Pokémon — one of **329 possible starting species**, weighted by the
official capture rate, so a legendary lands about **once in 136 hatches**. It
grows through its real evolution line, graduates into your Pokédex, and a fresh
egg arrives.

Underneath the companion it's an exact usage tracker: today's tokens and cost,
the current 5-hour block, 7- and 30-day rolling totals, and a burn-rate forecast.

| Surface | What's on it |
|---|---|
| **Tray icon** | Animated Gen-V sprite; hover for today's tokens, cost, and window % |
| **Floating pet** | Optional always-on-top companion with the token count under it — drag anywhere, hover for detail, click to open the window, right-click for a menu, and it pipes up when something happens |
| **Home** | Companion, growth bar, today's spend, 5-hour and weekly meters, burn rate |
| **Pokédex** | Every species you've owned, plus a catch log of everything you've raised |
| **Pin a favourite** | Click any owned species to pin it to the tray icon and desktop pet |
| **Bag / Shop** | Rare Candy, Mints, Shiny Charms, and graded eggs, bought with tokens |

Shiny hatches (~1 in 256, better with Shiny Charms) keep their colours through
every evolution.

<table>
<tr>
<td width="50%"><img src="docs/catch-log.png" alt="Catch log: each Pokemon raised, shown as its full evolution line with rarity and nature"></td>
<td width="100%"><img src="docs/floating-pet.png" alt="The floating desktop pet with its hover readout"></td>
</tr>
<tr>
<td align="center"><b>Catch log</b> — every line you've raised</td>
<td align="center"><b>Desktop pet</b> — hover for the detail</td>
</tr>
<tr>
<td><img src="docs/shop.png" alt="Shop: Rare Candy, Mint, Shiny Charm and three grades of egg, priced in tokens"></td>
<td><img src="docs/settings.png" alt="Settings: refresh interval, budgets, window reset time, pet size, language and the data folder"></td>
</tr>
<tr>
<td align="center"><b>Shop</b> — your usage is the currency</td>
<td align="center"><b>Settings</b> — budgets, reset time, language</td>
</tr>
</table>

**The floating pet is interactive.** Hovering shows today's tokens and cost, the
5-hour window with its countdown, the weekly figure, and what you're raising.
Right-click for open / refresh / unpin / hide / quit. Hatches, evolutions, and a
filled 5-hour window arrive as a speech bubble above it.

**The weekly window resets** if you tell it when. Weekly limits roll over on a
fixed weekday and time, so put that into **Weekly reset day and time** in
Settings (`Thu 04:00`, `금 04:00`, `thu 4` all parse) and the meter counts from
the last reset and says *This week*. Left empty it totals a rolling 7 days,
which never resets — accurate, but it will not drop when your real limit does.

**Reset countdowns** sit in the meters — `100% (217.2M · 2h 9m left)`. For Codex
the reset instant is the one it reports itself; for Claude Code it is the end of
the current 5-hour block. The weekly figure for Claude Code is a rolling 7 days
with no reset instant, so it shows no countdown.

**Pinning.** Clicking a species in the Pokédex pins it to the tray icon and the
desktop pet, so those stop changing at every hatch and evolution. The companion
carries on being raised underneath — Home still shows it and its progress — and
clicking the pinned cell again, or the Unpin button, hands the icon back to it.
Only species you already own can be pinned.

## Agents it reads

| Agent | Logs | Cost | Limits |
|---|---|---|---|
| **Claude Code** | `~/.claude/projects/**/*.jsonl` | list price per model | your own budgets |
| **Codex** | `~/.codex/sessions/**/*.jsonl` | not estimated | **official**, from the log |

Whichever agents are present are detected automatically. With two or more, chips
on the Home tab switch between each agent and a combined view; the companion is
always raised by the combined total, so every token counts whichever tool spent
it.

Codex records its own rate-limit utilisation (`rate_limits.primary` /
`secondary`, with reset timestamps) in its session log, so for Codex the app
shows the **real** 5-hour and weekly percentages rather than a budget you set.
It does not record per-model prices, so Codex tokens are counted but not costed
— an honest blank instead of a guess.

## Where the numbers come from

Usage is read directly from the local session logs the agents already write. No
external CLI, no account access, nothing uploaded.

- **Tokens (Claude Code)** = `input + output + cache creation + cache read`,
  deduplicated by `(message id, request id)`.
- **Tokens (Codex)** come from differencing the cumulative `total_token_usage`
  rather than summing the per-turn `last_token_usage`: Codex re-emits
  `token_count` without new work fairly often, and summing double-counts those
  (18% high on the log tested here). Differencing reproduces the session's own
  final total exactly. `cached_input_tokens` is already inside `input_tokens`,
  so it is not added twice.
- **Cost** is computed at public list prices per model, with cache writes billed
  at 1.25× input for the 5-minute TTL and 2× for the 1-hour TTL, and cache reads
  at 0.1×. The logs record the two TTLs separately, so this is exact rather than
  estimated. On a subscription plan, treat it as "what this would have cost on
  the API".
- **5-hour blocks** are derived from the log timestamps by default: a block
  opens on the hour of its first message and runs five hours; a gap of five
  hours also opens a new one. That mirrors the real limit, which starts its
  window when you send the first message after the previous one lapsed. If your
  windows sit on a schedule you already know, put one boundary (the reset time
  Claude Code's `/usage` shows you) into **5-hour window reset time** in
  Settings and the blocks line up with that clock instead.

Only two hosts are contacted, both for Pokémon data, never for your usage:
`raw.githubusercontent.com` (species tables and sprites) and nothing else.
Everything is cached under `~/.local/share/poketokenbar/` (or
`%LOCALAPPDATA%\PokeTokenBarWin\` on Windows).

### One deliberate difference from the macOS original

The original shows Anthropic's **official** 5-hour and weekly limit percentages
by reading an OAuth token out of the macOS Keychain and calling an unofficial
`api.anthropic.com` endpoint. This version does not. Desktop Linux and Windows
both store credentials differently from the macOS Keychain, and an undocumented
endpoint is a fragile thing to depend on — so the 5-hour and weekly meters run
against **budgets you set yourself** in Settings (defaults: 120M per window, 2B
per week). Filling one still earns a Rare Candy. Nothing here ever reads your
credentials.

## Tuning

Settings lets you change the refresh interval, both budgets, the 5-hour and
weekly reset points, the floating pet and its size, tooltip contents, and the UI language
(한국어 / English). Species names, natures, and rarities all follow the chosen
language — saves store the English keys, so switching language never invalidates
your Pokédex.

Settings also shows the data folder currently in use. That matters more than it
sounds: a sandboxed launcher can redirect `$XDG_DATA_HOME` (or
`%LOCALAPPDATA%` on Windows) elsewhere, so two copies started different ways
can quietly keep separate saves. If a companion seems to have vanished, check
this path first.

`~/.local/share/poketokenbar/config.json` (`$XDG_DATA_HOME/poketokenbar/` if
you've set that variable; `%LOCALAPPDATA%\PokeTokenBarWin\config.json` on
Windows) holds the same settings if you prefer editing them by hand; it is
read as UTF-8 with or without a BOM, so any editor is safe.

Game constants live at the top of `poketokenbar/game.py` — `EGG_HATCH_TOKENS`,
`BASE_GRADUATE_TOKENS`, `RARITY_MULTIPLIER`, and `SHOP_PRICES`. The defaults are
calibrated so that at heavy use (~100M tokens/day) a Common graduates in about
three days and a Legendary in about twenty-four, matching the original's stated
pacing. Lower `BASE_GRADUATE_TOKENS` if you use Claude Code less than that.

## Layout

```
poketokenbar/
  providers.py one class per agent: where its logs are and how to read them
  entry.py     a single call's usage, and list-price costing
  usage.py     merges every agent, dedupes, builds 5-hour blocks and rollups
  pokedata.py  species table + evolution trees from PokeAPI, sprite cache
  game.py      egg → hatch → evolve → graduate, Pokédex, bag, shop
  app.py       config, background refresh, sprite frame loading
  ui.py        main window and floating pet (tkinter)
  tray.py      system tray icon (pystray)
  x11shape.py  Linux-only: cuts the floating pet to its sprite's silhouette
  i18n.py      every UI string, in Korean and English
packaging/linux/ .desktop launcher + install.sh for the application menu
build.py       Windows only: draws the icon and runs PyInstaller for the .exe
```

### Adding another agent

Subclass `Source` in `providers.py` with `files()` and `parse()`, add it to
`all_sources()`, and it appears in the UI automatically. If the agent reports
its own rate limits, override `limits()` and its meters become official too.

### Replacing an icon

Create `poketokenbar/assets/` and drop a transparent PNG in, named after the
item key — `rare_candy.png`, `mint.png`, `shiny_charm.png`, or `egg.png`. It
takes priority over the fetched sprite. Any size works; icons are scaled with
nearest-neighbour when enlarging so pixel art stays crisp. The folder is absent
by default, and anything you put there is yours, not part of this project.

## Porting notes from the Windows version

Everything below `poketokenbar/usage.py`, `entry.py`, `game.py`, `pokedata.py`
and `i18n.py` is unmodified: usage parsing, pricing, and game rules don't know
or care what OS they're running on. What actually changed, and why:

- **Data directory.** `%LOCALAPPDATA%\PokeTokenBarWin\` becomes
  `$XDG_DATA_HOME/poketokenbar/` (`~/.local/share/poketokenbar/` by default) —
  the conventional place for an app's own state on Linux, same as `%LOCALAPPDATA%`
  is on Windows.
- **Single-instance lock.** `msvcrt.locking` becomes `fcntl.flock`; both are
  advisory, per-process locks the OS releases automatically on exit or crash,
  so the behaviour (a second launch quietly bows out) is identical.
- **The floating pet's transparent window.** Windows carves the sprite's
  silhouette out of the window by keying one background colour
  (`-transparentcolor`); X11 has no such attribute, so `x11shape.py` does the
  equivalent with the **Shape extension** instead — a 1-bit mask, built from
  the sprite's already-binarised alpha channel, applied to the window's
  bounding region after each render. This works the same way through XWayland,
  so it covers a Wayland session too, as long as `python-xlib` is installed and
  the compositor ships an XWayland server (every major one does). If shaping
  genuinely never becomes available, the pet still works — it is just a plain
  rounded card instead of a cut-out silhouette, rather than failing outright.
- **The tray backend.** pystray picks Win32 on Windows and, on Linux,
  whichever of AppIndicator / GTK / Xorg it finds (see Install above). One
  real UX gap survives this swap: the AppIndicator/StatusNotifierItem protocol
  has no notion of a plain left click separate from opening the menu, so
  Windows' double-click-to-open has no Linux equivalent — opening the window
  always goes through **Tray menu → Open**. Nothing in `tray.py` can paper
  over a difference in the underlying tray protocol.
- **Fonts.** "Segoe UI" only exists on Windows; `ui.py` picks "Noto Sans CJK
  KR" on Linux instead, both because it actually exists there and because the
  UI defaults to Korean. fontconfig substitutes a reasonable fallback if even
  that face is missing, the same way Tk/Win32 already does for an unknown
  family.
- **Animated tray icon.** AppIndicator has no in-memory icon update — every
  frame change is a PNG encode plus a temp file write (Win32 instead swaps an
  in-memory `HICON`) — so the animation interval is slower on Linux
  (`tray.py`'s `FRAME_MS`) to keep that off the hot path.
- **Packaging.** `build.py`/PyInstaller stays Windows-only (a `.exe` makes
  sense there; it doesn't on Linux, where `pip install` already covers the
  "no build step" case). `packaging/linux/` adds the Linux equivalent of "an
  icon you can click": a `.desktop` entry and an install script, in place of
  the Start Menu shortcut `run.pyw` is meant for.

## Licence & disclaimer

MIT for the code here. This is an unofficial, non-commercial fan project, **not
affiliated with, endorsed, or sponsored by Nintendo, Game Freak, Creatures Inc.,
or The Pokémon Company**. Pokémon and all related names and imagery are
trademarks of their respective owners. Provided as is, for personal use only.

**No Pokémon artwork is bundled into the program.** Species data, Pokémon
sprites, the egg, and every item icon are fetched at runtime from the public
[PokéAPI](https://pokeapi.co) and cached under the user's own data directory
(`~/.local/share/poketokenbar/` on Linux, `%LOCALAPPDATA%` on Windows); none of
it is compiled into the executable or shipped as a source asset. The app
icon is a plain egg the program draws itself. PokéAPI has no mint sprite in any
flavour, so the Mint item borrows the Ability Urge icon — also fetched, not
shipped.

The screenshots under `docs/` are the exception: they necessarily contain
Pokémon imagery, and are included solely to illustrate what the application
does.

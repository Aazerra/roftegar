# roftegar

`roftegar` is a Python TUI for browsing directory sizes and monitoring basic system usage from the terminal. It is built with [Textual](https://textual.textualize.io/) and ships with a plugin-based startup menu.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- Startup menu for choosing a plugin
- Disk analyzer with directory navigation and size scanning
- Live system usage dashboard for CPU, memory, swap, and disk
- Vim-style keybinds for fast keyboard navigation
- Progress reporting while large directory trees are being scanned

## Built-in Plugins

- `disk_analyzer` - browse directories, inspect sizes, and delete entries with confirmation
- `system_usage` - view live CPU, memory, swap, and disk usage

## Requirements

- Python 3.10 or newer
- Linux, Windows, or another terminal environment supported by Textual

## Installation

### From source

```bash
git clone git@github.com:Aazerra/roftegar.git
cd roftegar
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run the app

```bash
roftegar
```

If the editable install is not activated, run the entry point directly from the virtual environment:

```bash
.venv/bin/roftegar
```

## Usage

When the app starts, you will see a menu of available plugins.

### Startup menu

- `j` / `k` - move down and up
- `l` or `Enter` - open the selected plugin
- `m` - return to the startup menu after opening a plugin
- `q` - quit

### Disk analyzer

- `j` / `k` - move through files and directories
- `l` or `Enter` - open the selected directory
- `h` or `Backspace` / `Left` - go up one level
- `Ctrl+H` - toggle hidden files
- `s` - toggle sorting mode
- `r` - refresh the current directory
- `d` or `Delete` - delete the selected entry after confirmation

### System usage

- `r` - refresh the live system metrics manually

## Development

The project uses `hatchling` for packaging and exposes a console script named `roftegar`.

```bash
pip install -e .
python -m compileall roftegar
```

## Project Layout

```text
roftegar/
├── pyproject.toml
├── README.md
├── agent.md
├── progress.md
└── roftegar/
    ├── __main__.py
    ├── app.py
    ├── plugin.py
    ├── registry.py
    ├── scanner.py
    ├── roftegar.tcss
    ├── plugins/
    └── widgets/
```

## Notes

- The app uses a plugin registry, so new features should generally be added as new plugins.
- Large directory scans are handled in the background to keep the UI responsive.
- See `progress.md` for the current project status and recent work.
- The project is licensed under the MIT License. See `LICENSE` for the full text.

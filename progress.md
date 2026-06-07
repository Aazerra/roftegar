# Progress Report

## 2026-06-07 11:57
- Added a GitHub Actions workflow to build and upload a Debian package artifact (`.deb`) on push, pull request, and manual runs.

## 2026-06-07 11:49
- Added a new instruction in `agent.md` requiring timestamped progress entries in `progress.md` whenever an agent adds a feature.

## Current State
- Renamed the Python package and app branding to `roftegar`.
- Kept the plugin-based architecture with two built-in plugins:
  - `disk_analyzer`
  - `system_usage`
- Added startup menu flow so the app opens with a plugin chooser instead of the old sidebar.
- Added vim-style navigation bindings for the startup menu and disk analyzer.
- Added packaging metadata so the stylesheet ships with the wheel.

## Validation Completed
- Editable install works.
- `roftegar` imports cleanly and registers both plugins.
- Project metadata parses correctly.

## Notes for Future Work
- If more plugins are added, register them in `roftegar/plugins/__init__.py`.
- If release packaging changes, update both `pyproject.toml` and `.github/workflows/release.yml`.

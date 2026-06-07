# Progress Report

## 2026-06-07 12:30
- Fixed Arch release CI by passing repository URL into the Docker container and using that value in `PKGBUILD` to avoid unbound `GITHUB_REPOSITORY` errors under `set -u`.

## 2026-06-07 12:28
- Fixed Arch release version parsing command quoting in CI so `pyproject.toml` is read as a string literal inside the container Python invocation.

## 2026-06-07 12:26
- Fixed Arch release workflow shell parsing by replacing nested heredoc version parsing with a one-line Python command inside the container script.

## 2026-06-07 12:25
- Fixed Arch Linux release CI failure caused by an externally managed Python environment by creating a virtual environment before installing and running `pyinstaller`.

## 2026-06-07 12:23
- Fixed Arch Linux release build in CI by installing `pyinstaller` via pip inside the Arch container instead of using pacman.

## 2026-06-07 12:19
- Added Arch Linux release packaging in the tag-based release workflow and upload of `.pkg.tar.zst` artifacts to GitHub Releases.

## 2026-06-07 12:02
- Added a tag-triggered GitHub Actions release workflow that builds Linux `.deb` and Windows `.exe` artifacts and uploads them to GitHub Releases.

## 2026-06-07 12:02
- Added a GitHub Actions workflow to build and upload a Windows standalone executable (`.exe`) using PyInstaller.

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

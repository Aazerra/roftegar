# Agent Instructions for roftegar

## Purpose
Use this file as the working guide when adding or changing features in this repository.

## What to do first
- Read the affected files before editing.
- Prefer the smallest change that solves the request.
- Keep the plugin architecture intact unless the user asks to change it.

## Feature workflow
- Identify the owning module for the behavior.
- Make the change in the closest layer that controls it.
- Update imports, plugin registration, and packaging metadata if names or entry points change.
- If a new feature affects startup behavior, update the startup menu and plugin registry together.
- When an agent adds a new feature, append a progress entry to `progress.md` with a datetimestamp and a short summary of what changed.
- Use a consistent entry format in `progress.md`, for example: `YYYY-MM-DD HH:MM - summary`.

## Editing rules
- Use `apply_patch` for manual file edits.
- Preserve existing style and avoid unrelated formatting changes.
- Do not rename classes or symbols unless the change requires it.

## Validation rules
- Run an import smoke test after code changes.
- Run a packaging or install check after project metadata changes.
- If workflows are added or changed, verify the YAML is structurally valid.

## Current project shape
- Package name: `roftegar`
- Main app: `roftegar.app.SysmonApp`
- Built-in plugins live under `roftegar.plugins`
- Release artifacts are built through GitHub Actions

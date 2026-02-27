# Copilot Instructions for Crewbot1501

## Repository Overview
Crewbot1501 is a repository currently in early setup. This file provides guidance for GitHub Copilot coding agent when working in this repository.

## Repository Structure
- `README.md` – Top-level project description.
- `.github/copilot-instructions.md` – This file; repository-wide instructions for Copilot.

## General Guidelines
- Keep changes minimal and focused on the task at hand.
- Follow existing code style and conventions when adding new files or code.
- Prefer clarity and simplicity over clever abstractions.
- Add comments only when they meaningfully explain non-obvious logic.

## Working in This Repository
- There are currently no build, lint, or test pipelines configured. Do not assume any CI tooling is present unless it is explicitly added and documented.
- When adding new code, prefer standard tooling for the language being used (e.g., `npm` for JavaScript/TypeScript, `pip`/`poetry` for Python).
- When in doubt about project conventions, refer to the README or ask the maintainer.

## Pull Requests
- Keep pull requests small and focused on a single concern.
- Provide a clear description of what changed and why.
- Avoid including generated files, build artifacts, or `node_modules` in commits.

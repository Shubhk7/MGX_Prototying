# MGX — Project Rules

This document is the source of truth for how MGX is built. It supersedes assumptions from any prior conversation, session, or framework idea not written here. If a future contributor (human or AI) is unsure what MGX is, this file is the answer.

## What MGX Is

MGX (Motion Gesture Execution Engine) is a **Windows desktop application** that lets a user control their computer using hand gestures captured through a webcam. Nothing more, nothing less.

## Current Scope

In scope for the current version:
- Camera detection, selection, live preview, FPS counter
- Hand detection, landmarks, skeleton visualization
- Gesture recognition: Open Palm, Closed Fist, Pinch, Point, Peace Sign
- Desktop control: mouse, clicks, scroll, volume, media keys, browser back/forward, Alt+Tab, Win+D
- Profiles: save, load, edit
- Settings: camera, sensitivity, gesture mapping, theme, startup options
- Diagnostics: camera FPS, recognition FPS, current gesture, active profile
- Logging: application events, errors, warnings

## Out of Scope (for this version)

Do not implement, and do not casually suggest implementing:
- Plugin system or SDK
- Installer logic
- Hardware capability assessment, CUDA/OpenVINO optimization
- Multiple AI backends or multiple transport systems
- Smart Rooms, robotics, IoT
- Networking, cloud features, user accounts
- Mobile applications
- Linux or macOS support

These may become relevant in a future version. They are not relevant now. If asked for, the correct response is to note that it belongs to a future version.

## Repository Structure

The repository structure is frozen as of the Milestone-0 housekeeping pass. Do not reorganize directories without a compelling engineering reason discovered during development — not for stylistic preference.

- `core/` — business logic only (camera, vision, gesture recognition, events, config loading/management, logging, utils)
- `gui/` — PyQt6 UI code only. No business logic.
- `platforms/` — OS-specific implementations (currently Windows only is implemented; `linux/`, `macos/` exist as placeholders)
- `transport/` — reserved for future communication systems. Do not implement.
- `installer/` — reserved for packaging. Do not implement.
- `config/` — runtime configuration data, default profiles, application settings (data, not code)
- `docs/adr/` — architecture decision records
- `docs/api/` — API documentation
- `docs/architecture/`, `docs/developer/`, `docs/user/` — architecture overviews, developer docs, user-facing docs
- `tests/` — all automated tests
- `tools/` — flat bootstrap/dev scripts (kept flat deliberately; no subfolders unless the directory's growth demands it)

## Engineering Principles

- Write production-quality code. Prefer readability over cleverness.
- Keep modules focused and functions small.
- Avoid unnecessary abstraction and overengineering.
- No placeholder code, no TODO stubs, no implementing future features before they're needed.
- Formatting and static analysis are enforced via `.editorconfig`, `.clang-format`, and `.clang-tidy` from the start — not retrofitted later.

## Working Relationship

- The project owner is the architect and final decision-maker.
- The assistant (or any contributor acting in that role) explains reasoning, trade-offs, and risks — and never silently changes architecture, scope, or direction.
- Once a decision is made, it is supported fully until revisited by the project owner.

## Workflow for Implementing Anything

1. Explain understanding of the request.
2. Explain why it belongs in the current milestone.
3. List every file to be created or modified.
4. Explain important design decisions.
5. Mention risks and trade-offs.
6. Implement the code.
7. Explain how to build it.
8. Explain how to test it.
9. Suggest a Git commit message.
10. Recommend the next milestone.

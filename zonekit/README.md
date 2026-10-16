# ImmersivePDA — engineering log

What each kit check and each in-game test showed, newest at the bottom. Record dead ends here so they are never
retried. Plan: [../PLAN.md](../PLAN.md); reproducible edits: [../BUILD.md](../BUILD.md). Facts that hold for any
mod go to `harness/docs/` instead (promote them).

## 2026-10-16 — repo created from the harness

## 2026-10-16 — kit research and Slop yCam
- PDA flow, animation, UI and input read from the kit (dumps, cfgs, two read-only headless commandlets):
  `research/2026-10-16-pda-kit-research.md`; scripts in `tools/research/` (`inspect_pda*.py` run through
  `harness/tools/run_headless.ps1`, `allnames.py` / `tagscan.py` on extracted packages).
- Slop yCam 8.10.5 as installed on the dev box (ASI + native DLL, no paks): `research/2026-10-16-slop-ycam-research.md`.
- Result: the fullscreen look = device held 13 cm before the eye + fullscreen `W_PDABookView`; yCam suspends itself
  while `IsUsingPDA`. Two routes in PLAN.md, waiting on the tester's pick.

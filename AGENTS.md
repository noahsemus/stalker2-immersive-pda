# ImmersivePDA — mod context for the agent

**First read `harness/AGENTS.md`**: the shared rules, tester workflow, pipeline and game knowledge for every
Stalker 2 mod. They apply here. This file holds only what is specific to this mod.

Purpose: Skif raises the PDA in his hand instead of it filling the screen: the world stays visible around it, free look works, and it goes away fast.

Repo `noahsemus/stalker2-immersive-pda`, Zone Kit plugin `ImmersivePDA` (`/ImmersivePDA/`), asset prefix `ImmPDA`. Created from the
harness on 2026-10-16.

## Current state (one line per checkpoint / release: date, what changed, what the tester confirmed in game)
- 2026-10-16: repo created; kit research and Slop yCam research done (`zonekit/research/`), PLAN.md written with
  two routes. Waiting on the tester: pick `ImmersivePDA` in the editor's toolbar mod selector once (GameFeatureData),
  a preview of `MG_fp_pda_EMP_a`.
- 2026-10-16: tester decided: Route A (real PDA in hand), WASD walks while it is up, looking around = our copy of
  Slop yCam's Free Look (same key / feel, from his yCam profile). PLAN.md § Decisions.

## Key facts (verified; cite file:line in the kit)
- The fullscreen look = `MG_fp_pda` idle holds `SK_pda` 13 cm before the eye (no FOV / camera change) +
  fullscreen UMG `W_PDABookView` (`CoreVariables.cfg:932`) opened by `AnimNotify_UseHandItem` at 0.833 s.
- Every PDA page pushes an Exclusive context without look / walk rows (`InputMappingContextPrototypes.cfg:59-228`).
- `MG_fp_pda_EMP_a` holds the device ~34 cm ahead with no UI: the base for our held pose.
- Slop yCam 8.10.5 suspends itself while `IsUsingPDA`, cancels Free Look on a visible cursor, and must keep the
  pawn camera parented to the mesh (`harness/docs/compatibility.md`).

## Assets this mod may override
- _(none yet; see harness/docs/compatibility.md before adding any)_

## Files
- `PLAN.md` plan and test matrix · `BUILD.md` every edit asset by asset · `zonekit/README.md` engineering log
  (what each test showed, dead ends) · `zonekit/ImmersivePDA/` plugin mirror · `zonekit/tools/` mod-specific generators
  and classifier lists · `zonekit/builds/` checkpoint and release paks · `mod.json` names and pak suffixes.
- `CLAUDE.md` / `GEMINI.md` only import `harness/AGENTS.md` and this file, for tools that don't read `AGENTS.md`.

## Release (only when the tester says "cut a release")
Follow `harness/docs/pipeline.md` § Release. Nexus page: _(record the mod id here once it exists)_.

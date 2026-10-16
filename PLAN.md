# ImmersivePDA — plan

Skif raises the PDA in his hand instead of it filling the screen: the world stays visible around it, free look works, and it goes away fast.

## How the game does it today (evidence: kit file:line, probe runs, tester reports)
Full notes: `zonekit/research/2026-10-16-pda-kit-research.md` (PDA) and `zonekit/research/2026-10-16-slop-ycam-research.md`
(Slop yCam). Short form:
- P (`IA_OpenPDA`, `IMC_Exploration`) -> native `PDAOpenIPU` -> `PC.StartUsePDA` -> USE_PDA. `MG_fp_pda` (2.3 s,
  MainActionSlot) raises `SK_pda`; at 0.833 s `AnimNotify_UseHandItem` opens `W_PDABookView`; the Idle section loops;
  close plays Out / OutFast.
- **The "takes over the screen" has two parts**: (1) the idle pose holds the device 13 cm before the eye, dead centre
  (fills the 90 deg view; no FOV change, no camera modifier; camera pitches -20 deg); (2) `W_PDABookView` is a
  fullscreen UMG view (frame art `T_pda_*` all around, cursor on). The device's own screen is plain emissive blue.
- Every PDA page pushes an **Exclusive** input context with no look / walk rows: look and walking are dead while it is
  open; WASD pans the map, the mouse drives a cursor. The world keeps running (no time dilation in the data;
  to confirm in game).
- `MG_fp_pda_EMP_a` (3 s, no UI) already holds the device ~34 cm ahead, 4 cm below centre, world visible around it.
- Slop yCam 8.10.5 (installed; no paks, ASI + DLL): **suspends itself completely while `IsUsingPDA()`** (camera
  handed back, Free Look off) and cancels Free Look whenever a mouse cursor shows. Its Free Look = hold
  `ThumbMouseButton` (tester's profile), via `SetIgnoreLookInput`; it refuses to start if look input is already
  ignored, and switches off if anyone re-parents the camera.

## Decisions (tester, 2026-10-16)
- **Route A**: the real PDA, held in the hand, UI on the device, world around it.
- **Walking while it is up: yes, WASD walks**; the map pans by mouse drag (and arrow keys).
- **Looking around: our copy of Slop yCam's Free Look** while the PDA is up (yCam's own is off in the PDA by its
  code): hold the button from yCam's `profile.ini` (`freelook_key`, tester: `ThumbMouseButton`), its sensitivity,
  limits (yaw 75 / pitch 40), return speed and torso follow; read the profile at runtime if a Blueprint can (else
  ship the defaults + MCM), fall back to yCam's defaults when yCam is absent. While held: cursor hidden, mouse turns
  the view, the device stays put. Released / PDA closed: ease back, hand everything to yCam (camera parent
  untouched, `SetIgnoreLookInput` balanced).
- The world keeps running in the PDA (tester: as vanilla).

## Approach, cheapest and least conflicting first
Two routes; the tester picks (open question 1). Both need the same building blocks: a NewContent runtime host
(`BP_ImmPDASubsystem` -> `BP_ImmPDAActor`, `harness/docs/runtime-host.md`), a held pose of our own made from the
EMP_a hold frames (`AS_ImmPDA_Hold*`, pitch-aware so the device follows the view), no camera / pawn overrides.

**Route A: the real PDA, held in the hand.** Vanilla opens as today (all pages, markers, map work). Our actor:
1. replaces the 13 cm idle with our held pose (device ~35-40 cm out, lower centre) once the UI is open;
2. finds the live `W_PDABookView` and each tick sets its render transform so the UI sits on the device screen
   (project the screen corners of `SK_pda` to the viewport), hiding the outer frame art;
3. look: hold a key -> cursor hidden, the mouse turns the view (our own look: yCam is off in the PDA by its design).
   Needs a mod context that beats the Exclusive page context (canary test first) or polling the raw mouse delta;
4. walking while it is up (if wanted): our context feeds `SetMoveVector`; WASD then stops panning the map.

**Route B: glance mode, full PDA on demand.** P raises our own device (`SK_pda` attached to the hand, our pose,
never USE_PDA) with the live map on its screen (`RT_WorldMap` in a mod material, player arrow + markers drawn by us).
You walk, look and use yCam's Free Look normally; P / Esc lowers it. Click (or a second key) = vanilla's full PDA for
markers / journal / notes. Overrides nothing; more of our own UI.

| Layer | Change | Ships as | Conflicts |
|---|---|---|---|
| 1 | Runtime host + held pose + device placement | NewContent | none |
| 2A | Live `W_PDABookView` moved / scaled onto the device each tick | NewContent (runtime) | UI mods restyling the PDA (none known) |
| 2B | Own device screen material (`RT_WorldMap`) + overlay | NewContent | none |
| 3 | Look / walk while raised: mod IMC | NewContent | other mods' contexts above Exclusive |
| fallback | `AnimCollection_fp_pda` / `MG_fp_pda` override, only if a runtime pose swap cannot win over MainActionSlot | override pak | No Wasted Movement (edits 1,407 vanilla montages), PDA speed mods |

## Open questions and how each gets answered
| Question | Answered by |
|---|---|
| 1-2. Route, look, walking | decided (above) |
| 3. What does holding P 1 s do (the world keeps running: tester) | tester, one look in game |
| 3b. How to turn the view without touching the camera's parent: camera relative rotation (yCam is detached in the PDA) vs `jnt_camera` pose | kit + build; restore before yCam re-binds |
| 3c. Can a Blueprint read yCam's `profile.ini` (no file API in BP?) | kit grep for file / config read nodes |
| 4. Does `MG_fp_pda_EMP_a` show the device with the screen visible at a good distance | tester previews it in the editor |
| 5. Can a mod montage / pose win over `MG_fp_pda` in MainActionSlot under `AnimBP_Player_TwoHandedItem` | kit read of the posture AnimBP, then a build |
| 6. Can a mod input context beat the Exclusive `IMC_PDA_*` contexts | canary build |
| 7. Is `IsLookInputIgnored` / UI-only input mode set while the PDA is open | probe riding along on build 1 |
| 8. `W_PDABookView` render transform settable at runtime without breaking map clicks (UMG hit-testing follows the render transform) | build |

## Test matrix (all must pass before a release)
| # | Setup | Steps | Expected |
|---|---|---|---|
| 1 | vanilla keys, keyboard | P, M, J, K open; Esc / P close | PDA in hand, world visible around it, page right |
| 2 | Slop yCam on | open PDA, look around (our key / yCam Free Look per route), close | no camera jump on open / close, yCam back after close |
| 3 | quick put-away | open, close at once, mid raise, mid lower; spam P | no stuck pose, weapon back |
| 4 | armed: rifle, pistol, knife, bolt, detector, bare hands | open / close | right hand back on the item it had |
| 5 | map use | pan, zoom, place / remove marker, track quest | works as vanilla |
| 6 | combat / damage / sprint / crouch / ladder | open in each | sane (vanilla refusals kept) |
| 7 | rebound keys | as 1 | rebinds honoured |
| 8 | gamepad | as 1, look | works |
| 9 | with our other mods (Looting incl. Instant Intel note open, Dialogue, Campfires, Reloading) | open PDA around each | no conflict |
| 10 | save / load with PDA up, death, cutscene starting | — | clean state |

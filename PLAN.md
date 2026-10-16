# ImmersivePDA — plan

Skif raises the PDA in his hand instead of it filling the screen: the world stays visible around it, free look works, and it goes away fast.

## How the game does it today (evidence: kit file:line, probe runs, tester reports)
_(research first: harness/docs/zonekit.md)_

## Approach, cheapest and least conflicting first
Prefer, in order: a cfg patch file → a NewContent runtime host (ModWorldSubsystem + actor) → an asset override
(only with the tester's explicit decision; list who else overrides it).

| Layer | Change | Ships as | Conflicts |
|---|---|---|---|
| 1 | | | |

## Open questions and how each gets answered
| Question | Answered by (kit grep / tester opens asset / probe / test run) |
|---|---|

## Test matrix (all must pass before a release)
| # | Setup | Steps | Expected |
|---|---|---|---|
| 1 | vanilla keys, keyboard | | |
| 2 | rebound keys | | |
| 3 | gamepad | | |
| 4 | with our other mods installed | | |
| 5 | save / load mid-action, death, cutscene | | |

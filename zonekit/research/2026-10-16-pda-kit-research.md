# Vanilla PDA: kit research (2026-10-16, read-only)

Sources: `<kit>` = `G:/Epic Games/STALKER2ZoneKit`. `dump2` = `<kit>/bp_api_dump2.txt`, `dump1` = `<kit>/bp_api_dump.txt`,
cfgs under `<kit>/Stalker2/Content/GameLite/GameData/`. Asset facts come from two read-only headless editor passes
(`pda_scripts/inspect_pda.py`, `inspect_pda2.py` → `headless_out.txt`, `headless_out2.txt` here) and from name tables /
tagged-property scans of assets pulled from the FullEditor pak (`assets/`, `names/`; montage sections read with
`pda_scripts/tagscan.py`). Pak index reused from the Dialogue session:
`C:/Users/noahs/AppData/Local/Temp/claude/C--Users-noahs-OneDrive-Documents-GitHub-stalker2-immersive-dialogue/bfe98bcc-3ef9-41df-805a-89d5a560b0bc/scratchpad/pak_index_full.txt`
(with offsets; cleaned copy `index_clean.txt`, PDA subset `pda_assets.txt`).

Tags: **[V]** verified from data, **[I]** inferred, **[?]** open (needs the editor or a game test).

---------------------------------------------------------------------------------------------------------------------
## 1. Open / close flow

### Input actions and contexts [V]
- `IMC_Exploration` (`InputMappingContextPrototypes.cfg:10-17`, priority **Lowest**) holds the PDA openers
  (asset `/Game/_Stalker_2/data/input/InputMappingContexts/IMC_Exploration`, read headless):
  - `IA_OpenPDA`: **P** (mappable `OpenPDA`), `OpenPDAAlt` (unbound), `Gamepad_Special_Left` (View/Touchpad button).
    Row triggers on the keyboard rows: `InputTriggerTap` (release < 0.5 s) **and** `InputTriggerHold` (1.0 s,
    one-shot); gamepad row: Tap only. What the 1 s hold does is native [?] (ask the tester: "hold P one second").
  - `IA_WorldMap` **M** (`WorldMap`), `IA_Journal` **J**, `IA_Note` **K** open the PDA on a page (Pressed).
    `IA_Inventory` I, `IA_PauseMenu` Esc are neighbours.
  - The IA assets themselves carry no triggers/modifiers; `IA_OpenPDA`/`IA_UI_PDA_Close` are Boolean,
    `consume_input = True`, `trigger_when_paused = False`.
- Inside the PDA each page pushes its own context, **all Exclusive** (`InputMappingContextPrototypes.cfg`):
  `IMC_PDA_Map` 59-65 (`EMappingContext::Map`), `IMC_PDA_Journal` 66-72, `IMC_PDA_Note` 73-79,
  `IMC_PDA_Upgrades` / `UpgradesPopup` / `UpgradesNavigation` 113-133, `IMC_PDA_Encyclopedia` 178-184 (empty asset),
  `IMC_PDA_Stats` 185-191 (asset `IMC_Stats`), `IMC_PDATutorial` 222-228 (asset `IMC_PDA_Tutorial`). All have
  `IgnorePreviousPressedKeysOnRemove = true`. `EMappingContext` also has a plain `PDA = 10` value with no cfg row.
- `IMC_PDA_Map` rows (no look, no locomotion rows: the Exclusive context shadows `IMC_Exploration`, so **no free-look
  and no walking while the PDA is up** [V for the rows, I for the runtime effect]):
  - close: `IA_UI_PDA_Close` = Esc (Released), M (`WorldMap`), P (`OpenPDA`), pad B / View; also `IA_UI_Map_Exit`
    Esc / M / pad B / Menu (Down).
  - tabs: `IA_UI_PDA_MoveToPreviousSlot` Q (`PDA_MoveToPreviousSlot`) / pad LB, `IA_UI_PDA_MoveToNextSlot` E / pad RB
    (Pulse); direct page keys `IA_Journal` J, `IA_Note` K, `IA_Upgrades` U, `IA_Tutorial` O, `IA_Statistic`
    (unbound); `IA_UI_PDA_TransitionForward/Back/Release` (Hold 0.5 / 0.0, no keys).
  - map pan: `IA_UI_Map_NavigationUp/Down/Left/Right` = **W/S/A/D** + arrows, `IA_UI_Map_StickNavigation` left stick /
    D-pad / touchpad; zoom: `IA_UI_Map_ZoomIn/Out` mouse wheel up/down, +/-, right stick; `IA_UI_WorldMap_Scroll`
    wheel axis; `IA_UI_Map_MoveToPlayerPosition` V / LT; markers: RMB tap `IA_UI_Map_CreatePlayerMarker`, RMB hold /
    Tab `IA_UI_Map_OpenPlayerMarkSelector`, R delete, C hide markers, F `IA_UI_Map_ToggleMarkTracking`, L legend,
    J `IA_UI_Map_OpenQuestInJournal`; LMB `IA_UI_Map_SelectMarker_OnlyHint` (hint only: clicking is plain UMG mouse).
  - Journal / Note / Tutorial / Upgrades contexts: same Close/Prev/Next/page-key rows plus their own navigation
    (`IA_UI_Journal_*`, `IA_UI_Note_*` incl. `IA_UI_Note_PlayAudio`, `IA_UI_Upgrades_*`). Full rows in
    `headless_out.txt` lines 259-662.
- Referencers of `IA_OpenPDA`: `IMC_Exploration`, `IMC_QuestNotification`, `IMC_SystemNotifications`,
  tutorial quest `GDTQ00_BP`, `DA_InputElementsModels` (Options > Controls).

### Native code path [V names / I order]
- Handler class `PDAOpenIPU` (dump2:5431) has no BP members; `UIManagerEx` (dump2:7052) has 0 members.
  No BP-exposed API opens/closes views (game-facts.md; confirmed: no `open_view`/`on_view_*` anywhere in dump2).
- `PC` (dump2:5141): `is_using_pda()` (5224), `start_use_pda(initial_page_type=PDAPageType.NONE)` (5360),
  `on_pda_use_started_bp()` (5288) / `on_pda_use_ended_bp()` (5287) — BP events on the pawn class; the vanilla
  `BP_Stalker2Character` does **not** implement them (no PDA name in its name table) [V], so they are only usable by
  overriding the pawn (forbidden). `is_action_active(action_type)` (5210) with `ActionType.USE_PDA` (= 24) is the other
  pollable signal. `toggle_fov_and_foreground_render(enable)` (5369).
- Enums (editor Python): `PDAPageType` MAP=0, JOURNAL=1, NOTES=2, UPGRADES=3, STATISTIC=4, BESTIARY=5, TUTORIAL=6,
  NONE=255. `ActionType.USE_PDA = 24`; `PlayerTriggerState.USE_PDA_TRIGGER = 2199023255552`; `HandItem` NONE/BACKPACK/PDA;
  `WidgetNameEx.PDA = 10`, `BACKGROUND_BLUR_VIEW = 29`; `MappingContext` MAP=11, JOURNAL=12, NOTE=13, PDA=10,
  PDA_STATS=27, PDA_TUTORIAL=35, PDA_ENCYCLOPEDIA=26.
- Sequence [I, consistent with all data]: key → `PDAOpenIPU` → `PC.StartUsePDA(page)` → action `USE_PDA` → posture
  `AnimBP_Player_TwoHandedItem` linked, PDA device mesh spawned, montage `MG_fp_pda` section **In** plays →
  at **0.833 s** `AnimNotify_UseHandItem(HandItem=PDA)` → native opens `W_PDABookView` (view `PDA`) and pushes the
  page's IMC → section **Idle** loops while the view is open → on close: section **Out** (or **OutFast**), device montage
  re-synced by `AnimNotify_SyncAnimation` at 1.18 s → posture/weapon restored.
- Blocks [V from game-facts]: the open path refuses while `is_interaction_in_progress` (campfire sit). Instant Intel
  works via `PC.StartUsePDA(Notes)` from a mod (ImmersiveLooting 1.3.1) → the BP entry point works.
- No BP-visible delegate fires on PDA open/close [V for dump2]. Detect it by polling: `PC.IsUsingPDA`, or
  `EnhancedInputLocalPlayerSubsystem.HasMappingContext(IMC_PDA_*)`, or `GetAllWidgetsOfClass(PDAView)`.

---------------------------------------------------------------------------------------------------------------------
## 2. The animation

### Collection [V]
`/Game/_STALKER2/Animations/Weapons/items/pda/AnimCollections/AnimCollection_fp_pda` (class `ItemAnimCollection`):
- `use_item_animation` = { character `MG_fp_pda`, weapon (device) `MG_pda_fp`, play_rate 1 }
- `use_item_fast_animation` = { `MG_fp_pda_fast`, `MG_pda_fp_fast` } (when "fast" is chosen is native [?])
- `weapon_animations.player_anim_blueprint` = `AnimBP_Player_TwoHandedItem_C` (posture; the same one the backpack uses —
  never link it from a mod: animation.md crash family)
- also references `MG_fp_pda_EMP_a` / `MG_pda_fp_EMP_a` and `AnimCollection_fp_ar` (fields not visible to Python [?]).
- Referenced by `AnimBP_PDA` (device ABP, parent `AnimInstanceItem`, `item_anim_collection` dump2:1071; graph = one
  `DefaultSlot` + `BlueprintUpdateAnimation`/`TryGetPawnOwner`). `CoreVariables.cfg:892` `PDAAnimationBlueprint`,
  `AssetLibrary.cfg:62`.

### Player montage `MG_fp_pda` (`.../Player/AnimSequences/Items/pda/`) [V]
Length 2.3 s, slot **MainActionSlot** (group ActionGroup), default blend in/out 0.0 s.
| Section | Time | Sequence | Next |
|---|---|---|---|
| In | 0 – 1.0 | `AS_fp_pda_equip` (30 fr) | Idle |
| Idle | 1.0 – 1.133 | `AS_fp_pda_idle` (4 fr, static) | Idle (loop) |
| Out | 1.133 – 1.967 | `AS_fp_pda_unequip` (25 fr) | – |
| OutFast | 1.967 – 2.3 | `AS_fp_pda_interrupt` 0.5–0.833 (last 0.33 s) | – |

Notifies: MotionAudioEnveloper (0.048, 0.98 s; 1.38, 1.02 s; cloth sounds), AkEvent 0.077 (SFX_UI_PDA_Equip),
0.5 (SFX_PDA_PushButton), 1.52 and 1.906 (SFX_UI_PDA_Unequip), **UseHandItem(PDA) 0.833**, **SyncAnimation
(SYNC_WITH_SECONDARY_ITEM_IN_HANDS) 1.182 and 1.189**. No HandIK, no FOV, no camera notifies. `MG_fp_pda_fast`: same
sections and lengths (equip_fast / unequip_fast), UseHandItem 0.833, SyncAnimation 1.269.
`AS_fp_pda_*` are plain (non-additive) full-body sequences; no curves read.

### What the "zoom" really is [V numbers, I interpretation]
Component-space bone traces (relative to `jnt_camera`, which sits at z 160.3 and is a root child):
- `jnt_camera` **only rotates**: pitch 0 → **-20°** over the In section (camF z 0 → -0.34), held through Idle, back to
  0 in Out. It never translates (no dolly).
- The device: `SK_pda` skeleton `SKEL_pda` = `jnt_pda_fp` (root, constant at (18.4, 6.6, 147.5) = the player's
  `jnt_l_weapon` rest point) → `jnt_offset` (the device body) → `jnt_l_hand`, `jnt_r_hand`, `jnt_button_*`. The device
  anims are authored in the character's component space: in `AS_pda_fp_idle` the device's `jnt_l_hand`/`jnt_r_hand`
  equal the player's hand bones exactly. In idle `jnt_offset` = (12.4, 0.6, 155.8) → in the view frame **13 cm in
  front of the eye, dead centre**, its face (Z) pointing straight back at the camera. Device size (bounds): about
  17 × 28 × 2 cm. At 13 cm it covers the whole 90° view: that is the "camera zoom" — the PDA is brought to the face,
  then the fullscreen UI replaces it at 0.833 s.
- Hands in player idle (view frame): left ~15 cm ahead / 18 cm left / 2 cm down, right ~11 cm ahead / 18 cm right /
  13 cm down.
- `jnt_item` stays at the root origin in all PDA sequences (the PDA is not carried by `jnt_item` in first person;
  animation.md's note "jnt_item carries the PDA" is likely the third-person / cutscene case [?]).
- Device attach point on the character is native [?] (consistent with "SK_pda component at the mesh origin, its
  anim synced to the player montage"). `AssetLibrary.cfg:80` `PDASkeletal = SK_pda`, `:89` `PDAMaterial = MI_PDA`.

### `MG_fp_pda_EMP_a` — a vanilla "PDA held, world visible" pose [V numbers, I purpose]
3.0 s, one `Default` section, notifies = sounds only (no UseHandItem). Camera again pitches -20°, but the device
(`AS_pda_fp_EMP_a` `jnt_offset` ≈ (30.8, 0.5, 144.8), frames ~11-77 ≈ 0.37–2.57 s) is held **~34 cm in front, ~4 cm
below the view centre** — a "look at the PDA in your hands" pose with the world around it. Probably played when the
PDA is used inside an EMP area (`EMPArea` dump2:2782, `CoreVariables.cfg:323-326` `PDADisabledEffectSID =
PDADisabledEffect` (no such SID in any cfg), `PDADisabledMaterialPath = MI_PDA_Screen`, slot 1; `W_PDANoise` "no
signal" widget) [I]. Strong candidate as the base of our hold pose.

### Camera / FOV [V]
- No `AnimNotifyState_FOVBlend` (dump2:1183) or camera notify on any PDA asset. No PDA FOV in `CoreVariables.cfg`
  (only `FOVDefault = 90` :331, `DialogFOVDefault = 70` :333). The `CameraModifier_*` classes (dump2:1811-1821:
  AbilityCamModifier, LookAt, PsyAttackFocusTarget, ResetRelativeRotation) and `GSCCameraModifier(_PostProcess)`
  (3172-3177) have nothing PDA-specific. Whether native code calls `ToggleFOVAndForegroundRender` during the PDA [?].
- The device materials use the first-person foreground FOV correction: `MI_dev_pda` parent `MI_PBR_FOV`;
  `M_PDA_Screen` has `ForegroundFOVEnabled`, `MF_Foreground*`, `MPC_FOV` (see animation.md "arms are drawn squeezed").

---------------------------------------------------------------------------------------------------------------------
## 3. The UI [V]
- **Fullscreen UMG view**, not a 3D widget: `CoreVariables.cfg:932` / `AssetLibrary.cfg:49` `PDAClass =
  /Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDABookView` (parent native `PDAView` dump2:5594 → `BookViewBase` 1757 →
  `ViewBaseExtended` → `ViewBase` 7286). Tree: `MainOverlay` → `BackgroundOverlay` (decorative frame images
  `T_pda_*` top bar / frame lines / hints bar), `NavigationPanel` (W_PDANavigationPanel), `RegionWidget`,
  `TimeWidget`, `Container` → `SizeBox_258` → `Switcher` (WidgetSwitcher) with pages `MapPage` (W_MapPage),
  `JournalPage`, `NotesPage`, `UpgradePage`, `StatisticPage`, `BestiaryPage`, `TutorialPage`. Widget anims
  `PDAFadeInAnimation` / `PDAFadeOutAnimation`. No BackgroundBlur widget and no full-screen black image inside it.
- CDO values: `pda_turn_on_timer = 2.0`, `shold_show_input = False`, `should_enable_navigation = False`,
  `default_page_index = 0`, `widget_name = PDA`, `view_open_settings` = { shoud_show_mouse_cursor **True**,
  priority_z_order 11, close_type PRIORITY_AND_IGNORE_CLOSE_BY_NAME, close_widget_names [AutonomicTutorial,
  ReferenceTutorial, SplashTutorial, Interact], widgets_to_hide_this_when_open [GamePauseMenu],
  can_be_restored_after_pause True, shoud_clear_input_on_close True, shoud_ignore_input_on_pause False }.
  `W_Inventory` has the same settings (z 11, cursor, GamePauseMenu hides it). `ViewOpenSettings` struct: dump1:5647.
- Pages are `PDAPage` subclasses (dump2:5436, `pda_page`): `W_MapPage` (native `WorldMapPage` 7473,
  `should_bind_widget_inputs`, `shoud_ignore_input_on_pouse`, binds IA_UI_Map_* and IA_UI_PDA_Close itself, contains
  `W_PDANoise`, `W_MapZoomContainer` → `W_WorldMap`, tooltip, legend, hints).
- **The map image is a 3D scene captured to a render target**: `BP_WorldMapScene` (`CoreVariables.cfg:955`) = a plane
  with `M_WorldMapSceneMaterial` (unlit, `MapTexture` param) + an orthographic `SceneCaptureComponent2D` →
  `RT_WorldMap` (2048×1024, RGBA8 sRGB), shown in the UI by `M_WorldMapUIMaterial`. Markers / zones / player arrow
  are UMG children of `W_WorldMap` (`MarkerStorage`, `ZoneStorage`, `PlayerPosition`).
- **The device's own screen shows no UI**: `SK_pda` materials = `MI_dev_pda` (body) + slot `screen` =
  `MI_PDA_Screen` (parent `M_PDA_Screen`: opaque lit, emissive blue (0.29, 0.48, 1.0) ×4, no texture, no render
  target; switches `UseCutsceneTextures`, `UseEmissive`, `UseEyeAdaptation`; `Pick_Image` selects static
  `T_Cinematic_Map*` images in cutscenes via `MI_PDA_Screen_Cinematic_E03_MQ06_E15_MQ04`). Third-person `SK_pda_tp`
  uses the static `MI_dev_pda_map` (map photo texture).
- Background: `W_BackgroundBlurView` (`CoreVariables.cfg:984`, `WidgetNameEx.BACKGROUND_BLUR_VIEW`) is a separate
  view = one `BackgroundBlur` (strength 10), z −1, IGNORE_CLOSE, no cursor. Whether the PDA opens it with itself is
  native [?]; in practice the PDA pages cover the screen anyway. The pause menu has its own blur (5). No post-process
  asset tied to the PDA found.

---------------------------------------------------------------------------------------------------------------------
## 4. Pause, time, look, mouse
- Pause: nothing in the data makes the PDA pause. Its view settings mirror the inventory's; `GamePauseMenu` hides it
  and it is restored after the pause (`can_be_restored_after_pause`), which only makes sense for a non-pause view; the
  only time-dilation cfg is `ItemSelectorTimeDilationCoefficient = 0.3` (`CoreVariables.cfg:24`, the quick-item wheel).
  **[I] the world keeps running; confirm in game (open the map near a walking NPC / in a fight).**
- Look/move: blocked by the Exclusive page contexts (no `IA_LookUp` / locomotion rows) [V rows]; whether the native code
  additionally calls `SetIgnoreLookInput` / sets UI-only input mode [?] (probe `Controller.IsLookInputIgnored`,
  `IsMoveInputIgnored`, `bShowMouseCursor` while the PDA is open). The camera pitch is also pinned by the montage's
  absolute `jnt_camera` keys (-20°).
- Mouse: the view shows the OS cursor (`shoud_show_mouse_cursor`); map dragging / clicking is UMG mouse handling in the
  native `WorldMapPage`; wheel = zoom (IMC rows), RMB = marker, LMB = select.

---------------------------------------------------------------------------------------------------------------------
## 5. Levers for "PDA in hand, world visible, free look, quick put-away"
1. **`StartUsePDA` is BP-callable** and `IsUsingPDA` / `IsActionActive(USE_PDA)` / `HasMappingContext(IMC_PDA_*)` are
   pollable: a mod actor (runtime host) can open the vanilla PDA on a given page and detect open/close without any
   override.
2. **Hold pose without the fullscreen**: `MG_fp_pda_EMP_a` / `MG_pda_fp_EMP_a` already hold the device 34 cm away with
   the world visible. The device mesh and its sync only exist inside the native USE_PDA flow [I], so either
   (a) let vanilla run and swap what it plays (small override of `AnimCollection_fp_pda` → mod montages, or override
   `MG_fp_pda` / `AS_fp_pda_idle`; each is a conflict point, `AnimCollection_fp_pda` is referenced only by `AnimBP_PDA`
   and ReferenceHolder), or (b) our own path: play a mod montage built from the EMP_a hold frames in MainActionSlot /
   FullBody and attach our own `SK_pda` (or `SM_dev_pda`) component to the hand ourselves, never calling USE_PDA.
   A mod montage can leave `jnt_camera` unkeyed / additive so look stays live.
3. **The UI is a normal UMG view at runtime**: find the live `PDAView` widget (`GetAllWidgetsOfClass`) and change it
   from a mod actor without overriding the asset: `SetRenderScale/Translation`, hide `BackgroundOverlay` frame parts,
   set opacity; or don't open it and draw our own small UI. The map itself is a render target (`RT_WorldMap`), so a
   mod material on our device screen could show `RT_WorldMap` (or a `WidgetComponent` rendering a mod widget) — the
   vanilla screen material `MI_PDA_Screen` has no texture input, so this needs our own material.
4. **Input**: the page contexts are Exclusive and the view enables the cursor; free look needs either our own context
   above them carrying `IA_LookUp` (copy rows from `IMC_Exploration` incl. its `ApplySensitivity` modifiers, input.md
   techniques) — whether a mod context can beat "Exclusive" is the first thing to test with a canary — or not using the
   vanilla view/IMCs at all (option 2b) and mapping our own page keys.
5. **Quick put-away**: `OutFast` section (0.33 s tail of `AS_fp_pda_interrupt`) and the `_fast` variants exist;
   `Montage_JumpToSection("OutFast")` on the player montage is a cheap test once we know who drives the close.
6. HUD: no minimap in vanilla; compass is `UIRemaster/HUD/Compass/W_Compass` in `W_GameHUD`
   (`CoreVariables.cfg` HUDWidgetClass). Quest markers on the map are `W_WorldMapMarker` (`CoreVariables.cfg:951`).
7. Third-person / NPC "PDA in hand" exists only as contextual-action anims (`Characters/AnimSequences/bh/contextual/*pda*`,
   `CA_sit_*` cfgs) and cutscene `SK_PDA_*` meshes: nothing reusable for first person beyond the EMP_a set.

---------------------------------------------------------------------------------------------------------------------
## What only the editor / the game can answer (ask the tester)
Editor (open and screenshot):
1. `/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda_EMP_a` and `MG_fp_pda` — play them in the
   preview: does EMP_a show the device held at chest height with the screen visible? (preview mesh needs the PDA; the
   device montage is `/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/MG_pda_fp_EMP_a` on `SK_pda`).
2. `/Game/_STALKER2/Animations/Weapons/items/pda/AnimCollections/AnimCollection_fp_pda` — Details panel: which field
   holds the EMP_a montages, any other fields (fast-use condition?).
3. `/Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDABookView` — Designer hierarchy + Animations tab
   (PDAFadeIn/Out length, what they animate), Graph (does it do anything on construct?).
4. `/Game/_STALKER2/SkeletalMeshes/weapons/items/pda/SK_pda` — sockets list (Python can't read them).
5. `/Game/_STALKER2/Animations/Player/AnimBP_Player_TwoHandedItem` — which slots it evaluates and whether it
   uses `HandItemData` (to know if a FullBody / LeftHand mod montage over it shows).
Game (one run each, after a probe is proven to capture):
6. Does the world pause in the PDA? Does holding P for 1 s do something different from a tap?
7. Probe while the PDA is open: `IsLookInputIgnored`, `IsMoveInputIgnored`, `bShowMouseCursor`, active IMCs, whether
   `W_BackgroundBlurView` is in the viewport, the device component's attach parent/socket on the pawn.

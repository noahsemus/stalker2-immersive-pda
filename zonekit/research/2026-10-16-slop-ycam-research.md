# Slop yCam research (2026-10-16) for ImmersivePDA

V = verified from files on this PC; I = inferred.

## 1. Installed files (V)
Nexus mod 2746 "Slop yCam - Immersive Camera System". Installed build `standalone-native-asset-free-beta.8.10.5`
(`Binaries/Win64/Slop yCam/installation-manifest.json`; README "Slop yCam Beta 8.10.5"). Vortex archives beta8.5 .. beta8.10.5
in `%APPDATA%\Vortex\downloads\stalker2heartofchornobyl\`. Add-on "Inspect 3" (`inspect-addon.3`) also installed.

Game folder `.../Stalker2/Binaries/Win64/`:
- `Slop_yCam.asi` (loaded by Ultimate ASI Loader as `dsound.dll`; `Slop_yCam_Loader.log`)
- `Slop yCam Studio.exe` (config GUI; profiles in `%LOCALAPPDATA%\Slop yCam Studio\`, `active.ini`)
- `Slop yCam/Slop_yCam_Standalone.dll` (native runtime + own private Lua state; NOT UE4SS)
- `Slop yCam/Addons/Slop_yCam_Inspect.dll`, `inspect-addon.json`
- `Slop yCam/Scripts/*.lua`: bootstrap, runtime (565 KB, 7724 lines), config, settings (schema/ranges), preferences,
  freelook-keys, equipment, motion, offhand, placement, throwable, laser, laser-compat, mcm*, inspect, inspect-hands
- `Slop yCam/Scripts/profile.ini` (live profile, = Studio active.ini), `mcm-profile.ini`, state files
  (`studio-state.txt`, `status.txt`, `hook-diagnostics.txt`, `items.txt`, `weapons.txt` ...)
- `Slop yCam/Slop_yCam_Standalone.log` (runtime log)
- `ue4ss/Mods/Slop yCam/` = stale leftovers from Sep 18 (old UE4SS build); disabled in `ue4ss/Mods/mods.txt` ("Slop yCam : 0").

NO pak/utoc/ucas. README: "No replacement player, weapon Animation Blueprint, Control Rig or asset container is
included"; CHANGELOG: "fully native and asset-free: no UE4SS requirement, no replacement Blueprints, Animation
Blueprints, Control Rigs or PAK/UTOC/UCAS files". scan_mods.py: BP_Stalker2Character only in ImmersiveDialogue 2.0.0
(`zzz_ImmersiveDialogue_20_P`); `ChestCamLag` (old yCam pak component) in no pak. Stalker2.log: no yCam mounts.
=> harness/docs/compatibility.md entry for Slop yCam is OUTDATED (describes the pre-asset-free version).

## 2. What it does (V from Lua)
- Camera: `native_camera.ensure` (runtime.lua ~4110) adds a runtime `SpringArmComponent` to the pawn, attached to mesh
  socket `jnt_camera`, and re-parents the pawn's `CameraComponent` to its `SpringEndpoint`; rotation lag on
  (camera inertia / bodycam trail). Refuses to bind if the camera's parent is not the pawn mesh ("Do not seize a camera
  belonging to a scripted view or another mod"); then camera='waiting' and the whole tick returns (all effects off).
  Release re-attaches the camera to its original parent/socket and destroys the arm.
- Free Look (runtime.lua 1358-1655): hold (default) or toggle; user's key ThumbMouseButton, hold, sensitivity 500,
  return 25, torso follow 100 (`freelook_body`). On press: if `pc:IsLookInputIgnored()` or another FreeLook mod
  (`/FreeLook/BP_FreeLook`) is active -> blocked; else `pc:SetIgnoreLookInput(true)`, reads `GetInputMouseDelta` and
  right stick, yaw +-75, pitch +-40 (gaze +-90/+-60 with head tracking), applied as relative rotation on its spring arm
  (not ControlRotation). Release: `SetIgnoreLookInput(false)`, view eases back. Cancelled by: aim alpha > 0.05,
  `pc.bShowMouseCursor`, game paused, Escape or Tab held. Shoulder clearance 25 deg from `jnt_l_arm`/`jnt_r_arm`.
  Torso follow: native `SlopSetNativeTorso` (upper-spine turn, via hooked ModifyBone nodes).
- Weapon inertia/sway, bodycam weight, weapon lowering (key LeftControl in profile.ini), hip-fire along the barrel,
  aim dot (moves `W_Crosshair_C` render translation), laser, detector inertia (writes DetectorData.InertiaData),
  held-item arms (`SlopSetNativeArms`: right arm for throwables/items, left arm only when
  `DetectorData.bHasDetectorInHands`), near clip `r.SetNearClipPlane 0.1` (console command), viewmodel/aim FOV
  (`SlopSetViewFov`, FovMPC reads), head/eye tracking (add-on, not installed), Realistic body (off; would write
  ControlRotation).
- States: `pawn:IsUsingPDA()` -> full stop() of every effect (camera handed back, free look released, torso/arms
  cleared, FOV released) and nothing runs until it ends; re-init with age 2.5 s afterwards. Mod switch off -> same.
  `pc.bShowMouseCursor` (menus/inventory) -> free look cancelled, lowering suspended, held arms rest, momentum reset,
  tracking keys ignored; camera effects continue. `IsGamePaused` -> free look cancel, effects frozen.
  `IsInStaticDialog` / `IsInCinematic` polled 5x/s only for tracking add-ons / Realistic body. Lowering busy list:
  IsReloading, IsWeaponReloading, ShouldReload, IsUsingPDA, IsUsingBackpack, IsInteractionInProgress, IsVaulting,
  IsClimbing, IsInCinematic, IsInStaticDialog, IsSprinting.
- Native DLL (strings, hook-diagnostics.txt): hooks two game tick vtable slots (runs Lua every frame), an aim function
  by signature, AnimNode_ModifyBone evaluation (torso / arms / inertia), CameraComponent view (GetCameraView: FOV and
  view re-timing). (I: exact targets from strings only.)
- Equipment class from `anim.WeaponData.WeaponMesh` anim instance `.WeaponAnimCollection` (equipment.lua lists "pda"
  among items). items.txt never saw a PDA collection (consistent with suspension during PDA).

## 3. Overrides
None (V). Runtime-only changes: added SpringArm + camera re-parent, ModifyBone node outputs, weapon swing/inertia
properties on AnimInstance/AnimCollection, DetectorData inertia, crosshair widget translation, near clip CVar, FOV.

## 5. Implications for ImmersivePDA
- Pawn override is no longer a yCam conflict (it ships none). The pawn conflict on this PC is ImmersiveDialogue 2.0.0.
- Path A, the game's PDA state kept on (IsUsingPDA true): yCam goes fully dormant. There's no conflict, but there's also no yCam free
  look, bodycam or inertia while the PDA is up. Free look has to be ours. On entry yCam snaps its view back (a held free look ends
  at once). When IsUsingPDA ends, yCam re-binds.
- Path B, our own raised-PDA state (IsUsingPDA false): yCam runs fully. Its free look (ThumbMouseButton hold) would work
  only while `bShowMouseCursor` is false, aim alpha is about 0, the game isn't paused, and Esc/Tab aren't held. If the PDA screen
  needs a mouse cursor, yCam free look cancels. If we call SetIgnoreLookInput(true) before the press, yCam's free look is
  blocked. It's a counter, so keep our calls balanced. Don't move the camera through its relative transform or
  re-parent it: yCam owns the camera's parent (its SpringArm) and rewrites the arm's rotation every tick. If our mod re-parents the camera, yCam's
  check `camera parent == mesh` fails and yCam stops all its effects. Rotate the view through ControlRotation (normal look) or
  leave free look to yCam.
- Don't touch: the CameraComponent parent and relative transform, `ChestCamLag`, IgnoreLookInput left unbalanced, ModifyBone
  nodes / the torso chain of AnimBP_Player, DetectorData.bHasDetectorInHands (it turns the left arm natively),
  W_Crosshair_C render translation, r.SetNearClipPlane.

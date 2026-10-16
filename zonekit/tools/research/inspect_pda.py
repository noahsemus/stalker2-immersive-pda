"""READ-ONLY inspection of vanilla PDA assets (no saves, no edits). Output: OUTFILE."""
import json
import unreal

OUT = r"C:/Users/noahs/AppData/Local/Temp/claude/c--Users-noahs-OneDrive-Documents-GitHub-stalker2-immersive-looting/dd18b75b-f907-463a-93bb-51f7a7e1a9c3/scratchpad/pda_research/headless_out.txt"
lines = []


def P(*a):
    lines.append(" ".join(str(x) for x in a))


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))


def safe(f, default="<err>"):
    try:
        return f()
    except Exception as e:  # noqa
        return f"{default}:{e}"


def props(o, skip=()):
    """All readable editor properties of an object (by dir())."""
    d = {}
    for a in dir(o):
        if a.startswith("_") or a in skip:
            continue
        try:
            v = o.get_editor_property(a)
        except Exception:
            continue
        d[a] = v
    return d


def enum_vals(name):
    E = getattr(unreal, name, None)
    if E is None:
        return "<no enum>"
    out = []
    for x in dir(E):
        if x.isupper():
            try:
                out.append(f"{x}={int(getattr(E, x).value)}")
            except Exception:
                out.append(x)
    return out


AL = unreal.AnimationLibrary
AR = unreal.AssetRegistryHelpers.get_asset_registry()

# ---------------- enums
P("#### ENUMS")
for en in ("PDAPageType", "HandItem", "SyncAnimationType", "CloseType", "ActionType", "MappingContext",
           "InputMappingContextPriority", "WidgetNameEx", "PlayerTriggerState", "ItemInHandType", "AttachItemType",
           "InteractionSystemNotificationsType", "HideViewType", "StateTag"):
    P(en, enum_vals(en))
flush()

# ---------------- anim assets
P("\n#### ANIM")
ANIMS = [
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda_fast",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda_EMP_a",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_equip",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_equip_fast",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_idle",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_interrupt",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_unequip",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_unequip_fast",
    "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_EMP_a",
    "/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/MG_pda_fp",
    "/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/MG_pda_fp_fast",
    "/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/AS_pda_fp_idle",
]
mont_dir_done = False
for path in ANIMS:
    a = unreal.load_asset(path)
    if not a:
        P("LOAD FAIL", path); continue
    P(f"\n== {path.rsplit('/', 1)[1]} ({a.get_class().get_name()}) len={safe(lambda: round(a.get_play_length(), 4))}")
    if isinstance(a, unreal.AnimMontage):
        if not mont_dir_done:
            P("AnimMontage dir:", [x for x in dir(a) if not x.startswith("_")])
            mont_dir_done = True
        for nm in ("composite_sections", "slot_anim_tracks", "blend_in", "blend_out", "blend_out_trigger_time",
                   "enable_auto_blend_out", "b_enable_auto_blend_out", "sync_group", "sync_slot_index"):
            v = safe(lambda: a.get_editor_property(nm))
            if isinstance(v, str) and v.startswith("<err>"):
                continue
            P(" ", nm, "=", v)
        try:
            for s in a.get_editor_property("composite_sections"):
                P("   section", safe(lambda: s.get_editor_property("section_name")),
                  "next", safe(lambda: s.get_editor_property("next_section_name")),
                  "link", safe(lambda: s.get_editor_property("link_value")),
                  "seq", safe(lambda: s.get_editor_property("linked_sequence")))
        except Exception as e:
            P("  sections err", e)
        try:
            for t in a.get_editor_property("slot_anim_tracks"):
                P("   slot", t.get_editor_property("slot_name"))
                for seg in t.get_editor_property("anim_track").get_editor_property("anim_segments"):
                    P("     seg", safe(lambda: seg.get_editor_property("anim_reference").get_name()),
                      "start", safe(lambda: seg.get_editor_property("start_pos")),
                      "a0", safe(lambda: seg.get_editor_property("anim_start_time")),
                      "a1", safe(lambda: seg.get_editor_property("anim_end_time")),
                      "rate", safe(lambda: seg.get_editor_property("anim_play_rate")),
                      "loop", safe(lambda: seg.get_editor_property("looping_count")))
        except Exception as e:
            P("  slots err", e)
        for fn in ("get_num_sections", "get_section_name"):
            pass
        try:
            n = a.get_num_sections()
            P("  num_sections", n, [str(a.get_section_name(i)) for i in range(n)])
        except Exception as e:
            P("  num_sections err", e)
    else:
        P("  frames", safe(lambda: AL.get_num_frames(a)), "rate", safe(lambda: AL.get_frame_rate(a)),
          "additive", safe(lambda: a.get_editor_property("additive_anim_type")))
        P("  curves", safe(lambda: [str(c) for c in AL.get_animation_curve_names(a, unreal.RawCurveType.FLOAT_CURVE)]))
    try:
        evs = AL.get_animation_notify_events(a)
    except Exception as e:
        evs = []; P("  notify err", e)
    for e in evs:
        n = safe(lambda: e.get_editor_property("notify"))
        ns = safe(lambda: e.get_editor_property("notify_state_class"))
        obj = n if n and not isinstance(n, str) else (ns if ns and not isinstance(ns, str) else None)
        t = safe(lambda: AL.get_anim_notify_event_trigger_time(e))
        du = safe(lambda: AL.get_anim_notify_event_duration(e))
        nm = safe(lambda: e.get_editor_property("notify_name"))
        detail = {}
        if obj is not None:
            for k, v in props(obj).items():
                if k in ("notify_color",):
                    continue
                detail[k] = str(v)[:120]
        P(f"  notify t={t} dur={du} name={nm} cls={obj.get_class().get_name() if obj else None} {detail}")
    flush()

# camera / item bones over the sequences (component space, rel. to jnt_camera)


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qrot(a, p):
    r = qmul(qmul(a, (p[0], p[1], p[2], 0.0)), (-a[0], -a[1], -a[2], a[3]))
    return (r[0], r[1], r[2])


def cs(seq, bone, frame):
    path = [str(b) for b in AL.find_bone_path_to_root(seq, bone)]
    q, p = (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0)
    for b in reversed(path):
        t = AL.get_bone_pose_for_frame(seq, b, frame, False)
        lq = (t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w)
        lp = (t.translation.x, t.translation.y, t.translation.z)
        rp = qrot(q, lp)
        p = (p[0] + rp[0], p[1] + rp[1], p[2] + rp[2])
        q = qmul(q, lq)
    return p, q


P("\n#### BONES (component space; item/hands relative to jnt_camera)")
for path in ANIMS[3:10]:
    seq = unreal.load_asset(path)
    if not isinstance(seq, unreal.AnimSequence):
        continue
    try:
        n = AL.get_num_frames(seq)
        P(f"== {path.rsplit('/', 1)[1]} frames={n}")
        for b in ("jnt_item", "jnt_camera"):
            P("  path", b, safe(lambda: [str(x) for x in AL.find_bone_path_to_root(seq, b)]))
        step = max(1, n // 12)
        for f in list(range(0, n, step)) + [n - 1]:
            cam, cq = cs(seq, "jnt_camera", f)
            fwd = qrot(cq, (1.0, 0.0, 0.0)); up = qrot(cq, (0.0, 0.0, 1.0))
            row = [f"f{f:03d} cam=({cam[0]:.1f},{cam[1]:.1f},{cam[2]:.1f}) camF=({fwd[0]:.2f},{fwd[1]:.2f},{fwd[2]:.2f}) camU=({up[0]:.2f},{up[1]:.2f},{up[2]:.2f})"]
            for b in ("jnt_item", "jnt_l_hand", "jnt_r_hand"):
                try:
                    p, _ = cs(seq, b, f)
                    row.append(f"{b[4:]}=({p[0]-cam[0]:.1f},{p[1]-cam[1]:.1f},{p[2]-cam[2]:.1f})")
                except Exception as e:
                    row.append(f"{b}:err")
            P("  " + " ".join(row))
    except Exception as e:
        P("  bones err", e)
    flush()

# ---------------- anim collection, AnimBP_PDA
P("\n#### ANIM COLLECTION")
ac = unreal.load_asset("/Game/_STALKER2/Animations/Weapons/items/pda/AnimCollections/AnimCollection_fp_pda")
if ac:
    P("class", ac.get_class().get_name())
    for k, v in props(ac).items():
        P(" ", k, "=", str(v)[:1500])
abp = unreal.load_asset("/Game/_STALKER2/Animations/Weapons/items/pda/AnimBP_PDA")
if abp:
    P("AnimBP_PDA parent", safe(lambda: abp.get_editor_property("parent_class")))
flush()

# ---------------- input
P("\n#### INPUT ACTIONS")
IAS = ["IA_OpenPDA", "IA_UI_PDA_Close", "IA_UI_PDA_TransitionBack", "IA_UI_PDA_TransitionForward",
       "IA_UI_PDA_TransitionRelease", "IA_UI_PDA_MoveToNextSlot", "IA_UI_PDA_MoveToPreviousSlot"]
for ia in IAS:
    o = unreal.load_asset(f"/Game/_Stalker_2/data/input/InputActions/{ia}")
    if not o:
        P("LOAD FAIL", ia); continue
    d = props(o)
    P(ia, {k: str(v)[:200] for k, v in d.items()})


def desc(o):
    if o is None:
        return None
    d = {"class": o.get_class().get_name()}
    for prop in ("hold_time_threshold", "is_one_shot", "tap_release_time_threshold", "actuation_threshold",
                 "lower_threshold", "upper_threshold", "scalar", "order", "type"):
        try:
            d[prop] = str(o.get_editor_property(prop))
        except Exception:
            pass
    return d


P("\n#### IMCs")
IMCS = ["IMC_Exploration", "IMC_PDA_Map", "IMC_PDA_Journal", "IMC_PDA_Note", "IMC_Stats", "IMC_PDA_Tutorial",
        "IMC_PDA_Encyclopedia", "IMC_PDA_Upgrades", "IMC_Interactivity", "IMC_Inventory"]
for name in IMCS:
    imc = unreal.load_asset(f"/Game/_Stalker_2/data/input/InputMappingContexts/{name}")
    if not imc:
        P("LOAD FAIL", name); continue
    P(f"== {name}")
    for m in imc.get_editor_property("mappings"):
        act = m.get_editor_property("action")
        an = act.get_name() if act else None
        if name in ("IMC_Exploration", "IMC_Interactivity", "IMC_Inventory") and not any(
                s in (an or "") for s in ("PDA", "Map", "Journal", "Look", "Note", "Inventory", "Escape", "Menu", "Pause")):
            continue
        try:
            mp = m.get_editor_property("player_mappable_key_settings")
            mpn = str(mp.get_editor_property("name")) if mp else None
        except Exception:
            mpn = None
        P(f"  {an:45s} key={m.get_editor_property('key').get_editor_property('key_name')} map={mpn} "
          f"trig={[desc(x) for x in m.get_editor_property('triggers')]} mods={[desc(x)['class'] for x in m.get_editor_property('modifiers')]}"
          f" actTrig={[desc(x) for x in act.get_editor_property('triggers')] if act else None}")
    flush()

# ---------------- referencers
P("\n#### REFERENCERS")
opt = unreal.AssetRegistryDependencyOptions()
for pkg in ["/Game/_Stalker_2/data/input/InputActions/IA_OpenPDA",
            "/Game/_Stalker_2/data/input/InputActions/IA_UI_PDA_Close",
            "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDABookView",
            "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda",
            "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda_fast",
            "/Game/_STALKER2/Animations/Weapons/items/pda/AnimCollections/AnimCollection_fp_pda",
            "/Game/_STALKER2/SkeletalMeshes/weapons/items/pda/SK_pda",
            "/Game/_Stalker_2/items/device/SM_dev_pda/Materials/MI_PDA_Screen",
            "/Game/_Stalker_2/items/device/SM_dev_pda/Materials/M_PDA_Screen",
            "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_MapPage",
            "/Game/GameLite/FPS_Game/UIRemaster/PDA/WorldMap/W_WorldMap",
            "/Game/GameLite/FPS_Game/UIRemaster/Materials/Map/RT_WorldMap",
            "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDANoise"]:
    P(pkg.rsplit("/", 1)[1], "<-", safe(lambda: [str(x) for x in AR.get_referencers(pkg, opt)]))
    P("    ->", safe(lambda: [str(x) for x in AR.get_dependencies(pkg, opt)]))
flush()

# ---------------- widgets
P("\n#### WIDGETS")


def widget_cdo(path):
    bp = unreal.load_asset(path)
    if not bp:
        return None, None
    cls = safe(lambda: bp.generated_class())
    if isinstance(cls, str):
        cls = unreal.load_object(None, path + "." + path.rsplit("/", 1)[1] + "_C")
    return bp, unreal.get_default_object(cls)


for wp in ["/Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDABookView",
           "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_MapPage",
           "/Game/GameLite/FPS_Game/UIRemaster/PDA/WorldMap/W_WorldMap",
           "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_JournalPage",
           "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_NotesPage"]:
    bp, cdo = widget_cdo(wp)
    P(f"\n== {wp.rsplit('/', 1)[1]} parent={safe(lambda: bp.get_editor_property('parent_class'))}")
    if cdo is None:
        P("  no cdo"); continue
    skip = {"slot", "navigation", "render_transform"}
    for k, v in props(cdo).items():
        if k in skip:
            continue
        s = str(v)
        if k == "view_open_settings":
            vs = props(v)
            P("  view_open_settings:", {a: str(b) for a, b in vs.items()})
            continue
        P("  ", k, "=", s[:300])
    flush()

# widget tree of W_PDABookView (objects under the blueprint / generated class)
for wp in ["/Game/GameLite/FPS_Game/UIRemaster/PDA/W_PDABookView", "/Game/GameLite/FPS_Game/UIRemaster/PDA/W_MapPage",
           "/Game/GameLite/FPS_Game/UIRemaster/PDA/WorldMap/W_WorldMap"]:
    bp = unreal.load_asset(wp)
    P(f"\n== widget tree {wp.rsplit('/', 1)[1]}")
    seen = 0
    try:
        for w in unreal.ObjectIterator(unreal.Widget):
            pn = w.get_path_name()
            if not pn.startswith(wp + ".") or "WidgetTree" not in pn:
                continue
            seen += 1
            extra = ""
            if isinstance(w, unreal.Image):
                br = safe(lambda: w.get_editor_property("brush"))
                extra = f" res={safe(lambda: br.get_editor_property('resource_object'))} tint={safe(lambda: br.get_editor_property('tint_color'))} color={safe(lambda: w.get_editor_property('color_and_opacity'))}"
            if isinstance(w, unreal.BackgroundBlur):
                extra = f" BLUR strength={safe(lambda: w.get_editor_property('blur_strength'))}"
            if isinstance(w, unreal.Border):
                extra = f" brushColor={safe(lambda: w.get_editor_property('brush_color'))}"
            P(f"  {pn.split('WidgetTree', 1)[1]} [{w.get_class().get_name()}] vis={safe(lambda: w.get_editor_property('visibility'))} op={safe(lambda: w.get_editor_property('render_opacity'))}{extra}")
    except Exception as e:
        P("  iter err", e)
    P("  widgets seen", seen)
    flush()

# ---------------- materials / meshes
P("\n#### MATERIALS / MESHES")
MEL = unreal.MaterialEditingLibrary
for mp in ["/Game/_Stalker_2/items/device/SM_dev_pda/Materials/M_PDA_Screen",
           "/Game/_Stalker_2/items/device/SM_dev_pda/Materials/MI_PDA_Screen",
           "/Game/_Stalker_2/items/device/SM_dev_pda/Materials/MI_dev_pda_map",
           "/Game/_Stalker_2/items/device/SM_dev_pda/Materials/MI_dev_pda",
           "/Game/_STALKER2/SkeletalMeshes/weapons/items/pda/Materials/MI_PDA",
           "/Game/GameLite/FPS_Game/UIRemaster/Materials/Map/M_WorldMapSceneMaterial"]:
    m = unreal.load_asset(mp)
    if not m:
        P("LOAD FAIL", mp); continue
    P(f"== {mp.rsplit('/', 1)[1]} ({m.get_class().get_name()})")
    if isinstance(m, unreal.MaterialInstance):
        P("  parent", safe(lambda: m.get_editor_property("parent")))
        P("  scalars", safe(lambda: [(str(p.parameter_info.name), p.parameter_value) for p in m.get_editor_property("scalar_parameter_values")]))
        P("  vectors", safe(lambda: [(str(p.parameter_info.name), str(p.parameter_value)) for p in m.get_editor_property("vector_parameter_values")]))
        P("  textures", safe(lambda: [(str(p.parameter_info.name), str(p.parameter_value)) for p in m.get_editor_property("texture_parameter_values")]))
    P("  scalar names", safe(lambda: [str(x) for x in MEL.get_scalar_parameter_names(m)]))
    P("  vector names", safe(lambda: [str(x) for x in MEL.get_vector_parameter_names(m)]))
    P("  texture names", safe(lambda: [str(x) for x in MEL.get_texture_parameter_names(m)]))
    P("  switch names", safe(lambda: [str(x) for x in MEL.get_static_switch_parameter_names(m)]))
    if isinstance(m, unreal.Material):
        P("  domain", safe(lambda: m.get_editor_property("material_domain")), "blend", safe(lambda: m.get_editor_property("blend_mode")),
          "shading", safe(lambda: m.get_editor_property("shading_model")))
        P("  used textures", safe(lambda: [t.get_path_name() for t in MEL.get_used_textures(m)]))
flush()

for sp in ["/Game/_STALKER2/SkeletalMeshes/weapons/items/pda/SK_pda", "/Game/_STALKER2/SkeletalMeshes/item/pda/tp/SK_pda_tp"]:
    sk = unreal.load_asset(sp)
    if not sk:
        P("LOAD FAIL", sp); continue
    P(f"== {sp.rsplit('/', 1)[1]}")
    P("  materials", safe(lambda: [(str(x.get_editor_property('material_slot_name')), str(x.get_editor_property('material_interface').get_path_name() if x.get_editor_property('material_interface') else None)) for x in sk.get_editor_property("materials")]))
    P("  sockets", safe(lambda: [(str(s.get_editor_property('socket_name')), str(s.get_editor_property('bone_name'))) for s in sk.get_editor_property('sockets')]))
    P("  bounds", safe(lambda: sk.get_bounds()))
    ref = safe(lambda: sk.get_editor_property("skeleton"))
    P("  skeleton", ref)
    try:
        sm = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    except Exception:
        sm = None
    P("  bones", safe(lambda: [str(sk.skeleton.get_reference_pose().get_bone_names()[i]) for i in range(5)] if False else ""))

rt = unreal.load_asset("/Game/GameLite/FPS_Game/UIRemaster/Materials/Map/RT_WorldMap")
if rt:
    P("RT_WorldMap", safe(lambda: (rt.get_editor_property("size_x"), rt.get_editor_property("size_y"), str(rt.get_editor_property("render_target_format")))))

# ---------------- PC / player class surface related to PDA
P("\n#### CLASS SURFACE")
for cn in ("PC", "PDAView", "PDAOpenIPU", "UIManagerEx", "CppMediator", "ViewBase", "BookViewBase", "WorldMapPage", "PDAPage",
           "AnimInstanceItem", "AnimInstancePlayer", "PlayerControllerStalker", "Stalker2PlayerController", "GSCPlayerController"):
    c = getattr(unreal, cn, None)
    if c is None:
        P(cn, "<none>"); continue
    P(cn, [x for x in dir(c) if any(s in x.lower() for s in ("pda", "pause", "fov", "look", "input", "view", "cursor", "map", "ui", "time"))][:80])
flush()
P("\nDONE")
flush()
print("[harness] inspect_pda done")

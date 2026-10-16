"""READ-ONLY second pass (no saves, no edits)."""
import unreal

OUT = r"C:/Users/noahs/AppData/Local/Temp/claude/c--Users-noahs-OneDrive-Documents-GitHub-stalker2-immersive-looting/dd18b75b-f907-463a-93bb-51f7a7e1a9c3/scratchpad/pda_research/headless_out2.txt"
L = []


def P(*a):
    L.append(" ".join(str(x) for x in a))
    open(OUT, "w", encoding="utf-8").write("\n".join(L))


def safe(f):
    try:
        return f()
    except Exception as e:
        return f"<err:{e}>"


def props(o):
    d = {}
    for a in dir(o):
        if a.startswith("_"):
            continue
        try:
            d[a] = o.get_editor_property(a)
        except Exception:
            pass
    return d


AL = unreal.AnimationLibrary


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


P("#### hand item data struct")
for sn in ("AnimHandItemData", "AnimPlayerCameraData", "AnimPlayerStateData"):
    s = getattr(unreal, sn, None)
    P(sn, [x for x in dir(s) if not x.startswith("_")] if s else "<none>")

P("\n#### anim collection direct props")
ac = unreal.load_asset("/Game/_STALKER2/Animations/Weapons/items/pda/AnimCollections/AnimCollection_fp_pda")
for n in ("use_item_animation", "use_item_fast_animation", "weapon_animations", "player_weapon_animations",
          "character_weapon_animations", "equip_weapon", "player_anim_blueprint", "use_item_emp_animation"):
    P(n, safe(lambda: ac.get_editor_property(n)))
P("dir", [x for x in dir(ac) if not x.startswith("_")])

P("\n#### device anim bones (SKEL_pda), component space")
for path in ["/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/AS_pda_fp_idle",
             "/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/AS_pda_fp_equip",
             "/Game/_STALKER2/Animations/Weapons/items/pda/AnimSequences/fp/AS_pda_fp_EMP_a"]:
    seq = unreal.load_asset(path)
    if not seq:
        P("LOAD FAIL", path); continue
    n = AL.get_num_frames(seq)
    P(f"== {path.rsplit('/', 1)[1]} frames={n} len={seq.get_play_length():.3f}")
    names = safe(lambda: [str(x) for x in AL.get_bone_names(seq)] if hasattr(AL, "get_bone_names") else "")
    P("  bones?", names)
    for b in ("jnt_pda_fp", "jnt_offset", "jnt_l_hand", "jnt_r_hand"):
        P("  path", b, safe(lambda: [str(x) for x in AL.find_bone_path_to_root(seq, b)]))
    step = max(1, n // 8)
    for f in list(range(0, n, step)) + [n - 1]:
        row = [f"f{f:03d}"]
        for b in ("jnt_pda_fp", "jnt_offset", "jnt_l_hand", "jnt_r_hand"):
            try:
                p, q = cs(seq, b, f)
                fx = qrot(q, (1, 0, 0)); fz = qrot(q, (0, 0, 1))
                row.append(f"{b[4:]}=({p[0]:.1f},{p[1]:.1f},{p[2]:.1f}) X=({fx[0]:.2f},{fx[1]:.2f},{fx[2]:.2f}) Z=({fz[0]:.2f},{fz[1]:.2f},{fz[2]:.2f})")
            except Exception as e:
                row.append(f"{b}:err {e}")
        P("  " + " ".join(row))

P("\n#### player hands in player idle, component space (root frame), for comparison")
seq = unreal.load_asset("/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/AS_fp_pda_idle")
for b in ("jnt_l_hand", "jnt_r_hand", "jnt_camera", "jnt_item", "jnt_l_weapon", "jnt_r_weapon"):
    try:
        p, q = cs(seq, b, 0)
        P(b, f"({p[0]:.1f},{p[1]:.1f},{p[2]:.1f})", "path", [str(x) for x in AL.find_bone_path_to_root(seq, b)])
    except Exception as e:
        P(b, "err", e)

P("\n#### views")


def cdo_of(path):
    cls = unreal.load_object(None, path + "." + path.rsplit("/", 1)[1] + "_C")
    return unreal.get_default_object(cls) if cls else None


for wp in ["/Game/GameLite/FPS_Game/UIRemaster/View/W_BackgroundBlurView",
           "/Game/GameLite/FPS_Game/UIRemaster/Inventory/W_Inventory",
           "/Game/GameLite/FPS_Game/UIRemaster/View/MenuMainView/W_PauseMenuMainView",
           "/Game/GameLite/FPS_Game/UIRemaster/HUD/W_GameHUD",
           "/Game/GameLite/FPS_Game/UIRemaster/View/Binoculars/W_BinocularsView"]:
    unreal.load_asset(wp)
    c = safe(lambda: cdo_of(wp))
    if c is None or isinstance(c, str):
        P(wp, "no cdo", c); continue
    vs = safe(lambda: c.get_editor_property("view_open_settings"))
    P(f"== {wp.rsplit('/', 1)[1]} class={c.get_class().get_name()} parent={c.get_class().get_super_class().get_name() if hasattr(c.get_class(), 'get_super_class') else '?'}")
    P("  widget_name", safe(lambda: c.get_editor_property("widget_name")))
    if not isinstance(vs, str):
        P("  view_open_settings", {a: str(b) for a, b in props(vs).items()})
    for w in unreal.ObjectIterator(unreal.BackgroundBlur):
        if w.get_path_name().startswith(wp + "."):
            P("  BackgroundBlur", w.get_path_name().split("WidgetTree", 1)[-1], "strength", safe(lambda: w.get_editor_property("blur_strength")),
              "vis", safe(lambda: w.get_editor_property("visibility")))

P("\n#### W_PDABookView instance anims")
for w in unreal.ObjectIterator(unreal.WidgetAnimation):
    pn = w.get_path_name()
    if "W_PDABookView" in pn or "W_MapPage" in pn:
        P(pn, "len", safe(lambda: w.get_end_time() - w.get_start_time()))

P("\n#### montage section times via sequence play length")
for path in ["/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda",
             "/Game/_STALKER2/Animations/Player/AnimSequences/Items/pda/MG_fp_pda_fast"]:
    m = unreal.load_asset(path)
    for nm in ("CompositeSections", "SlotAnimTracks", "composite_sections"):
        P(nm, safe(lambda: m.get_editor_property(nm)))
    P("blend in", safe(lambda: m.get_default_blend_in_time()), "out", safe(lambda: m.get_default_blend_out_time()))
    P("first ref", safe(lambda: m.get_first_anim_reference()))
    P("group", safe(lambda: m.get_group_name()))
P("DONE")
print("[harness] inspect_pda2 done")

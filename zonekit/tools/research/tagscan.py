import sys, struct
src = open(sys.argv[1]).read().split("\nfor p in sys.argv[1:]:")[0]
ns = {}; exec(src, ns)
data = open(sys.argv[2], "rb").read()
names = ns["name_table"](data)
idx = {n: i for i, n in enumerate(names)}
want = sys.argv[3].split(",")
fp = idx.get("FloatProperty"); np_ = idx.get("NameProperty"); dp = idx.get("DoubleProperty"); op = idx.get("ObjectProperty"); ip = idx.get("IntProperty")
out = []
for w in want:
    if w not in idx: continue
    key = struct.pack("<ii", idx[w], 0)
    o = 0
    while True:
        o = data.find(key, o)
        if o < 0: break
        t, tn = struct.unpack_from("<ii", data, o + 8)
        if t in (fp, np_, op, ip, dp):
            inner = struct.unpack_from("<i", data, o + 16)[0]
            size = struct.unpack_from("<i", data, o + 20)[0]
            flags = data[o + 24]
            v = o + 25
            if t == fp: val = struct.unpack_from("<f", data, v)[0]
            elif t == dp: val = struct.unpack_from("<d", data, v)[0]
            elif t == ip: val = struct.unpack_from("<i", data, v)[0]
            elif t == np_:
                a, b = struct.unpack_from("<ii", data, v); val = names[a] if 0 <= a < len(names) else a
            else:
                val = struct.unpack_from("<i", data, v)[0]
            out.append((o, w, names[t], size, flags, val))
        o += 1
for r in sorted(out): print(r)

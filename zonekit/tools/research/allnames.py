import sys, importlib.util
spec = importlib.util.spec_from_file_location("dn", sys.argv[1]); dn = importlib.util.module_from_spec(spec)
src = open(sys.argv[1]).read().split("\nfor p in sys.argv[1:]:")[0]
exec(src, dn.__dict__)
for p in sys.argv[2:]:
    data = open(p, "rb").read()
    names = dn.name_table(data)
    print("===", p, "names" if names else "BYTESCAN")
    if names is None:
        import re
        names = [m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{4,}', data)]
    for n in names: print(n)

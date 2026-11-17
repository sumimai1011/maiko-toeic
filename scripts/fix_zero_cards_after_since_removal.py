#!/usr/bin/env python3
"""Remove obsolete initialization of deleted since card, leaving 360 unchanged."""
import json, re, subprocess
from pathlib import Path
path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
p=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[p:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(197,163), (len(base),len(extra))
ids={c["id"] for c in base+extra}
assert "s361" not in ids and {"s167","s204"}.issubset(ids)
lines=src.splitlines(keepends=True)
idxs=[i for i,line in enumerate(lines) if line.startswith('Object.assign(BASE.find(x=>x.id==="s361"),')]
assert len(idxs)==1, idxs
lines[idxs[0]]="// Removed obsolete since/s361 startup override.\n"
src="".join(lines)
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert set(startup_ids)=={"s167","s204"},startup_ids
assert "preserveMergedCardProgress" in src
assert src.rstrip().endswith("</html>")
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(scripts)==1,len(scripts)
js=Path("/tmp/toeic_startup.js")
js.write_text(scripts[0],encoding="utf-8")
res=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
assert res.returncode==0,res.stderr
path.write_text(src,encoding="utf-8")
print("Removed stale since startup crash; JS syntax validated.")
print("Verified 360 cards (197 base + 163 extra), with other card/image/progress data intact.")

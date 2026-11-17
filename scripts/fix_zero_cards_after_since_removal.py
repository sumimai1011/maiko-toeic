#!/usr/bin/env python3
"""Fix 0-card startup error referencing since/s361 after its authorized removal."""
from pathlib import Path
import json
import re
import subprocess

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
p=src.index("const BASE=")+len("const BASE=")
base,consumed=json.JSONDecoder().raw_decode(src[p:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(197,163), (len(base),len(extra))
ids={c["id"] for c in base+extra}
assert "s361" not in ids and "s167" in ids and "s204" in ids

# The deleted since card must not be accessed by the startup overrides.
lines=src.splitlines(keepends=True)
matches=[i for i,line in enumerate(lines) if line.startswith('Object.assign(BASE.find(x=>x.id==="s361"),')]
assert len(matches)==1, matches
lines[matches[0]]="// Deleted s361 has no startup override.\n"
src="".join(lines)
startup_ids=re.findall(r'Object\\.assign\\(BASE\\.find\\(x=>x\\.id==="([^"]+)"\\)',src)
assert set(startup_ids)=={"s167","s204"}, startup_ids
assert all(x in ids for x in startup_ids)
assert "preserveMergedCardProgress" in src
assert src.rstrip().endswith("</html>")

scripts=re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(scripts)==1, len(scripts)
js=Path("/tmp/toeic_repair_check.js")
js.write_text(scripts[0],encoding="utf-8")
res=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
assert res.returncode==0,res.stderr
path.write_text(src,encoding="utf-8")
print("Fixed stale since/s361 startup override. JavaScript syntax PASSED.")
print("Card total: 197 + 163 = 360. Other cards/images/progress preserved.")

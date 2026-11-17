#!/usr/bin/env python3
"""Fix blank 0-card screen caused by stale since/s361 startup override."""
from pathlib import Path
import json,re,subprocess
path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1
p=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[p:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert len(base)==197 and len(extra)==163 and len(base)+len(extra)==360
ids={c["id"] for c in base+extra}
assert "s361" not in ids, "since must remain deleted"
assert "s167" in ids and "s204" in ids
src,count=re.subn(r'^Object\.assign\(BASE\.find\(x=>x\.id==="s361"\),\{.*\}\);
# Catch any other deleted-card startup overrides, not just since.
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert all(x in ids for x in startup_ids), ("Stale overrides left",startup_ids)
assert len(startup_ids)==2 and set(startup_ids)=={"s167","s204"}
assert src.count('id="exportCards"')==0 and "cardEditLayer" not in src
assert src.rstrip().endswith("</html>")
# Syntax check the actual inline script before writing.
matches=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(matches)==1
jsfile=Path("/tmp/toeic_after_repair.js")
jsfile.write_text(matches[0],encoding="utf-8")
r=subprocess.run(["node","--check",str(jsfile)],capture_output=True,text=True)
assert r.returncode==0, r.stderr[-2500:]
path.write_text(src,encoding="utf-8")
print("Repaired stale s361 startup override; JavaScript syntax validation PASSED")
print("Validated 197 + 163 = 360 cards, all remaining overrides refer to existing IDs.")
print("No card records, images, or browser progress altered.")
, '// s361 since card was removed by request; no startup override needed.',src,flags=re.M)
assert count==1, ('Unexpected count of stale since override',count)
# Catch any other deleted-card startup overrides, not just since.
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert all(x in ids for x in startup_ids), ("Stale overrides left",startup_ids)
assert len(startup_ids)==2 and set(startup_ids)=={"s167","s204"}
assert src.count('id="exportCards"')==0 and "cardEditLayer" not in src
assert src.rstrip().endswith("</html>")
# Syntax check the actual inline script before writing.
matches=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(matches)==1
jsfile=Path("/tmp/toeic_after_repair.js")
jsfile.write_text(matches[0],encoding="utf-8")
r=subprocess.run(["node","--check",str(jsfile)],capture_output=True,text=True)
assert r.returncode==0, r.stderr[-2500:]
path.write_text(src,encoding="utf-8")
print("Repaired stale s361 startup override; JavaScript syntax validation PASSED")
print("Validated 197 + 163 = 360 cards, all remaining overrides refer to existing IDs.")
print("No card records, images, or browser progress altered.")

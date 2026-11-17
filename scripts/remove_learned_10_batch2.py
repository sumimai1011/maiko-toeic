#!/usr/bin/env python3
"""Remove only 10 explicitly approved memorized cards, preserving everything else."""
import json
from pathlib import Path
path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
start=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[start:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(228,163),("unexpected original counts",len(base),len(extra))
requested={
"s87":"take effect",
"s90":"empty A of B",
"s99":"keep you posted",
"s100":"as to",
"s109":"outline",
"s111":"accordingly",
"s122":"consecutive",
"s125":"timely",
"s142":"burden",
"s154":"preventive"
}
found={c["id"]:c["front"] for c in base if c["id"] in requested}
assert found==requested,("Target cards don't match",found)
assert not any(c["id"] in requested for c in extra)
remaining=[c for c in base if c["id"] not in requested]
assert len(remaining)==218 and len(remaining)+len(extra)==381
src=src[:start]+json.dumps(remaining,ensure_ascii=False,separators=(",",":"))+src[start+used:]
assert "preserveMergedCardProgress" in src
assert "cardEditLayer" not in src and 'id="exportCards"' not in src
assert src.count("BASE.push(")==1 and src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Precisely removed:",", ".join(f"{key} {value}" for key,value in requested.items()))
print("Verified final cards:",len(remaining),"+",len(extra),"=",len(remaining)+len(extra))
print("All other card metadata, images, and browser learning-history code preserved.")

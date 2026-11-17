#!/usr/bin/env python3
"""Remove exactly five explicitly approved learned cards from the published TOEIC deck.
Retain all other card data, images, and local browser learning history."""
import json
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
marker="const BASE="
assert src.count(marker)==1 and src.count("BASE.push(")==1
start=src.index(marker)+len(marker)
base,used=json.JSONDecoder().raw_decode(src[start:])
push_start=src.index("BASE.push(")+len("BASE.push(")
push_end=src.index("\n);",push_start)
extra=json.loads("["+src[push_start:push_end].strip().strip(",")+"]")
assert len(base)==233 and len(extra)==163 and len(base)+len(extra)==396, (len(base),len(extra))
requested={
 "s9":"consist of",
 "s10":"insist on",
 "s17":"turnaround time",
 "s18":"up and running",
 "s44":"whether to do",
}
found={c["id"]:c["front"] for c in base if c["id"] in requested}
assert found==requested, ("Unexpected deletion targets",found)
assert not any(x["id"] in requested for x in extra)
before_other=[x for x in base if x["id"] not in requested]
assert len(before_other)==228
src=src[:start]+json.dumps(before_other,ensure_ascii=False,separators=(",",":"))+src[start+used:]
assert "preserveMergedCardProgress" in src, "Do not modify the previous learning-history safeguard"
assert len(before_other)+len(extra)==391
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
assert src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Removed exactly:",", ".join(f"{k} {v}" for k,v in requested.items()))
print("Verified card count:",len(before_other),"+",len(extra),"=",len(before_other)+len(extra))
print("No other cards, pictures, localStorage, or study history altered.")

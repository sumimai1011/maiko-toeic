#!/usr/bin/env python3
"""Delete exactly the 21 third-batch TOEIC cards explicitly approved by the learner.
Match both card ID and front; preserve all other metadata/images/progress code."""
import json
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
p=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[p:])
push_start=src.index("BASE.push(")+len("BASE.push(")
push_end=src.index("\n);",push_start)
extra=json.loads("["+src[push_start:push_end].strip().strip(",")+"]")
assert (len(base),len(extra))==(218,163),("Unexpected deck state",len(base),len(extra))
requested={
"s165":"enclosed",
"s208":"nor do I ~",
"s270":"be posted",
"s287":"those who",
"s288":"those with",
"s292":"at no extra cost",
"s294":"be credited to an account",
"s297":"expect A to do",
"s298":"be expected to do",
"s302":"anywhere (that) S + V",
"s303":"the date of expiration",
"s304":"consider ~ing",
"s307":"the single + 最上級",
"s310":"be stacked up",
"s311":"anyone who + V / whoever + V",
"s354":"economical",
"s361":"since",
"s364":"even",
"s367":"acquaint oneself with ～",
"s368":"commission",
"s370":"be subjected to ～",
}
assert len(requested)==21
matched=[c for c in base+extra if c["id"] in requested and c["front"]==requested[c["id"]]]
assert len(matched)==21 and {c["id"] for c in matched}==set(requested),("Missing/duplicated targets", matched)
assert not any(c["id"] in requested and c["front"]!=requested[c["id"]] for c in base+extra), "Ambiguous IDs; refuse unsafe deletion"
remaining=[c for c in base if c["id"] not in requested]
other_extra=[c for c in extra if c["id"] not in requested]
assert len(remaining)==197 and len(other_extra)==163 and len(remaining)+len(other_extra)==360
assert len(other_extra)==len(extra), "Unexpected extra card alteration"
assert all(c==d for c,d in zip(other_extra,extra)), "Other card modifications detected"
src=src[:p]+json.dumps(remaining,ensure_ascii=False,separators=(",",":"))+src[p+used:]
assert "preserveMergedCardProgress" in src, "Learning history handling unexpectedly removed"
assert "cardEditLayer" not in src and 'id="exportCards"' not in src
assert src.count("BASE.push(")==1 and src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Removed exactly 21 IDs:",", ".join(f"{key} {front}" for key,front in requested.items()))
print("Verified final:",len(remaining),"+",len(other_extra),"=",len(remaining)+len(other_extra))
print("All remaining card data/images and client learning history untouched.")

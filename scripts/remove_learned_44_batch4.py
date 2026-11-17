#!/usr/bin/env python3
"""User-approved batch 4: delete precisely 44 cards from the currently published 360.

Position is checked against the original 402-card sequence (201..300).
Every selected record must match position, ID, and English front. No others
are modified, and no client-side learning history is cleared.
"""
import json, re, subprocess
from pathlib import Path

targets = [
 (211,"s381","local resident"),
 (214,"s384","heighten"),
 (216,"s386","constructive"),
 (217,"s387","distribute"),
 (223,"s393","flooding"),
 (224,"s394","precaution"),
 (226,"s396","order from"),
 (227,"s397","package"),
 (229,"s399","relocation"),
 (237,"s375","substitute"),
 (239,"s377","confectionery"),
 (240,"s378","formally"),
 (244,"s383","advertise on a website / in a newspaper"),
 (247,"s386","commitment"),
 (249,"s391","throughout"),
 (250,"s392","demonstrate respect for ～"),
 (253,"s396","contractor"),
 (255,"s398","voice recognition software"),
 (256,"s399","pinpoint"),
 (257,"s400","diagnostic"),
 (261,"s404","multinational"),
 (262,"s405","oil giant"),
 (263,"s406","beyond"),
 (265,"s408","competitive"),
 (266,"s409","refrain from ~ing"),
 (271,"s414","submit ～ for approval"),
 (272,"s415","lecturer"),
 (274,"s417","inquiry"),
 (275,"s418","warranty"),
 (276,"s419","select"),
 (279,"s425","at the rate of ～"),
 (280,"s426","present a lecture"),
 (281,"s427","drape"),
 (282,"s428","correspondingly"),
 (284,"s430","miscellaneous"),
 (286,"s432","redo"),
 (289,"s435","whole-grain"),
 (290,"s436","head over to"),
 (291,"s437","loaner car"),
 (292,"s438","developer"),
 (295,"s441","fill out"),
 (296,"s442","displeasure"),
 (297,"s443","give away"),
 (298,"s444","precise")
]
assert len(targets)==44 and len({x[0] for x in targets})==44
path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
start=src.index("const BASE=")+len("const BASE=")
base, consumed=json.JSONDecoder().raw_decode(src[start:])
p=src.index("BASE.push(")+len("BASE.push(")
q=src.index("\n);",p)
extra=json.loads("["+src[p:q].strip().strip(",")+"]")
assert (len(base),len(extra))==(197,163), f"Deck changed: {len(base)}+{len(extra)}"

# All 36 preceding approved deletions fell within original positions 1-200.
# The six merged duplicates removed from the extra array had original positions
# 316, 322, 323, 353, 354, 356; no changes to its positions 234-300.
selected_base=set()
selected_extra=set()
for position, card_id, front in targets:
    if position<=233:
        index=position-1-36
        assert 0<=index<len(base)
        card=base[index]
        selected_base.add(index)
    else:
        index=position-234
        assert 0<=index<len(extra)
        card=extra[index]
        selected_extra.add(index)
    assert (card["id"],card["front"])==(card_id,front), (
        "Position/ID/front mismatch",position,card_id,front,
        card.get("id"),card.get("front"))
assert len(selected_base)+len(selected_extra)==44
new_base=[card for i,card in enumerate(base) if i not in selected_base]
new_extra=[card for i,card in enumerate(extra) if i not in selected_extra]
assert len(new_base)+len(new_extra)==316
assert len(new_base)==197-len(selected_base) and len(new_extra)==163-len(selected_extra)

# Surgical JSON literal replacement, preserving every retained record verbatim
# at the data structure level (including examples/images), and other HTML/JS.
src=src[:start]+json.dumps(new_base,ensure_ascii=False,separators=(",",":"))+src[start+consumed:]
p=src.index("BASE.push(")+len("BASE.push(")
q=src.index("\n);",p)
src=src[:p]+"\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in new_extra)+src[q:]

ids={c["id"] for c in new_base+new_extra}
# Most importantly, deleting since earlier broke startup due to an old
# Object.assign(BASE.find()) call. Ensure this cannot recur here.
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert all(card_id in ids for card_id in startup_ids), ("Invalid startup references",startup_ids)
assert "preserveMergedCardProgress" in src
assert 'id="exportCards"' not in src and "cardEditLayer" not in src
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(scripts)==1
js_file=Path("/tmp/toeic_batch4_syntax.js")
js_file.write_text(scripts[0],encoding="utf-8")
check=subprocess.run(["node","--check",str(js_file)],capture_output=True,text=True)
assert check.returncode==0, check.stderr
assert src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("All 44 original positions, IDs and fronts verified.")
print("Deleted from BASE:",len(selected_base),"and BASE.push:",len(selected_extra))
print("Final verified card count:",len(new_base),"+",len(new_extra),"=",len(new_base)+len(new_extra))
print("Startup references verified:",startup_ids)
print("JavaScript syntax PASSED; remaining cards/images and study-history code unchanged.")

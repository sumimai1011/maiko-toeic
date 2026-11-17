#!/usr/bin/env python3
"""Delete the exact 45 cards approved in batch 5; check original position, id, front.
Keep both new cards, all other images/cards, and stored learning history untouched."""
from pathlib import Path
import json, re, subprocess

targets=[
 (301,"s447","reward"),
 (302,"s448","quarterly"),
 (303,"s449","defect"),
 (304,"s450","mark down"),
 (306,"s452","visual aid"),
 (307,"s453","hire"),
 (308,"s454","comprehensive"),
 (310,"s456","imply"),
 (312,"s458","rub off"),
 (314,"s460","take care of"),
 (317,"s463","exhaust"),
 (318,"s464","temporary agency"),
 (320,"s466","diabetes"),
 (326,"s472","means"),
 (328,"s474","specify"),
 (330,"s476","courthouse"),
 (331,"s477","weave"),
 (335,"s481","excerpt"),
 (337,"s483","projection"),
 (338,"s484","sales figure"),
 (345,"s491","cease"),
 (346,"s492","devotion"),
 (348,"s494","applaud"),
 (350,"s496","for the time being"),
 (352,"s498","go through"),
 (355,"s501","tutoring"),
 (358,"s504","memorabilia"),
 (359,"s505","monetary"),
 (360,"s506","playbook"),
 (364,"s510","throw out"),
 (369,"s515","landline phone"),
 (373,"s519","turmoil"),
 (382,"s528","hallway"),
 (383,"s529","driveway"),
 (384,"s530","utensil"),
 (385,"s531","specification"),
 (386,"s532","transfer"),
 (388,"s534","motorcycle"),
 (390,"s536","hire a service"),
 (391,"s537","address an invitation"),
 (393,"s539","renowned"),
 (395,"s541","art"),
 (399,"s545","cause"),
 (401,"s547","weaver"),
 (402,"s548","range")
]
assert len(targets)==45 and len(set(p for p,_,_ in targets))==45

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
s=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[s:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,128), ("Unexpected source count",len(base),len(extra))
new_cards={
 "new_call_off_20261117":("call off","中止する"),
 "new_mail_20261117":("mail","郵便（email＝電子メール）")
}
for id,(front,meaning) in new_cards.items():
 matches=[x for x in base if x["id"]==id]
 assert len(matches)==1 and (matches[0]["front"],matches[0]["meaning"])==(front,meaning)

# Original export positions 234-402 were inside BASE.push. During batch 4,
# 35 positions <=300 were removed. Previously consolidated duplicates at
# 316,322,323,353,354,356 were removed as well. No other positions >=301
# have been deleted until this batch.
previously_removed=[316,322,323,353,354,356]
selected=set()
for original_position,card_id,front in targets:
 index=original_position-234-35-sum(k<original_position for k in previously_removed)
 assert 0<=index<len(extra), (original_position,index)
 card=extra[index]
 assert (card["id"],card["front"])==(card_id,front),(
  "Position, ID, or English mismatch",original_position,
  (card_id,front),(card["id"],card["front"]))
 selected.add(index)
assert len(selected)==45

new_extra=[x for i,x in enumerate(extra) if i not in selected]
assert len(new_extra)==83 and len(base)+len(new_extra)==273
assert {x["id"] for x in new_extra}.isdisjoint({id for _,id,_ in targets})
assert [x for x in base]==base, "BASE must not change"
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
src=src[:a]+"\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in new_extra)+src[b:]

# Deleting 'since' once caused a 0-card crash. Check all startup overrides
# reference cards that are actually present. Old progress data stays in place.
ids={x["id"] for x in base+new_extra}
refs=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert all(id in ids for id in refs),("Stale startup card overrides",refs)
assert "preserveMergedCardProgress" in src
assert "new_call_off_20261117" in ids and "new_mail_20261117" in ids
assert "cardEditLayer" not in src and 'id="exportCards"' not in src
assert src.rstrip().endswith("</html>")
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(scripts)==1
js=Path("/tmp/toeic_batch5_check.js")
js.write_text(scripts[0],encoding="utf-8")
check=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
assert check.returncode==0,check.stderr
path.write_text(src,encoding="utf-8")
print("All 45 original numbers, IDs and English phrases matched exactly.")
print("Verified 190 + 83 = 273 cards.")
print("call off and mail retained; other cards/images and browser study history unchanged.")
print("Startup references validated:",refs,"; Node JavaScript syntax check PASSED.")

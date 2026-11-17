#!/usr/bin/env python3
"""Fix mistaken duplicate import of 169 already-embedded TOEIC cards.
Keep all original card images and local study history untouched."""
import json
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
marker="const BASE="
assert src.count(marker)==1
start=src.index(marker)+len(marker)
base, consumed=json.JSONDecoder().raw_decode(src[start:])
assert len(base) in (233,402), "Unexpected base cards: "+str(len(base))

push_start=src.index("BASE.push(")+len("BASE.push(")
push_end=src.index("\n);",push_start)
push_cards=json.loads("["+src[push_start:push_end].strip().strip(",")+"]")
assert len(push_cards)==169, "Expected 169 original pushed cards; got "+str(len(push_cards))

approved=[
 ("legislation","法律、法令、立法","法律、立法"),
 ("yet","しかし、それでも、～でありながら","まだ、しかし"),
 ("name","名付ける、任命する、名前を挙げる","名付ける、任命する"),
 ("commitment","約束、献身、責任ある取り組み","約束、献身"),
 ("recognition","評価、表彰、認識","評価、表彰"),
 ("patron","利用客、常連客、後援者","利用客、後援者"),
 ("select","選ぶ、厳選された、特定の","選ぶ、厳選された"),
 ("drape","カーテン、覆い布、～を布で覆う","カーテン、布で覆う"),
 ("miscellaneous","雑多な、さまざまな、雑貨","雑多な、さまざまな"),
 ("exhaust","排気、排気ガス、疲れ果てさせる","排気ガス、疲れ果てさせる"),
 ("affirm","断言する、確認する、支持する","断言する、確認する")
]
changed=[]
for c in push_cards:
 for front,old,new in approved:
  if c.get("front")==front and c.get("meaning")==old:
   c["meaning"]=new
   changed.append(front)
assert len(changed)==11 or (len(base)==233 and not changed), changed
if len(base)==402:
 extra=base[233:]
 assert len(extra)==169 and all(c.get("id")==f"mig_{i:03d}" for i,c in enumerate(extra))
 assert all(c.get("front")==push_cards[i].get("front") for i,c in enumerate(extra)), "Migration cards differ from original."
 base=base[:233]
 src=src[:start]+json.dumps(base,ensure_ascii=False,separators=(",",":"))+src[start+consumed:]
 src=src[:src.index("BASE.push(")+len("BASE.push(")]+ "\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in push_cards) +src[src.index("\n);",src.index("BASE.push(")):]
else:
 print("Incorrect migration already removed.")
# Remove faulty local-card migration shim which was based on the wrong 169-card premise.
shim="// Canonical 402 cards; retain old browser cards and review history as backup."
if shim in src:
 a=src.index(shim)
 b=src.index("\nrenderHome();\n</script>",a)
 src=src[:a]+src[b:]
# Keep the approved "since" meaning (the preexisting override is applied after BASE.push).
src=src.replace('meaning:"～以来、～なので、それ以来"','meaning:"～以来、～なので"')
assert src.count("const BASE=")==1
assert src.count("BASE.push(")==1
assert "const LEGACY_PAIRS=" not in src
assert src.count('id="exportCards"')==0
assert "cardEditLayer" not in src
assert src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Verified canonical cards:", len(base), "+",len(push_cards),"=",len(base)+len(push_cards))
print("Approved updated pushed meanings:",changed)
print("Removed only mistakenly imported duplicate entries, not localStorage or progress.")

#!/usr/bin/env python3
"""Publish the 22 user-approved entries from the 2026-11-25 handwritten note.
Operate on *live repository* index.html, not an outdated local copy.
Preserve existing cards, image data, POINT and daily 80 review history.
"""
import json,re,subprocess
from pathlib import Path

entries=[
 ("文法","all / no / most + 複数名詞","後ろには複数名詞が来る","All cars must be inspected before delivery."),
 ("文法","several / many / few + 複数名詞","後ろには複数名詞が来る","Several cars are parked outside."),
 ("熟語","have since been","その後ずっと〜されている／それ以来〜された","The company opened in 2010 and has since expanded worldwide."),
 ("熟語","invite A to B for C","AをBにCのために招待する","We invited clients to the hotel for dinner."),
 ("単語","reception","レセプション、歓迎会","A reception will be held after the ceremony."),
 ("単語","valuation","査定、評価","The property valuation took several days."),
 ("単語","secure","確保する","We need to secure additional funding."),
 ("熟語","though (they are) promising","有望ではあるが","Though promising, the plan still needs work."),
 ("熟語","a deal valued at X","X相当の取引","The company signed a deal valued at $2 million."),
 ("熟語","deal value","取引額","The deal value exceeded expectations."),
 ("単語","imperfection","欠陥、欠点","Minor imperfections were found in the product."),
 ("熟語","pertain to","〜に関係する、〜に適用される","These rules pertain to all employees."),
 ("単語","oneself","自分自身","She taught herself how to code."),
 ("単語","trade show","見本市","The company will exhibit at the trade show."),
 ("熟語","be pertinent to","〜に関連している","The comments are pertinent to the topic."),
 ("文法","one of the + 最上級 + 複数名詞","『最も〜なものの1つ』を表す","This is one of the best solutions."),
 ("単語","overwhelming","圧倒的な","The response from customers was overwhelming."),
 ("単語","demolition","解体","The demolition of the old building begins next week."),
 ("熟語","with the exception of","〜を除いて","All staff attended with the exception of Mr. Sato."),
 ("熟語","be slated for","〜が予定されている","The new system is slated for release next month."),
 ("単語","table of contents","目次","Please check the table of contents first."),
 ("単語","acknowledgements","謝辞","Read the acknowledgements at the end of the book.")
]
assert len(entries)==22
path=Path("index.html")
source=path.read_text(encoding="utf-8")
start=source.index("const BASE=")+len("const BASE=")
base,consumed=json.JSONDecoder().raw_decode(source[start:])
a=source.index("BASE.push(")+len("BASE.push(")
b=source.index("\n);",a)
extra=json.loads("["+source[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,99),(len(base),len(extra))
assert len(base)+len(extra)==289
assert "point-onepage" in source
assert "const DAILY_TARGET=80;" in source
assert "preserveMergedCardProgress" in source
assert "new_call_off_20261117" in source and "new_mail_20261117" in source
assert source.rstrip().endswith("</html>")

seen={x["front"].strip().casefold() for x in base+extra}
new=[]
for i,(typ,front,meaning,example) in enumerate(entries,1):
  if front.strip().casefold() in seen:
    print("Already exists, skipping duplicate:",front)
    continue
  cid="note_20261125_"+str(i).zfill(2)
  assert cid not in {x["id"] for x in base+extra}
  new.append(dict(type=typ,front=front,meaning=meaning,example=example,image="",id=cid))
  seen.add(front.strip().casefold())
assert len(new)==22,("Unexpected duplicates",len(new))
extra_after=extra+new
payload="\n"+",\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in extra_after)
updated=source[:a]+payload+source[b:]
assert updated[:a]==source[:a]
assert updated[a+len(payload):]==source[b:]
assert len(base)+len(extra_after)==311
assert all((x["front"],x["meaning"])==(front,meaning) for x,(_,front,meaning,_) in zip(new,entries))
check_base,_=json.JSONDecoder().raw_decode(updated[updated.index("const BASE=")+len("const BASE="):])
assert check_base==base
ap=updated.index("BASE.push(")+len("BASE.push(")
ae=updated.index("\n);",ap)
check_extra=json.loads("["+updated[ap:ae].strip().strip(",")+"]")
assert check_extra==extra_after
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',updated)
assert all(x in {c["id"] for c in base+extra_after} for x in startup_ids)
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",updated,re.S|re.I)
assert len(scripts)==1
js_file=Path("/tmp/toeic_20261125_22.js")
js_file.write_text(scripts[0],encoding="utf-8")
syntax=subprocess.run(["node","--check",str(js_file)],capture_output=True,text=True)
assert syntax.returncode==0,syntax.stderr
path.write_text(updated,encoding="utf-8")
print("SUCCESS: Added exactly 22 terms to the live original 289 cards => 311 total.")
print("One-page POINT, daily 80-card target, all prior image/card data and progress code unchanged.")
print("JavaScript syntax check and startup-reference checks: PASSED.")

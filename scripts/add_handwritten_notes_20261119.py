#!/usr/bin/env python3
"""Add vocabulary transcribed from two handwritten photos to the live TOEIC app."""
import json,re,subprocess
from pathlib import Path

entries=[
 ("熟語","the broadest possible audience","できるだけ幅広い聴衆・観客","We hope to reach the broadest possible audience."),
 ("熟語","aside from","～に加えて／～を除いて","Aside from English, she speaks French."),
 ("熟語","far more successful","はるかに成功している（farは比較級の強調）","The new campaign was far more successful."),
 ("熟語","set aside","確保する／取っておく","We set aside funds for the project."),
 ("熟語","hire a service","サービスを依頼する／業務を委託する","We hired a cleaning service."),
 ("単語","identifiable","識別可能な／特定できる","The error is easily identifiable."),
 ("単語","distinctive","独特の／特徴的な","The building has a distinctive design."),
 ("単語","shoreline","海岸線","The shoreline stretches for miles."),
 ("単語","stock / share","株式（stock＝株式全般、share＝個々の株）","She bought shares in the company."),
 ("熟語","an extended period of time","長期間","The equipment will be stored for an extended period of time."),
 ("単語","theatrical","演劇の／劇場の","She has experience in theatrical productions."),
 ("単語","substantially","かなり／大幅に","Costs have increased substantially."),
 ("熟語","potential successor","後継者候補","She is considered a potential successor."),
 ("単語","enthusiast","熱心な愛好家","He is a photography enthusiast."),
 ("熟語","utility costs","光熱費／水道光熱費","Utility costs have risen this year."),
 ("単語","conventionally","従来の方法で／慣習的に","The material is conventionally processed at high temperatures.")
]
assert len(entries)==16
p=Path("index.html")
s=p.read_text(encoding="utf8")
st=s.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(s[st:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
before=base+extra
assert len(before)==273,("Unexpected count",len(base),len(extra))
assert len({(x["id"],x["front"]) for x in before})==273
assert all(x["front"] in {c["front"] for c in before} for x in base if x["front"] in {"call off","mail"})
assert s.count("point-onepage")==1
existing={x["front"].strip().casefold() for x in before}
ids={x["id"] for x in before}
new=[]
for kind,front,meaning,example in entries:
 assert front.casefold() not in existing,("Already in application",front)
 identifier="photo_20261119_"+str(len(new)+1).zfill(2)
 assert identifier not in ids
 new.append({"type":kind,"front":front,"meaning":meaning,"example":example,"image":"","id":identifier})
assert len(new)==16
new_extra=extra+new
s2=s[:a]+"\n"+",\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in new_extra)+s[b:]
assert len(base)+len(new_extra)==289
assert s2[:a]==s[:a] and s2[a+len("\n"+",\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in new_extra)):]==s[b:]
assert "preserveMergedCardProgress" in s2
assert s2.rstrip().endswith("</html>")
refs=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',s2)
assert all(cid in {x["id"] for x in base+new_extra} for cid in refs),refs
js=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s2,re.S|re.I)
assert len(js)==1
checkfile=Path("/tmp/toeic_photo_add_20261119.js")
checkfile.write_text(js[0],encoding="utf8")
ck=subprocess.run(["node","--check",str(checkfile)],capture_output=True,text=True)
assert ck.returncode==0,ck.stderr
p.write_text(s2,encoding="utf8")
print("Added exactly 16 handwritten-note cards; verified total 289.")
print("Original 273 cards, images, one-page POINT and stored progress logic unchanged.")
print("JavaScript syntax check passed. Startup card overrides:",refs)

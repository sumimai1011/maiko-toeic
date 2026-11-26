import json,re
from pathlib import Path
s=Path("index.html").read_text(encoding="utf8")
p=s.index("const BASE=")+len("const BASE=")
base,_=json.JSONDecoder().raw_decode(s[p:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
cards=base+extra
assert len(cards)==311
targets=["resolutely","suppkement","supplement","in a timely manner","as early as","exceed expectations","leave of absence","respondent","successor","dues","promote/advance","leave O C","retrieve","sublet","prospective","sales projection","favorable","demand exceeds production","exhaust system","store-wide","take note","mail","name","patron","booklet","sanctuary","recipient","along the way","rest assured","skyline","lawn","lawn mower","in action","shoreline","all/no/most","several/many/few","reception","a deal valued at X","deal value","oneself","one of the","as of","as of today","acquaint","be acquainted","company directory","directory","implement","be implemented","constructive"]
for t in targets:
 m=[(i,c["id"],c["front"],c.get("meaning","")) for i,c in enumerate(cards) if t.casefold() in c["front"].casefold()]
 print("TARGET",json.dumps({"term":t,"matches":m},ensure_ascii=False))
missing=[(i,c["id"],c["front"],c.get("meaning","")) for i,c in enumerate(cards) if not (c.get("example") or "").strip()]
print("MISSING_EXAMPLES_COUNT",len(missing))
for x in missing:print("NEEDS_EXAMPLE",json.dumps(x,ensure_ascii=False))
print("TRANSLATION_MULTI")
for i,c in enumerate(cards):
 m=c.get("meaning","")
 if any(sep in m for sep in ["、","／","/","・",";"]):
  print("MULTI",json.dumps([i,c["id"],c["front"],m],ensure_ascii=False))
print("TOTAL",len(cards))

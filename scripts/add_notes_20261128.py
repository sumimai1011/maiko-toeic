import json,re,subprocess,unicodedata
from pathlib import Path
entries=json.loads("[[\"単語\",\"identify\",\"～を特定する、見いだす\",\"We need to identify new strategies.\"],[\"熟語\",\"whether or not\",\"～かどうか、～であろうとなかろうと\",\"Please confirm whether or not you will attend.\"],[\"単語\",\"readily\",\"容易に\",\"The information is readily available.\"],[\"熟語\",\"be doubtful that ～\",\"～かどうか疑問に思う\",\"I am doubtful that the project will be completed on time.\"],[\"文法\",\"still と yet の位置の違い\",\"He still has not decided.\\nHe has not decided yet.\\nHe has not yet decided.\\nいずれも「彼はまだ決めていない」。\",\"He still has not decided. / He has not decided yet. / He has not yet decided.\"],[\"文法\",\"過去分詞 ＋ 名詞\",\"～された名詞（approved ways：承認された方法）\",\"Please use the approved ways to submit your application.\"],[\"熟語\",\"employee morale\",\"従業員の士気\",\"Flexible schedules can improve employee morale.\"],[\"熟語\",\"send in\",\"提出する\",\"Please send in your application by Friday.\"]]")
p=Path("index.html")
s=p.read_text(encoding="utf-8")
st=s.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(s[st:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
cards=base+extra
def norm(x):
 return re.sub(r"\s+","",unicodedata.normalize("NFKC",x).casefold().replace("’","'").replace("～","~"))
aliases={"whether or not":["whether or not ～"],"be doubtful that ～":["be doubtful that","be doubtful that ~"],"employee morale":["employee moral"],"still と yet の位置の違い":["stillとyetの位置の違い"],"過去分詞 ＋ 名詞":["過去分詞 + 名詞"],"send in":["send in ～"]}
before=len(cards)
drop=set()
added=0
for i,(typ,front,meaning,example) in enumerate(entries,1):
 keys={norm(x) for x in [front]+aliases.get(front,[])}
 matches=[c for c in cards if norm(c["front"]) in keys and id(c) not in drop]
 if matches:
  keep=matches[0]
  print("MATCH",[(c["id"],c["front"]) for c in matches])
  keep.update(front=front,meaning=meaning,example=example)
  for c in matches[1:]: drop.add(id(c))
 else:
  cid="note_20261128_"+str(i).zfill(2)
  assert cid not in {c["id"] for c in cards}
  c=dict(id=cid,type=typ,front=front,meaning=meaning,example=example,image="")
  extra.append(c);cards.append(c);added+=1
# Exact duplicate fronts and meanings only; preserve first ID, do not merge distinct senses.
seen=set()
for c in cards:
 if id(c) in drop: continue
 key=(norm(c["front"]),norm(c["meaning"]))
 if key in seen:
  print("EXACT DUPLICATE",c["id"],c["front"])
  drop.add(id(c))
 else: seen.add(key)
base=[c for c in base if id(c) not in drop]
extra=[c for c in extra if id(c) not in drop]
final=base+extra
s=s[:st]+json.dumps(base,ensure_ascii=False,separators=(",",":"))+s[st+used:]
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
s=s[:a]+"\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in extra)+s[b:]
assert all(cid in {c["id"] for c in final} for cid in re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',s))
assert "const DAILY_TARGET=80;" in s
assert len(final)==before+added-len(drop)
for _,front,meaning,_ in entries:
 assert sum(c["front"]==front and c["meaning"]==meaning for c in final)==1
js=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s,re.S|re.I)
assert len(js)==1
Path("/tmp/toeic-check.js").write_text(js[0],encoding="utf-8")
subprocess.run(["node","--check","/tmp/toeic-check.js"],check=True)
p.write_text(s,encoding="utf-8")
print("SUCCESS before",before,"added",added,"removed duplicates",len(drop),"final",len(final))

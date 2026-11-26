import json,re,subprocess,unicodedata
from pathlib import Path
entries=json.loads("[[\"文法\",\"cause + 名詞\",\"～を引き起こす\",\"Heavy rain may cause delays.\"],[\"文法\",\"a round of + 複数名詞\",\"一連の～\",\"A round of interviews will begin Monday.\"],[\"単語\",\"mandatory\",\"必須の\",\"Attendance is mandatory.\"],[\"単語\",\"contribution\",\"貢献、寄付\",\"Thank you for your contribution.\"],[\"熟語\",\"strictly voluntary\",\"完全に任意の\",\"Participation is strictly voluntary.\"],[\"熟語\",\"failure to do\",\"～しなかったこと（failureは名詞）\",\"Failure to comply may result in penalties.\"],[\"熟語\",\"in the comfort of one's own home\",\"自宅でくつろぎながら\",\"Study in the comfort of your own home.\"],[\"熟語\",\"base of clients\",\"顧客基盤\",\"The firm has a large base of clients.\"],[\"文法\",\"接続詞 + S + be動詞\",\"主節と従属節の主語が同じ場合、従属節のSとbe動詞を省略できる。\",\"When last reviewed, the policy was still valid.\"],[\"文法\",\"how + 形容詞／副詞 + S + V\",\"どれほど～なのか\",\"We assessed how quickly the team responded.\"]]")
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
aliases={"cause + 名詞":["cause + 名詞","cause"],"a round of + 複数名詞":["a round of + 複数名詞","a round of"],"base of clients":["base of clients","client base"],"how + 形容詞／副詞 + S + V":["how + 形容詞/副詞 + S + V"],"接続詞 + S + be動詞":["接続詞 + S + be動詞"]}
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
  cid="note_20261126_evening_"+str(i).zfill(2)
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

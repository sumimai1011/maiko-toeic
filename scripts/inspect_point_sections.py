from pathlib import Path
import re
s=Path("index.html").read_text(encoding="utf8")
print("file length",len(s),"lines",s.count("\n"))
for word in ["テスト概要","文法ルール①","文法ルール③","代名詞・形容詞まとめ","同形語メモ","前置詞・接続詞・接続副詞","POINT","point","grammar","renderPoint"]:
 print("\nSEARCH",repr(word),"count",s.count(word))
 occurrences=list(re.finditer(re.escape(word),s))
 for m in (occurrences[:4] + (occurrences[-2:] if len(occurrences)>4 else [])):
  print("LOCATION",m.start(),"LINE",s.count("\n",0,m.start())+1,repr(s[max(0,m.start()-250):m.start()+550]))
print("\nFILE LAST 7000\n",s[-7000:])

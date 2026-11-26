from pathlib import Path
import re,json
s=Path("index.html").read_text(encoding="utf8")
for q in ["function studyDeck()","function loadProgress(","function saveProgress(","function stateFor(","function preserveMergedCardProgress(","function renderHome()","renderHome();","const BASE=","BASE.push(","function fitFrontText()","const PRON=","const progress=","let progress=","const userCards=","function ymd(","window.addEventListener","serviceWorker"]:
 print("\nFIND",repr(q),"COUNT",s.count(q))
 for m in list(re.finditer(re.escape(q),s))[-2:]:
  print("AT",m.start(),s[max(0,m.start()-450):m.start()+950][:1400])
print("\nLAST 3000\n",s[-3000:])

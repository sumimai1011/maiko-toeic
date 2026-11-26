from pathlib import Path
s=Path("index.html").read_text(encoding="utf8")
terms=["<div class=\"hero\"","id=\"start\"","id=\"dueCount\"","const DAILY_TARGET","function dailyQueue()","function renderHome()","function startStudy(","function showCard()","function rate(","function finish","$(\"start\").onclick","$(\"back\").onclick","queue.length"]
for term in terms:
 print("\nINSPECT",repr(term),"COUNT",s.count(term))
 idx=s.find(term)
 if idx>=0:print(s[max(0,idx-300):idx+2200][:2500])

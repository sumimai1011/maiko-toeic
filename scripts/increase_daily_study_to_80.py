#!/usr/bin/env python3
"""Adjust TOEIC daily quota from 30 cards to 80; do not modify vocabulary or study records."""
import json,re,subprocess
from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf8")
st=s.index("const BASE=")+len("const BASE=")
base,_=json.JSONDecoder().raw_decode(s[st:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,99)
assert "point-onepage" in s and "preserveMergedCardProgress" in s
assert "call off" in [x["front"] for x in base+extra]
assert "mail" in [x["front"] for x in base+extra]

# Make a new completion flag so a prior 30-card session does not suppress
# today's new 80-card target; no old history or review dates are discarded.
changes=[
 ('const DAILY_TARGET=30;','const DAILY_TARGET=80;'),
 ('const DAILY_DONE_KEY="toeic_daily30_completed_v1";','const DAILY_DONE_KEY="toeic_daily80_completed_v1";'),
 ('// At least 30 cards a day (roughly 15 minutes at 30 seconds/card).','// At least 80 cards a day; review-due cards remain highest priority.'),
 ('// A manual single-card study must not mark the daily session completed.','// A manual single-card study must not mark the daily session completed.'),
 ('"学習スタート（"+todayCards.length+"枚・約15分〜）"','"学習スタート（"+todayCards.length+"枚）"')
]
for before,after in changes:
 if before==after:continue
 assert s.count(before)==1,("Expected exact match",before,s.count(before))
 s=s.replace(before,after,1)
assert "const DAILY_TARGET=80;" in s and 'toeic_daily80_completed_v1' in s
assert "function dailyQueue()" in s and "const scheduled=due()" in s
assert "const needed=Math.max(0,DAILY_TARGET-scheduled.length)" in s
assert "preserveMergedCardProgress" in s and s.rstrip().endswith("</html>")
# The original BASE.push and BASE arrays must be unchanged; only daily quota literals may differ.
bp=s.index("const BASE=")+len("const BASE=")
b2,_=json.JSONDecoder().raw_decode(s[bp:])
ap=s.index("BASE.push(")+len("BASE.push(")
ae=s.index("\n);",ap)
e2=json.loads("["+s[ap:ae].strip().strip(",")+"]")
assert (b2,e2)==(base,extra)
ref_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',s)
assert all(x in {c["id"] for c in base+extra} for x in ref_ids)
js=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s,re.S|re.I)
assert len(js)==1
f=Path("/tmp/toeic_daily80.js")
f.write_text(js[0],encoding="utf8")
syntax=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
assert syntax.returncode==0,syntax.stderr
# Test with synthetic 289-card study deck: 6 due +74 extra -> 80.
segment=s[s.index('const DAILY_TARGET=80;'):s.index('function renderHome()',s.index('const DAILY_TARGET=80;'))]
# Using known end avoids dependency on other app DOM functions.
test_code='''const localStorage={s:{},getItem(k){return this.s[k]||null},setItem(k,v){this.s[k]=v}};
const ymd=()=> "2026-11-22";
const all=Array.from({length:289},(_,i)=>({id:"x"+i,next:i<6?"2026-11-22":"2026-11-23",level:i%5}));
const studyDeck=()=>all;
const due=()=>all.filter(x=>x.next<=ymd());
'''
# Extract just the target and helper definitions up to the next unrelated function.
start=s.index('const DAILY_TARGET=80;')
end=s.index('function renderHome()',start)
fragment=s[start:end]
# Extra function declarations between these may reference DOM only when invoked.
node=Path("/tmp/daily80_smoke.js")
node.write_text(test_code+fragment+'''
const d=dailyQueue();
if(d.length!==80)throw new Error("Expected 80, got "+d.length);
if(d.filter(c=>c.next<=ymd()).length!==6)throw new Error("Due cards missing");
completeDailySession();
if(dailyQueue().length!==6)throw new Error("Completion should show only due cards");
console.log("PASS 6 due + 74 supplemental = 80; saved completion works");
''',encoding="utf8")
result=subprocess.run(["node",str(node)],capture_output=True,text=True)
assert result.returncode==0,result.stderr[-2000:]
p.write_text(s,encoding="utf8")
print("SUCCESS: Daily minimum 80 cards; 289 existing vocabulary cards preserved.")
print(result.stdout.strip())
print("Spaced repetition and user progress logic intact. JavaScript syntax passed.")

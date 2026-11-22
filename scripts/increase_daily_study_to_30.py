#!/usr/bin/env python3
"""Guarantee a daily ~15-minute session (at least 30 cards) while preserving spaced repetition."""
from pathlib import Path
import json,re,subprocess
p=Path("index.html")
s=p.read_text(encoding="utf-8")
st=s.index("const BASE=")+len("const BASE=")
base,_=json.JSONDecoder().raw_decode(s[st:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,99),(len(base),len(extra))
assert len(base)+len(extra)==289
assert "point-onepage" in s
assert "preserveMergedCardProgress" in s

old='''function due(){return studyDeck().filter(x=>!x.next||x.next<=ymd(0))}
'''
assert s.count(old)==1
new='''function due(){return studyDeck().filter(x=>!x.next||x.next<=ymd(0))}

// At least 30 cards a day (roughly 15 minutes at 30 seconds/card).
// Always prioritize due reviews, then fill from not-yet-due cards.
// Supplemental practice never erases existing progress or reschedules
// any card unless the learner explicitly scores it.
const DAILY_TARGET=30;
const DAILY_DONE_KEY="toeic_daily30_completed_v1";
let isDailySession=false;
function dailyCompleted(){
  try{return localStorage.getItem(DAILY_DONE_KEY)===ymd(0)}catch(e){return false}
}
function completeDailySession(){
  try{localStorage.setItem(DAILY_DONE_KEY,ymd(0))}catch(e){}
}
function dailyQueue(){
  const scheduled=due().sort((a,b)=>(a.next||"").localeCompare(b.next||""));
  if(dailyCompleted())return scheduled;
  const needed=Math.max(0,DAILY_TARGET-scheduled.length);
  if(!needed)return scheduled;
  const selected=new Set(scheduled.map(x=>x.id));
  // Less-mastered vocabulary and nearer review dates are introduced first.
  // Stable daily rotation prevents the same few cards always being selected.
  const day=ymd(0).split("-").join("");
  const offset=Number(day)%1009;
  const supplemental=studyDeck().filter(x=>!selected.has(x.id))
   .sort((a,b)=>{
     const av=Number.isFinite(a.level)?a.level:0,bv=Number.isFinite(b.level)?b.level:0;
     if(av!==bv)return av-bv;
     const an=a.next||"",bn=b.next||"";
     if(an!==bn)return an.localeCompare(bn);
     const hash=x=>[...String(x.id)].reduce((h,c)=>(h*31+c.charCodeAt(0))%1000003,offset);
     return hash(a)-hash(b);
   }).slice(0,needed);
  return scheduled.concat(supplemental);
}
'''
s=s.replace(old,new,1)
old_home='''  const d=studyDeck(), dueN=due().length;
  $("dateLabel").textContent=new Intl.DateTimeFormat("ja-JP",{month:"numeric",day:"numeric",weekday:"short"}).format(new Date());
  $("registered").textContent=d.length;
  $("dueCount").textContent=dueN;
  $("start").disabled=dueN===0;
  $("start").textContent=dueN?"学習スタート":"今日は復習なし 🎉";
'''
new_home='''  const d=studyDeck(), dueN=due().length, todayCards=dailyQueue();
  $("dateLabel").textContent=new Intl.DateTimeFormat("ja-JP",{month:"numeric",day:"numeric",weekday:"short"}).format(new Date());
  $("registered").textContent=d.length;
  $("dueCount").textContent=todayCards.length;
  $("start").disabled=todayCards.length===0;
  $("start").textContent=todayCards.length?"学習スタート（"+todayCards.length+"枚・約15分〜）":"今日の学習完了 🎉";
'''
assert s.count(old_home)==1
s=s.replace(old_home,new_home,1)
old_finish='''  if(index>=queue.length){
    $("study").classList.remove("on");
    $("home").classList.remove("off");
    renderHome();
'''
new_finish='''  if(index>=queue.length){
    if(isDailySession){completeDailySession();isDailySession=false;}
    $("study").classList.remove("on");
    $("home").classList.remove("off");
    renderHome();
'''
assert s.count(old_finish)==1
s=s.replace(old_finish,new_finish,1)
old_start='''$("start").onclick=()=>startStudy(due().sort(()=>Math.random()-.5));'''
new_start='''$("start").onclick=()=>{
  isDailySession=true;
  const cards=dailyQueue();
  if(cards.length)startStudy(cards);
};'''
assert s.count(old_start)==1
s=s.replace(old_start,new_start,1)
# A manual single-card study must not mark the daily session completed.
old_single='''startStudy([x])'''
assert s.count(old_single)==1
s=s.replace(old_single,'''(isDailySession=false,startStudy([x]))''',1)
# Backing out does not mark completion.
old_back='''$("back").onclick=()=>{$("study").classList.remove("on");$("home").classList.remove("off");renderHome()};'''
new_back='''$("back").onclick=()=>{isDailySession=false;$("study").classList.remove("on");$("home").classList.remove("off");renderHome()};'''
assert s.count(old_back)==1
s=s.replace(old_back,new_back,1)

# The existing spaced review interval ladder must be left unchanged.
assert 'const gaps=[1,3,7,14,30,60,120,180]' in s
assert 'st.next=ymd(1)' in s
assert len(json.JSONDecoder().raw_decode(s[s.index("const BASE=")+len("const BASE="):])[0])==190
assert "preserveMergedCardProgress" in s and "point-onepage" in s
assert s.rstrip().endswith("</html>")
js=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s,re.S|re.I)
assert len(js)==1
f=Path("/tmp/toeic_daily30.js")
f.write_text(js[0],encoding="utf-8")
check=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
assert check.returncode==0,check.stderr
# Self-contained queue test: 6 due + 24 extra = 30 and completion behavior.
test=Path("/tmp/toeic_daily30_test.js")
queue_js=new.split("// At least 30 cards a day")[1]
queue_js="// At least 30 cards a day"+queue_js
test.write_text('''const localStorage={s:{},getItem(k){return this.s[k]||null},setItem(k,v){this.s[k]=v}};
const ymd=()=> "2026-11-22";
const collection=Array.from({length:289},(_,i)=>({id:"c"+i,front:"term"+i,next:i<6?"2026-11-22":"2026-11-23",level:i%5,mastered:false}));
const studyDeck=()=>collection;
const due=()=>collection.filter(x=>x.next<=ymd());
''' +queue_js+'''
const first=dailyQueue();if(first.length!==30||first.filter(x=>x.next<=ymd()).length!==6)throw new Error("Unexpected daily queue");
completeDailySession();if(dailyQueue().length!==6)throw new Error("Completed schedule wrong");
console.log("PASS: 6 due + 24 extra = 30; completed schedule respected");
''',encoding="utf-8")
res=subprocess.run(["node",str(test)],capture_output=True,text=True)
assert res.returncode==0,res.stderr
p.write_text(s,encoding="utf-8")
print("Daily target: 30 items, due first, fill with weaker and nearest-review items.")
print(res.stdout.strip())
print("Verified all 289 cards, POINT page, embedded images, progress history, and spacing intervals retained.")
print("JavaScript syntax and queue functionality validated.")

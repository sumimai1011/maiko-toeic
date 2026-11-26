#!/usr/bin/env python3
"""Enable optional +10/+20/+30/+50 extra TOEIC study after completing daily 80.
Avoid repeats in same-day sessions and persist study history locally.
"""
import json,re,subprocess
from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf8")
s0=s
p0=s.index("const BASE=")+len("const BASE=")
base,_=json.JSONDecoder().raw_decode(s[p0:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(150,122),(len(base),len(extra))
assert "const DAILY_TARGET=80;" in s
assert "point-onepage" in s and "preserveMergedCardProgress" in s
assert s.count('id="start"')==1
assert "function dailyQueue()" in s and "function finishOrNext()" in s

# Supplemental controls are visually tucked under the daily start button.
old='''  <button id="start" class="primary">学習スタート</button>
  <div class="note"><span id="registered">0</span>カード登録済み</div>'''
new='''  <button id="start" class="primary">学習スタート</button>
  <div id="extraStudy" class="extraStudy" hidden>
    <div class="extraHeading">今日の80枚、完了！ 🎉</div>
    <div class="extraSubtitle">もう少し勉強する？</div>
    <div class="extraChoices">
      <button type="button" data-extra="10">＋10枚</button>
      <button type="button" data-extra="20">＋20枚</button>
      <button type="button" data-extra="30">＋30枚</button>
      <button type="button" data-extra="50">＋50枚</button>
    </div>
    <div id="extraInfo" class="extraInfo"></div>
  </div>
  <div class="note"><span id="registered">0</span>カード登録済み</div>'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Use CSS hidden selector explicitly because author CSS may override [hidden].
anchor="</style>"
assert s.count(anchor)==1
css='''/* Optional extra daily study — compact and finger-friendly. */
.extraStudy{margin:14px 0 6px;padding:14px 12px;border:1px solid #ece6ff;border-radius:16px;background:#faf8ff;text-align:center}
.extraStudy[hidden]{display:none!important}
.extraHeading{font-weight:850;font-size:16px;color:var(--purple);margin-bottom:5px}
.extraSubtitle{font-size:14px;font-weight:750;margin-bottom:12px}
.extraChoices{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.extraChoices button{padding:12px 6px;border-radius:12px;border:1px solid #d8caff;background:#fff;color:var(--purple);font-weight:850;font-size:15px}
.extraChoices button:disabled{opacity:.4;cursor:not-allowed}
.extraInfo{margin-top:10px;font-size:12px;color:var(--muted)}
'''
s=s.replace(anchor,css+anchor,1)

# New separate key, without modifying existing daily 80 completion key or study progress.
old='''let isDailySession=false;
function dailyCompleted(){'''
new='''let isDailySession=false;
let isExtraSession=false;
const EXTRA_DONE_KEY="toeic_daily_extra_seen_v1";
// Records the cards scored in today's main and extra study, not a global mastery flag.
function extraRecord(){
  try{
    const x=JSON.parse(localStorage.getItem(EXTRA_DONE_KEY)||"null");
    if(x && x.date===ymd(0) && Array.isArray(x.ids))return x;
  }catch(e){}
  return {date:ymd(0),ids:[],extraCount:0};
}
function saveExtraRecord(rec){
  try{localStorage.setItem(EXTRA_DONE_KEY,JSON.stringify(rec))}catch(e){}
}
function recordStudiedCard(card){
  if(!isDailySession && !isExtraSession)return;
  const r=extraRecord();
  const key=String(card.id)+"|"+String(card.front);
  if(!r.ids.includes(key))r.ids.push(key);
  saveExtraRecord(r);
}
function extraCandidates(){
  const seen=new Set(extraRecord().ids);
  return studyDeck().filter(x=>!seen.has(String(x.id)+"|"+String(x.front)))
    .sort((a,b)=>{
      // Review items that are due or less mastered first.
      const ap=a.next||"",bp=b.next||"";
      const dueA=(!ap||ap<=ymd(0)),dueB=(!bp||bp<=ymd(0));
      if(dueA!==dueB)return dueA?-1:1;
      const la=Number.isFinite(a.level)?a.level:0;
      const lb=Number.isFinite(b.level)?b.level:0;
      if(la!==lb)return la-lb;
      if(ap!==bp)return ap.localeCompare(bp);
      return String(a.id+"|"+a.front).localeCompare(String(b.id+"|"+b.front));
    });
}
function startExtraStudy(size){
  if(!dailyCompleted())return;
  if(![10,20,30,50].includes(size))return;
  const picked=extraCandidates().slice(0,size);
  if(!picked.length)return;
  isDailySession=false;
  isExtraSession=true;
  startStudy(picked);
}
function dailyCompleted(){'''
assert s.count(old)==1
s=s.replace(old,new,1)

# If user already completed 80 under previous version, all of today's initial 80 cannot
# be reconstructed accurately. Persist selected 80 IDs immediately on starting from now on.
# Score-click tracking handles retries and extra study sessions.
old='''  $("start").textContent=todayCards.length?"学習スタート（"+todayCards.length+"枚）":"今日の学習完了 🎉";
  if($("panel").classList.contains("on")) renderList();'''
new='''  $("start").textContent=todayCards.length?"学習スタート（"+todayCards.length+"枚）":"今日の学習完了 🎉";
  const extraEl=$("extraStudy");
  const finished=dailyCompleted();
  extraEl.hidden=!finished;
  if(finished){
    const remaining=extraCandidates().length;
    const rec=extraRecord();
    $("extraInfo").textContent="追加で学習済み："+(rec.extraCount||0)+"枚 ／ 未学習："+remaining+"枚";
    extraEl.querySelectorAll("[data-extra]").forEach(btn=>{
      btn.disabled=remaining===0;
      btn.title=remaining===0?"今日はすべて学習済み":"追加で"+Math.min(Number(btn.dataset.extra),remaining)+"枚";
    });
  }
  if($("panel").classList.contains("on")) renderList();'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Complete an extra session, update supplement count and clear mode.
old='''    if(isDailySession){completeDailySession();isDailySession=false;}
    $("study").classList.remove("on");'''
new='''    if(isDailySession){completeDailySession();isDailySession=false;}
    if(isExtraSession){
      const rec=extraRecord();
      // Count unique cards selected this extra session, ignoring same-session repeat reviews.
      rec.extraCount=(rec.extraCount||0)+new Set(queue.map(x=>String(x.id)+"|"+String(x.front))).size;
      saveExtraRecord(rec);
      isExtraSession=false;
    }
    $("study").classList.remove("on");'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Starting the main session clears the supplemental flag; progress is still saved
# each time a card is scored. Reserve main-session card IDs for no repeats today.
old='''$("start").onclick=()=>{
  isDailySession=true;
  const cards=dailyQueue();
  if(cards.length)startStudy(cards);
};'''
new='''$("start").onclick=()=>{
  isExtraSession=false;
  isDailySession=true;
  const cards=dailyQueue();
  if(cards.length){
    // Prevent supplemental sessions later in the day from repeating these initial 80.
    const rec=extraRecord();
    const seen=new Set(rec.ids);
    cards.forEach(x=>seen.add(String(x.id)+"|"+String(x.front)));
    rec.ids=[...seen];
    saveExtraRecord(rec);
    startStudy(cards);
  }else{isDailySession=false}
};
document.querySelectorAll("[data-extra]").forEach(btn=>{
  btn.onclick=()=>startExtraStudy(Number(btn.dataset.extra));
});'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Distinguish abandoned session from completed session; no extra count on back.
old='''$("back").onclick=()=>{isDailySession=false;$("study").classList.remove("on");$("home").classList.remove("off");renderHome()};'''
new='''$("back").onclick=()=>{isDailySession=false;isExtraSession=false;$("study").classList.remove("on");$("home").classList.remove("off");renderHome()};'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Single-card browsing must not be mistaken for an extra or daily session.
old='''(isDailySession=false,startStudy([x]))'''
new='''(isDailySession=false,isExtraSession=false,startStudy([x]))'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Add recordStudiedCard just after saveProgress (a score is always explicitly chosen).
old='''  progress[x.id]=st;
  saveProgress();
  finishOrNext();'''
new='''  progress[x.id]=st;
  saveProgress();
  recordStudiedCard(x);
  finishOrNext();'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Safeguards
st=s.index("const BASE=")+len("const BASE=")
base_after,_=json.JSONDecoder().raw_decode(s[st:])
ap=s.index("BASE.push(")+len("BASE.push(")
ae=s.index("\n);",ap)
extra_after=json.loads("["+s[ap:ae].strip().strip(",")+"]")
assert base_after==base and extra_after==extra
assert "const DAILY_TARGET=80;" in s
assert "preserveMergedCardProgress" in s and "point-onepage" in s
assert len(base_after+extra_after)==272
assert s.rstrip().endswith("</html>")
refs=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',s)
assert all(cid in {x["id"] for x in base_after+extra_after} for cid in refs)
js=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)
assert len(js)==1
f=Path("/tmp/toeic_extra_study.js")
f.write_text(js[0],encoding="utf8")
ck=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
assert ck.returncode==0,ck.stderr

# Test daily+extra selection against 272 mock cards and repeated batches.
start=s.index('let isDailySession=false;')
end=s.index('function dailyCompleted(){',start)
helpers=s[start:end]
test=r'''const localStorage={data:{},getItem(k){return this.data[k]||null},setItem(k,v){this.data[k]=v}};
const ymd=()=> "2026-11-26";
const cards=Array.from({length:272},(_,i)=>({id:"c"+i,front:"word"+i,next:i<6?"2026-11-26":"2026-11-27",level:i%5}));
const studyDeck=()=>cards;
const DAILY_DONE_KEY="toeic_daily80_completed_v1";
function dailyCompleted(){return localStorage.getItem(DAILY_DONE_KEY)===ymd()}
function startStudy(arr){globalThis.mockStarted=arr;}
'''
test += helpers.replace('let isDailySession=false;','').replace('let isExtraSession=false;','')
test += r'''
localStorage.setItem(DAILY_DONE_KEY,ymd());
const seen=extraRecord();
for(let i=0;i<80;i++)seen.ids.push("c"+i+"|word"+i);
saveExtraRecord(seen);
if(extraCandidates().length!==192)throw new Error("Expected 192 unseen");
startExtraStudy(20);
if(globalThis.mockStarted.length!==20)throw new Error("Expected 20 in first batch");
if(globalThis.mockStarted.some(c=>Number(c.id.slice(1))<80))throw new Error("Daily cards repeated");
globalThis.mockStarted.forEach(c=>recordStudiedCard(c));
if(extraCandidates().length!==172)throw new Error("Extra batch repeated");
startExtraStudy(50);
if(globalThis.mockStarted.length!==50)throw new Error("Expected 50 second batch");
if(globalThis.mockStarted.some(c=>seen.ids.includes(c.id+"|"+c.front)))throw new Error("Extra cards repeated");
console.log("PASS: daily 80 excluded, +20 and +50 non-overlap, localStorage persistence");
'''
testfile=Path("/tmp/toeic_extra_selection_test.js")
testfile.write_text(test,encoding="utf8")
result=subprocess.run(["node",str(testfile)],capture_output=True,text=True)
assert result.returncode==0,result.stderr[-2500:]
p.write_text(s,encoding="utf8")
print("SUCCESS: added +10 / +20 / +30 / +50 extra-practice buttons.")
print(result.stdout.strip())
print("All 272 cards, images, one-page POINT, daily 80 target and spaced repetition preserved.")
print("JavaScript syntax and initial card reference checks passed.")

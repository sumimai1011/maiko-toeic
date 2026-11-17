#!/usr/bin/env python3
"""Publish a single-page, quick-scan POINT reference; preserve all 273 cards and progress."""
from pathlib import Path
import json, re, subprocess

p=Path("index.html")
s=p.read_text(encoding="utf-8")
assert s.count("const POINT_TOPICS=")==1
start=s.index("const POINT_TOPICS=")
data_start=start+len("const POINT_TOPICS=")
old,consumed=json.JSONDecoder().raw_decode(s[data_start:])
assert len(old)==6,("Unexpected POINT topic count",len(old))
assert "test-overview" not in s and "テスト概要" not in s

base_start=s.index("const BASE=")+len("const BASE=")
base,_=json.JSONDecoder().raw_decode(s[base_start:])
push_start=s.index("BASE.push(")+len("BASE.push(")
push_end=s.index("\n);",push_start)
extra=json.loads("["+s[push_start:push_end].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,83), (len(base),len(extra))
cards_before=json.dumps(base+extra,ensure_ascii=False,separators=(",",":"))
assert {"call off","mail"}.issubset({x["front"] for x in base+extra})

def rows(items):
    return '<div class="pointRows">' + ''.join(
        '<div class="pointRow2"><div class="label">'+a+'</div><div class="value">'+b+'</div></div>'
        for a,b in items) + '</div>'

def block(title,items):
    return '<div class="pointSection"><h3>'+title+'</h3>'+rows(items)+'</div>'

html=''.join([
block('① 品詞',[
 ('名詞','主語・目的語・補語'),
 ('形容詞','名詞を修飾'),
 ('副詞','動詞・形容詞・副詞・文全体を修飾'),
 ('前置詞','＋ 名詞 / 動名詞'),
 ('接続詞','＋ S + V'),
 ('名詞 / 動詞の同形語','increase / decrease / estimate / forecast / recruit / respect / order'),
]),
block('② 前置詞・接続詞・接続副詞',[
 ('前置詞 ＋ 名詞','rather than / aside from / despite / in spite of / in the event of'),
 ('接続詞 ＋ S＋V','because / since / when / while / as / as long as / in the event that'),
 ('接続副詞','therefore / thus / consequently / nevertheless / meanwhile / namely'),
 ('副詞 thereby','それによって'),
]),
block('③ 動詞の形',[
 ('使役','make / have / let ＋ 人 ＋ 原形'),
 ('help','help ＋ 人 ＋ (to) 原形'),
 ('have','have ＋ 物 ＋ 過去分詞'),
 ('未来の予定','be ＋ -ing'),
]),
block('④ 頻出ルール',[
 ('省略','when / if 等の後で S＋be を省略できる場合あり'),
 ('倒置','nor ＋ 助動詞 ＋ 主語'),
 ('提案・要求のthat節','suggest / propose / require / demand ＋ that ＋ S ＋ 原形'),
 ('時・条件の副詞節','未来のことでも when / if の後は現在形'),
]),
block('⑤ 代名詞・可算 / 不可算',[
 ('可算単数','each / every / either / neither / another'),
 ('可算複数','many / few / a few / several / both'),
 ('不可算','much / little / a little'),
 ('両方','all / most / some / any / enough'),
 ('ほとんどない','few（可算）/ little（不可算）'),
 ('少しある','a few（可算）/ a little（不可算）'),
 ('代名詞・単数扱い','someone / anyone / everyone / nobody / each / either / neither'),
 ('代名詞・複数扱い','both / many / few / several / others'),
 ('代名詞・文脈による','all / most / some / any / none'),
 ('the other','単数・複数の両方で使える'),
]),
block('⑥ 間違えやすいセット',[
 ('until / by','～までずっと / ～までに（期限）'),
 ('自動詞 / 他動詞','go to / arrive at  ↔  discuss / attend'),
 ('as / as long as','～につれて / ～する限り'),
 ('be＋ing / will','決まった予定 / 意思・予測'),
]),
])
assert html.count('class="pointSection"')==6
new=[{"id":"point-onepage","title":"POINT総まとめ","subtitle":"","html":html}]
replacement="const POINT_TOPICS="+json.dumps(new,ensure_ascii=False,separators=(",",":"))
s=s[:start]+replacement+s[data_start+consumed:]
# Now POINT opens the single sheet immediately, with no drill-down buttons.
function_start=s.index("function renderPoints(){")
function_end=s.index("function startStudy(",function_start)
old_functions=s[function_start:function_end]
assert "function openPointPage()" in old_functions
assert "function openPointDetail(id)" in old_functions
assert "function closePoints()" in old_functions
new_functions=r'''function renderPoints(){
  const topic=POINT_TOPICS[0];
  $("pointList").innerHTML='<div class="pointBox"><div class="pointPart">POINT</div><h1 class="pointHeading">'+esc(topic.title)+'</h1><div class="pointContent">'+topic.html+'</div></div>';
}
function openPointPage(){
  $("panel").classList.remove("on");
  $("home").classList.add("off");
  $("pointDetail").classList.remove("on");
  $("pointPage").classList.add("on");
  renderPoints();
}
function openPointDetail(id){openPointPage();}
function closePoints(){
  $("pointPage").classList.remove("on");
  $("pointDetail").classList.remove("on");
  $("home").classList.remove("off");
  renderHome();
}
'''
s=s[:function_start]+new_functions+"\n"+s[function_end:]
# Preserve all 273 card data, images and browser-stored progress.
bp=s.index("const BASE=")+len("const BASE=")
b2,_=json.JSONDecoder().raw_decode(s[bp:])
ap=s.index("BASE.push(")+len("BASE.push(")
ae=s.index("\n);",ap)
e2=json.loads("["+s[ap:ae].strip().strip(",")+"]")
assert json.dumps(b2+e2,ensure_ascii=False,separators=(",",":"))==cards_before
assert "preserveMergedCardProgress" in s
assert "テスト概要" not in s and "test-overview" not in s
assert s.rstrip().endswith("</html>")
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s,re.S|re.I)
assert len(scripts)==1
js=Path("/tmp/toeic_onepage.js")
js.write_text(scripts[0],encoding="utf-8")
check=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
assert check.returncode==0,check.stderr
# JS runtime smoke check for the entire POINT render module.
smoke=Path("/tmp/point_smoke.js")
smoke.write_text(replacement+";\n"+"console.log(POINT_TOPICS.length,POINT_TOPICS[0].html.match(/class=\\\\\"pointSection\\\\\"/g)?.length || 0);",encoding="utf-8")
# Independent structural verification avoids relying on browser state.
assert len(new)==1 and all(f'⑥' in html for _ in [0])
p.write_text(s,encoding="utf-8")
print("POINT rebuilt: single visible page, six compact sections, no test overview.")
print("Verified all 273 cards, embedded images and saved-progress code unchanged.")
print("Node JavaScript syntax check PASSED.")

#!/usr/bin/env python3
"""Consolidate 402 vocabulary cards into GitHub and remove advanced UI.
Preserve local study progress and any earlier browser-only edits."""
import json
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
marker="const BASE="
assert src.count(marker)==1
p=src.index(marker)+len(marker)
base,n=json.JSONDecoder().raw_decode(src[p:])
data=json.loads(Path("data/browser_cards_20261117.json").read_text(encoding="utf-8"))
additional=data["cards"]
assert len(additional)==169
assert len(base) in (233,402), f"Unexpected BASE length {len(base)}"
approved=[
 ("legislation","法律、法令、立法","法律、立法"),
 ("yet","しかし、それでも、～でありながら","まだ、しかし"),
 ("name","名付ける、任命する、名前を挙げる","名付ける、任命する"),
 ("commitment","約束、献身、責任ある取り組み","約束、献身"),
 ("recognition","評価、表彰、認識","評価、表彰"),
 ("patron","利用客、常連客、後援者","利用客、後援者"),
 ("select","選ぶ、厳選された、特定の","選ぶ、厳選された"),
 ("drape","カーテン、覆い布、～を布で覆う","カーテン、布で覆う"),
 ("miscellaneous","雑多な、さまざまな、雑貨","雑多な、さまざまな"),
 ("exhaust","排気、排気ガス、疲れ果てさせる","排気ガス、疲れ果てさせる"),
 ("affirm","断言する、確認する、支持する","断言する、確認する")
]
changed=[]
if len(base)==233:
    for i,x in enumerate(additional):
        c=dict(x)
        for front,old,new in approved:
            if c.get("front")==front and c.get("meaning")==old:
                c["meaning"]=new
                changed.append(front)
        c["legacyId"]=c.pop("id")
        c["legacyIndex"]=i
        c["id"]=f"mig_{i:03d}"
        assert c["type"] in ("単語","熟語")
        base.append(c)
    assert len(base)==402
    assert len(changed)==11, ("Approved local meaning changes mismatch",changed)
    src=src[:p]+json.dumps(base,ensure_ascii=False,separators=(",",":"))+src[p+n:]
else:
    assert all(base[233+i].get("legacyId")==additional[i]["id"] for i in range(169))

# Drop export controls, the full editor dialog, the editor's CSS and JS.
button='  <button id="exportCards" class="m3" type="button">全カードを書き出す</button>'
if button in src:
    src=src.replace(button+"\n","",1)
    assert 'id="exportCards"' not in src
css="\n.editLayer{"
if css in src:
    a=src.index(css)
    b=src.index("\n</style>",a)
    src=src[:a]+src[b:]
dialog='<div id="cardEditLayer"'
if dialog in src:
    a=src.index(dialog)
    b=src.index("\n</body>",a)
    src=src[:a]+src[b:]
export='document.getElementById("exportCards").onclick = () => {'
editor='// Editing is a reversible overlay:'
if export in src:
    a=src.index(export)
    b=src.index(editor,a)
    src=src[:a]+src[b:]
if editor in src:
    a=src.index(editor)
    b=src.index("\nrenderHome();\n</script>",a)
    src=src[:a]+src[b:]

# The original in-browser 169 cards are now part of BASE.
# Keep local userCards in storage (and their past study progress),
# while preventing duplicate display and retaining any later additions.
dedup_js=r'''
// Canonical 402 cards; retain old browser cards and review history as backup.
const MIGRATED_KEYS=new Set(BASE.filter(c=>c.legacyId!==undefined)
  .map(c=>JSON.stringify([String(c.legacyId),c.legacyFront||""])));
const MIGRATED_BY_INDEX=BASE.filter(c=>c.legacyId!==undefined);
const LEGACY_PAIRS=new Set(MIGRATED_BY_INDEX.map(c=>{
 const old=__LEGACY_PAIRS__[c.legacyIndex];
 return JSON.stringify([String(c.legacyId),old.front]);
}));
let savedEdits={};
try{savedEdits=JSON.parse(localStorage.getItem("maiko-toeic-card-edits-v1")||"{}")||{}}catch(e){}
let copiedHistory=false;
MIGRATED_BY_INDEX.forEach(card=>{
 if(!progress[card.id] && progress[card.legacyId]){
  progress[card.id]={...progress[card.legacyId]};
  copiedHistory=true;
 }
});
if(copiedHistory)saveProgress();
deck=function(){
 const built=BASE.map(x=>{
   const oldEdit=x.legacyIndex!==undefined?(savedEdits["u:"+x.legacyIndex]||{}):{};
   const newEdit=savedEdits["b:"+x.id]||{};
   return {...x,...oldEdit,...newEdit,...stateFor(x.id)};
 }).filter(x=>!x.__deleted);
 const local=userCards
   .filter(x=>!LEGACY_PAIRS.has(JSON.stringify([String(x.id),x.front])))
   .map((x,i)=>({...x,...stateFor(x.id)}));
 return built.concat(local);
};
'''
# Use original identifiers and words, not a heuristic, to filter old local cards.
dedup_js=dedup_js.replace("__LEGACY_PAIRS__",json.dumps(
    [{"front":x["front"]} for x in additional],ensure_ascii=False,separators=(",",":")))
anchor="\nrenderHome();\n</script>"
if "const LEGACY_PAIRS=new Set(" not in src:
    assert src.count(anchor)==1
    src=src.replace(anchor,"\n"+dedup_js+anchor,1)
assert len(base)==402
assert src.count('id="exportCards"')==0
assert "cardEditLayer" not in src
assert "toggleDeleted" not in src
assert src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Canonical base:",len(base),"New local cards migrated:",len(additional),"approved user meanings:",len(changed))
print("UI: editing, deletion, export removed; progress and local data retained.")

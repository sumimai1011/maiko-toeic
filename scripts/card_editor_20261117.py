#!/usr/bin/env python3
"""Add reversible edit/delete UI and approved Japanese-meaning simplifications.
Never replace userCards or their study progress in localStorage."""
import json
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1
p=src.index("const BASE=")+len("const BASE=")
cards,used=json.JSONDecoder().raw_decode(src[p:])
assert len(cards)==233, f"Unexpected built-in count: {len(cards)}"
approved=[
 ("since","～以来、～なので、それ以来","～以来、～なので"),
 ("dedication","献身、熱意／落成式","献身、熱意"),
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
 ("affirm","断言する、確認する、支持する","断言する、確認する"),
 ("object","物・対象・目的語","物、目的語")
]
replaced=[]
for c in cards:
 for front,old,new in approved:
  if c.get("front")==front and (c.get("meaning")==old or (front=="since" and c.get("meaning")=="それ以来")):
   c["meaning"]=new
   replaced.append(front)
assert sorted(replaced)==sorted(["since","dedication","object"]), replaced
new_json=json.dumps(cards,ensure_ascii=False,separators=(",",":"))
src=src[:p]+new_json+src[p+used:]
if "maiko-toeic-card-edits-v1" in src:
 print("Editing capability already installed")
else:
 assert src.count("</style>")==1
 css="""
.editLayer{display:none;position:fixed;inset:0;z-index:1000;background:#14142791;padding:18px;align-items:center;justify-content:center}
.editLayer.open{display:flex}
.editSheet{width:min(100%,540px);max-height:90vh;overflow:auto;background:white;border-radius:18px;padding:22px;box-shadow:0 16px 55px #0003}
.editSheet h3{margin:0 0 14px}
.editSheet label{display:block;font-size:13px;font-weight:800;margin:12px 0 4px}
.editSheet input,.editSheet textarea,.editSheet select{width:100%;border:1px solid #ddd8e5;border-radius:10px;padding:10px;background:#fff;color:#232333}
.editSheet textarea{min-height:72px;resize:vertical}
.editActions{display:flex;gap:10px;margin-top:18px}
.editActions button{flex:1;border:0;border-radius:12px;padding:12px;font-weight:800}
.editSave{background:#8872e8;color:white}
.editCancel{background:#efedf2}
.cardActions{display:flex;gap:8px;flex-shrink:0;margin-left:10px;align-items:center}
.cardActions button{border:1px solid #e6e0ed;background:white;color:#565068;border-radius:9px;padding:7px 9px;font-size:12px;font-weight:750}
.cardActions button.cardDelete{color:#b33f51;border-color:#f3d9df}
#toggleDeleted{border:0;background:#f1edf8;color:#625a76;border-radius:9px;padding:7px 10px;font-size:12px;font-weight:700;margin-left:10px}
@media(max-width:420px){.cardActions{flex-direction:column}.cardActions button{padding:4px 7px}.editSheet{padding:16px}}
"""
 src=src.replace("</style>",css+"\n</style>",1)
 layer="""
<div id="cardEditLayer" class="editLayer" role="dialog" aria-modal="true" aria-label="カードを編集">
 <div class="editSheet">
  <h3>カードを編集</h3>
  <label for="cardEditType">種類</label><select id="cardEditType"><option>単語</option><option>熟語</option><option>POINT</option></select>
  <label for="cardEditFront">英語・熟語</label><input id="cardEditFront">
  <label for="cardEditMeaning">日本語の意味</label><textarea id="cardEditMeaning"></textarea>
  <label for="cardEditExample">例文（任意）</label><textarea id="cardEditExample"></textarea>
  <div class="editActions"><button type="button" id="cardEditCancel" class="editCancel">キャンセル</button><button type="button" id="cardEditSave" class="editSave">保存する</button></div>
 </div>
</div>
"""
 assert src.count("</body>")==1
 src=src.replace("</body>",layer+"\n</body>",1)
 script="""
// Editing is a reversible overlay: built-in cards, pictures, original local
// userCards, and study histories are never deleted or overwritten.
const EDIT_STORE_KEY="maiko-toeic-card-edits-v1";
let cardEdits={};
try{cardEdits=JSON.parse(localStorage.getItem(EDIT_STORE_KEY)||"{}")||{}}catch(e){cardEdits={}}
const MEANING_MIGRATIONS=__MIGRATIONS__;
function writeEdits(next){
 try{localStorage.setItem(EDIT_STORE_KEY,JSON.stringify(next));cardEdits=next;return true}
 catch(e){alert("保存できませんでした。ブラウザの空き容量を確認してください。");return false}
}
// The 11 approved meanings stored in the user's browser are migrated once,
// only when their original wording still matches. Never change a custom edit.
(function migrateMeanings(){
 let updated={...cardEdits};
 userCards.forEach((card,index)=>{
  const change=MEANING_MIGRATIONS.find(t=>t[0]===card.front&&t[1]===card.meaning);
  const key="u:"+index;
  if(change && !Object.prototype.hasOwnProperty.call(updated,key)){
   updated[key]={meaning:change[2]};
  }
 });
 if(JSON.stringify(updated)!==JSON.stringify(cardEdits))writeEdits(updated);
})();
function allStoredCards(){
 const built=BASE.map(c=>{
  const key="b:"+c.id;
  return {...c,...(cardEdits[key]||{}),...stateFor(c.id),__editKey:key};
 });
 const user=userCards.map((c,i)=>{
  const key="u:"+i;
  return {...c,...(cardEdits[key]||{}),...stateFor(c.id),__editKey:key};
 });
 return built.concat(user);
}
deck=function(){return allStoredCards().filter(c=>!c.__deleted)};
let listDeletedMode=false;
let activeEditKey=null;
function closeCardEditor(){
 $("cardEditLayer").classList.remove("open");
 activeEditKey=null;
}
function openCardEditor(key){
 const card=allStoredCards().find(x=>x.__editKey===key);
 if(!card)return;
 activeEditKey=key;
 $("cardEditType").value=card.type;
 $("cardEditFront").value=card.front||"";
 $("cardEditMeaning").value=card.meaning||"";
 $("cardEditExample").value=card.example||"";
 $("cardEditLayer").classList.add("open");
 $("cardEditFront").focus();
}
$("cardEditCancel").onclick=closeCardEditor;
$("cardEditLayer").addEventListener("click",e=>{if(e.target===$("cardEditLayer"))closeCardEditor()});
$("cardEditSave").onclick=()=>{
 if(!activeEditKey)return;
 const front=$("cardEditFront").value.trim();
 const meaning=$("cardEditMeaning").value.trim();
 if(!front||!meaning){alert("英語と日本語訳を入力してください。");return}
 const patch={...(cardEdits[activeEditKey]||{}),type:$("cardEditType").value,
  front,meaning,example:$("cardEditExample").value.trim()};
 if(writeEdits({...cardEdits,[activeEditKey]:patch})){
  closeCardEditor();renderHome();renderList();
 }
};
function deleteOrRestoreCard(card){
 const isDeleted=!!card.__deleted;
 if(!isDeleted&&!confirm("「"+card.front+"」を削除しますか？\\n削除済み一覧から元に戻せます。"))return;
 const key=card.__editKey;
 const patch={...(cardEdits[key]||{}),__deleted:!isDeleted};
 if(writeEdits({...cardEdits,[key]:patch})){renderHome();renderList()}
}
const deletedToggle=document.createElement("button");
deletedToggle.id="toggleDeleted";deletedToggle.type="button";
deletedToggle.onclick=()=>{listDeletedMode=!listDeletedMode;renderList()};
$("panelCount").insertAdjacentElement("afterend",deletedToggle);
renderList=function(){
 const query=$("search").value.trim().toLowerCase();
 const source=listDeletedMode?allStoredCards().filter(x=>x.__deleted):studyDeck();
 const list=source.filter(x=>listMode==="all"||x.image)
  .filter(x=>!query||(x.front+" "+x.meaning).toLowerCase().includes(query));
 $("panelTitle").textContent=listDeletedMode?"削除済みカード":(listMode==="image"?"語呂画像つき":"カード一覧");
 $("panelCount").textContent=list.length+"件";
 deletedToggle.textContent=listDeletedMode?"カード一覧へ戻る":"削除済み";
 $("list").innerHTML=list.map(x=>{
  const adj=["costly","lively","timely"].includes(x.front.toLowerCase())?"　※形容詞（副詞ではない）":"";
  return '<div class="row"><div class="rt"><div class="word">'+esc(x.front)+
   '</div><div class="meaning">'+esc(x.meaning)+adj+
   '</div></div><div class="cardActions">'+
   (listDeletedMode?'': '<button type="button" class="cardEdit">編集</button>')+
   '<button type="button" class="cardDelete">'+(listDeletedMode?'元に戻す':'削除')+
   '</button></div></div>';
 }).join("");
 Array.from($("list").querySelectorAll(".row")).forEach((row,i)=>{
  const card=list[i];
  row.onclick=()=>{if(!listDeletedMode)startStudy([card])};
  const edit=row.querySelector(".cardEdit");
  if(edit)edit.onclick=e=>{e.stopPropagation();openCardEditor(card.__editKey)};
  row.querySelector(".cardDelete").onclick=e=>{e.stopPropagation();deleteOrRestoreCard(card)};
 });
};
"""
 script=script.replace("__MIGRATIONS__",json.dumps(approved,ensure_ascii=False))
 assert src.count("\n</script>\n")==1, "Unexpected script location"
 src=src.replace("\n</script>\n","\n"+script+"\nrenderHome();\n</script>\n",1)
 assert "function renderList()" in src and "function allStoredCards()" in src
 path.write_text(src,encoding="utf-8")
 print("Installed editable & reversible card management UI.")
print("Embedded cards:",len(cards),"bulk-approved meanings in BASE:",replaced)

#!/usr/bin/env python3
"""Apply user-approved card cleanup; consolidate 4 pairs; improve meanings/examples; add 5 cards."""
import json,re,subprocess
from pathlib import Path
config=json.loads("{\"deletes\":[\"resolutely\",\"supplement\",\"in a timely manner\",\"as early as\",\"exceed expectations\",\"leave of absence\",\"respondent\",\"successor\",\"dues\",\"promote / advance\",\"leave O C\",\"retrieve\",\"sublet\",\"prospective\",\"sales projection\",\"favorable\",\"demand exceeds production\",\"exhaust system\",\"store-wide\",\"take note\",\"mail\",\"name\",\"patron\",\"booklet\",\"sanctuary\",\"recipient\",\"along the way\",\"rest assured\",\"skyline\",\"lawn\",\"lawn mower\",\"in action\",\"shoreline\",\"all / no / most + 複数名詞\",\"several / many / few + 複数名詞\",\"reception\",\"a deal valued at X\",\"deal value\",\"oneself\",\"one of the + 最上級 + 複数名詞\"],\"merge\":[[\"as of\",\"as of today\"],[\"acquaint A with B\",\"be acquainted with ～\"],[\"company directory\",\"directory\"],[\"implement\",\"will be implemented\"]],\"meaning\":{\"inaugural\":\"初開催の\",\"entail\":\"～を伴う\",\"preliminary\":\"予備の\",\"represent\":\"～を代表する\",\"practices\":\"慣行\",\"go out of business\":\"廃業する\",\"in accordance with\":\"～に従って\",\"turn A around\":\"Aを立て直す\",\"proceed with\":\"～を進める\",\"look into\":\"～を調べる\",\"set forth\":\"明記する\",\"on one's behalf\":\"～の代わりに\",\"deliberate\":\"故意の\",\"prestigious\":\"名門の\",\"provision\":\"規定\",\"reservation\":\"懸念\",\"bolster\":\"強化する\",\"retain\":\"維持する\",\"adequate\":\"十分な\",\"implication\":\"影響\",\"conserve\":\"節約する\",\"scrape\":\"削る\",\"conform\":\"従う\",\"objection\":\"反対\",\"stellar\":\"非常に優れた\",\"advise 人 of ~\":\"人に～を知らせる\",\"cordially\":\"丁重に\",\"pothole\":\"道路の穴\",\"be praised for ~ing\":\"～したことで称賛される\",\"delegate A to B\":\"AをBに委任する\",\"a wealth of\":\"豊富な\",\"differentiate\":\"区別する\",\"verify\":\"確認する\",\"subsequent\":\"その後の\",\"reconcile\":\"照合する\",\"scrutinize\":\"精査する\",\"substantiate\":\"裏付ける\",\"public official\":\"公務員\",\"dedication\":\"献身\",\"quite a bit\":\"かなり\",\"in light of ～\":\"～を考慮して\",\"legislation\":\"法律\",\"restoration\":\"修復\",\"disruption\":\"混乱\",\"stringent\":\"厳格な\",\"be committed to ~ing\":\"～することに尽力している\",\"recognition\":\"表彰\",\"subordinate\":\"部下\",\"impending\":\"差し迫った\",\"streamline\":\"効率化する\",\"thereby\":\"それによって\",\"draw near\":\"近づく\",\"qualify for A\":\"Aの資格を得る\",\"culinary\":\"料理の\",\"finish off\":\"仕上げる\",\"layover\":\"乗り継ぎの待ち時間\",\"affirm\":\"確認する\",\"as per\":\"～のとおり\",\"boast of\":\"～を誇る\",\"stand out from\":\"～より目立つ\",\"solely\":\"～だけ\",\"from then on\":\"それ以降\",\"formulate\":\"策定する\",\"narrative\":\"物語\",\"the broadest possible audience\":\"できるだけ幅広い観客\",\"set aside\":\"確保する\",\"hire a service\":\"業務を委託する\",\"identifiable\":\"識別できる\",\"distinctive\":\"特徴的な\",\"theatrical\":\"演劇の\",\"substantially\":\"大幅に\",\"utility costs\":\"光熱費\",\"conventionally\":\"従来の方法で\",\"valuation\":\"評価\",\"imperfection\":\"欠陥\",\"pertain to\":\"～に関係する\",\"assume\":\"引き受ける／～と仮定する\"},\"examples\":{\"advise A to do\":\"The manager advised us to submit the report early.\",\"ensure that ~\":\"Please ensure that all documents are complete.\",\"assure 人 that ~\":\"I assure you that the shipment will arrive tomorrow.\",\"be praised for ~ing\":\"She was praised for improving customer service.\",\"delegate A to B\":\"The manager delegated the task to her assistant.\",\"pay off\":\"Our hard work finally paid off.\",\"be serviced\":\"The equipment will be serviced next week.\",\"report to work\":\"Employees must report to work by 9 a.m.\",\"without written consent from ~\":\"Do not share the data without written consent from the client.\",\"so + 形容詞/副詞 + as to do\":\"The instructions are so clear as to prevent errors.\",\"decline\":\"Sales declined slightly last quarter.\",\"vicinity\":\"There are several hotels in the vicinity.\",\"correspondent\":\"The correspondent reported from the conference.\",\"liability\":\"The company accepted liability for the damage.\",\"omission\":\"The omission was corrected before publication.\",\"assess\":\"We will assess the project results next month.\",\"viability\":\"The team is reviewing the project's viability.\",\"specialize in ～\":\"Our firm specializes in software development.\",\"astound\":\"The final results astounded the researchers.\",\"affordability\":\"The affordability of the service attracts customers.\",\"stranded\":\"Passengers were stranded at the airport.\",\"address\":\"The director will address the staff tomorrow.\",\"comply with ～\":\"All employees must comply with the safety rules.\",\"whereas\":\"Sales grew in Japan, whereas they fell overseas.\",\"veterinary\":\"She works at a veterinary clinic.\",\"have yet to do\":\"We have yet to receive the invoice.\",\"foreman\":\"The foreman inspected the construction site.\",\"qualify for A\":\"You may qualify for a discount.\",\"be comprised of\":\"The committee is comprised of six members.\",\"culinary\":\"The hotel offers culinary training.\",\"settle the payment\":\"Please settle the payment by Friday.\",\"take down\":\"Please take down the notice after the event.\",\"pass on\":\"Please pass on the message to the team.\",\"finish off\":\"We need to finish off the report today.\",\"fairly\":\"The process is fairly simple.\",\"function\":\"This device has a useful function.\",\"scuff\":\"There was a scuff on the new floor.\",\"edge\":\"Our service gives us an edge over competitors.\",\"layover\":\"We have a two-hour layover in Singapore.\",\"in reference to\":\"I am writing in reference to your inquiry.\",\"pavilion\":\"Visitors gathered at the exhibition pavilion.\",\"affirm\":\"The report affirms the company's commitment.\",\"as per\":\"As per your request, the documents are attached.\",\"revel in\":\"The team reveled in its success.\",\"boast of\":\"The hotel boasts of excellent service.\",\"hand out\":\"Please hand out the brochures.\",\"commemorate\":\"The ceremony will commemorate the anniversary.\",\"stand out from\":\"Our design stands out from competing products.\",\"solely\":\"This decision was made solely for safety reasons.\",\"scientific community\":\"The discovery attracted the scientific community.\",\"sought\":\"The company sought additional funding.\",\"from then on\":\"From then on, the team met weekly.\",\"formulate\":\"The committee will formulate a new policy.\",\"handout\":\"Please read the handout before the meeting.\",\"avid\":\"She is an avid reader of industry reports.\",\"mint\":\"The used equipment is still in mint condition.\",\"pest\":\"A pest inspection is scheduled for Monday.\",\"state a complaint\":\"Customers may state a complaint by email.\",\"at all costs\":\"We must avoid delays at all costs.\",\"hygiene\":\"Good hygiene is essential in food production.\",\"halt\":\"The company decided to halt production.\",\"aforementioned\":\"Please review the aforementioned documents.\",\"placement\":\"The agency provides job placement services.\",\"narrative\":\"The report presents a clear narrative of events.\",\"blackout\":\"The blackout affected several offices.\",\"outage\":\"The network outage lasted two hours.\",\"surge\":\"The company saw a surge in online orders.\",\"scaffolding\":\"Workers installed scaffolding around the building.\",\"bus depot\":\"The new bus depot will open next month.\",\"at a later date\":\"We will discuss this at a later date.\",\"That's not necessarily the case.\":\"That's not necessarily the case for every department.\",\"civil engineering\":\"She studied civil engineering at university.\",\"state-of-the-art\":\"The factory uses state-of-the-art equipment.\",\"faculty\":\"The faculty attended the university meeting.\",\"festivity\":\"The annual festivity attracted many visitors.\",\"as of\":\"As of today, the new policy is in effect.\",\"acquaint A with B\":\"The trainer acquainted new staff with the procedures. She is acquainted with the process.\",\"company directory\":\"Please check the company directory for the extension number.\",\"implement\":\"We will implement the policy next month. The policy will be implemented next month.\",\"constructive\":\"We welcome constructive feedback from clients.\",\"all / no / most + 複数名詞\":\"All cars are parked outside.\",\"several / many / few + 複数名詞\":\"Several cars are parked outside.\",\"have since been\":\"Several changes have since been made to the policy.\",\"invite A to B for C\":\"We invited the client to the office for a meeting.\",\"reception\":\"The reception will begin at six.\",\"valuation\":\"The valuation was completed yesterday.\",\"secure\":\"We need to secure additional funding.\",\"though (they are) promising\":\"Though promising, the proposal requires further review.\",\"a deal valued at X\":\"The firm announced a deal valued at $2 million.\",\"deal value\":\"The deal value was reported as $2 million.\",\"imperfection\":\"The inspector noticed an imperfection.\",\"pertain to\":\"The new rules pertain to all employees.\",\"oneself\":\"She completed the task herself.\",\"trade show\":\"We will attend the trade show next week.\",\"be pertinent to\":\"These figures are pertinent to our discussion.\",\"one of the + 最上級 + 複数名詞\":\"This is one of the largest factories in the region.\",\"overwhelming\":\"The response was overwhelming.\",\"demolition\":\"The demolition is scheduled for next month.\",\"with the exception of\":\"Everyone attended with the exception of the director.\",\"be slated for\":\"The launch is slated for next week.\",\"table of contents\":\"The table of contents lists every chapter.\",\"acknowledgements\":\"She thanked her team in the acknowledgements.\"},\"mnemonics\":[[\"①咲いた咲いたの音楽で♪\\nall, no, most♪several, many , few cars♪\",\"可算複数名詞の前に置く語\",\"All cars are ready for delivery.\"],[\"②a deal (which was) valued at X：Xの価値がある取引\\n a deal value of 金額：(金額)の取引\",\"取引の金額を表す2つの言い方\",\"The company announced a deal valued at $5 million.\"],[\"③主語＋動詞＋○○self：自ら～する\",\"再帰代名詞で「自ら」\",\"The director herself approved the plan.\"],[\"④one of the 最上級＋複数名詞＝among the 最上級＋複数名詞\",\"最も～なものの一つ\",\"This is one of the best products on the market.\"]]}")
p=Path("index.html")
s=p.read_text(encoding="utf-8")
st=s.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(s[st:])
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
extra=json.loads("["+s[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(190,121),(len(base),len(extra))
assert len(base)+len(extra)==311
assert "const DAILY_TARGET=80;" in s and "point-onepage" in s
assert "preserveMergedCardProgress" in s
all_cards=base+extra
assert len({(c["id"],c["front"]) for c in all_cards})==311
by_front={}
for c in all_cards:
 by_front.setdefault(c["front"],[]).append(c)
for f in config["deletes"]:
 assert f in by_front and len(by_front[f])==1,("Missing or ambiguous deletion:",f)
for keep,remove in config["merge"]:
 assert keep in by_front and remove in by_front,(keep,remove)
 assert len(by_front[keep])==len(by_front[remove])==1
assert len(config["deletes"])==40
assert len(config["merge"])==4
assert len(config["mnemonics"])==4

drop=set(config["deletes"])|{remove for keep,remove in config["merge"]}
assert not (set(config["deletes"])&{keep for keep,remove in config["merge"]})
updates={
 "as of":("as of / as of today","～の時点で（as of today＝今日現在）"),
 "acquaint A with B":("acquaint A with B / be acquainted with B","AにBを知らせる／Bをよく知っている"),
 "company directory":("directory / company directory","名簿（company directory＝社員名簿）、建物案内板"),
 "implement":("implement / be implemented","実施する／実施される")
}
for keep,_ in config["merge"]:
 c=by_front[keep][0]
 c["front"],c["meaning"]=updates[keep]
 c["example"]=config["examples"][keep]
# Exact deleted/merged cards (not partial matches) only. IDs can repeat.
kept_base=[c for c in base if c["front"] not in drop]
kept_extra=[c for c in extra if c["front"] not in drop]
kept=kept_base+kept_extra
assert len(kept)==len(all_cards)-len(drop)
assert all(c["front"] not in drop for c in kept)
assert all(c["front"] in {x["front"] for x in kept} for c in by_front["potential successor"]+by_front["lend oneself to"]+by_front["correspondent"])

# Carefully curated synonym consolidation: different meanings are retained.
renamed=0
for c in kept:
 front=c["front"]
 if front in config["meaning"] and front not in {v[0] for v in updates.values()}:
  target=config["meaning"][front]
  if c.get("meaning")!=target:
   c["meaning"]=target
   renamed+=1
# Mapped examples for all cards previously lacking one.
filled=[]
for c in kept:
 if not (c.get("example") or "").strip():
  front=c["front"]
  val=config["examples"].get(front)
  assert val and val.strip(),("No authored example for",c["id"],front)
  c["example"]=val
  filled.append(front)
# Add constructive and the four mnemonic cards: exact text retained on card front.
ids={c["id"] for c in kept}
new_cards=[{"id":"new_constructive_20261126","type":"単語","front":"constructive","meaning":"建設的な","example":config["examples"]["constructive"],"image":""}]
for i,(front,meaning,example) in enumerate(config["mnemonics"],1):
 new_cards.append({"id":"mnemonic_20261126_"+str(i),"type":"熟語","front":front,"meaning":meaning,"example":example,"image":""})
assert all(c["id"] not in ids for c in new_cards)
assert all(c["front"] not in {x["front"] for x in kept} for c in new_cards)
kept_extra.extend(new_cards)
final=kept_base+kept_extra
expected=311-len(drop)+5
assert len(final)==expected,("Final count wrong",len(final),expected)
assert all((c.get("example") or "").strip() for c in final),[(c["id"],c["front"]) for c in final if not c.get("example")]
assert len({(c["id"],c["front"]) for c in final})==len(final)
assert set(config["deletes"]).isdisjoint({c["front"] for c in final})
assert all(x["front"] in {c["front"] for c in final} for x in by_front["potential successor"]+by_front["lend oneself to"]+by_front["correspondent"])
for keep,(front,meaning) in updates.items():
 assert len([c for c in final if c["front"]==front])==1

# Write both BASE and BASE.push, preserve all embedded images for retained cards.
new_base=json.dumps(kept_base,ensure_ascii=False,separators=(",",":"))
s=s[:st]+new_base+s[st+used:]
a=s.index("BASE.push(")+len("BASE.push(")
b=s.index("\n);",a)
s=s[:a]+"\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in kept_extra)+s[b:]

# Add optional merged progress migration for pairs with non-colliding IDs.
# "will be implemented" shares its ID with an unrelated legislation card,
# so its old progress cannot be safely migrated.
old='[["s499", "s388"], ["s468", "s398"], ["s469", "s402"], ["s500", "s391"], ["s502", "s392"], ["s462", "s393"]]'
assert s.count(old)==1
new='[["s499", "s388"], ["s468", "s398"], ["s469", "s402"], ["s500", "s391"], ["s502", "s392"], ["s462", "s393"], ["s390", "s203"], ["s336", "s175"], ["s511", "s339"]]'
s=s.replace(old,new,1)
# For mnemonic cards use multiline wrapping and a readable mobile font size.
startfit='''  const textLen=text.length;\n\n  // 毎カード初期化。'''
assert s.count(startfit)==1
s=s.replace(startfit,'''  const textLen=text.length;
  if(/^①|^②|^③|^④/.test(text)){
    el.style.whiteSpace="pre-line";
    el.style.overflow="visible";
    el.style.fontSize="clamp(15px,4.2vw,21px)";
    el.style.lineHeight="1.45";
    el.style.paddingLeft="6px";
    el.style.paddingRight="6px";
    el.style.minHeight="72px";
    return;
  }

  // 毎カード初期化.''',1)

# Card-level IDs after deletion shouldn't be referenced unconditionally by startup code.
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',s)
available_ids={c["id"] for c in final}
assert all(cid in available_ids for cid in startup_ids),startup_ids
assert "const DAILY_TARGET=80;" in s and "point-onepage" in s
assert "preserveMergedCardProgress" in s and "test-overview" not in s
assert s.rstrip().endswith("</html>")
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",s,re.S|re.I)
assert len(scripts)==1
jsfile=Path("/tmp/toeic_cleanup_20261126.js")
jsfile.write_text(scripts[0],encoding="utf-8")
check=subprocess.run(["node","--check",str(jsfile)],capture_output=True,text=True)
assert check.returncode==0,check.stderr
p.write_text(s,encoding="utf-8")
print("SUCCESS: removed",len(config["deletes"]),"user-specified cards and merged 4 pairs.")
print("FINAL COUNT",len(final),"=",311,"-",len(drop),"+ 5 (constructive + 4 mnemonic).")
print("NEW EXAMPLES ADDED",len(filled),"meanings simplified",renamed)
print("ALL",len(final),"remaining cards have an English example.")
print("Mobile multiline mnemonic view, original 80-card daily plan, embedded images and progress retained.")
print("Startup ID check and JavaScript syntax PASSED.")

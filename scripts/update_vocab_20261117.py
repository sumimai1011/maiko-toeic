#!/usr/bin/env python3
"""Append the 2026-11-17 photographed vocabulary to the existing standalone app."""
import json
from pathlib import Path

NEW = json.loads("[{\"type\":\"熟語\",\"front\":\"on the condition that\",\"meaning\":\"～という条件で\",\"example\":\"The contract will be signed on the condition that payment is made in advance.\"},{\"type\":\"熟語\",\"front\":\"will be implemented\",\"meaning\":\"実施される\",\"example\":\"The new policy will be implemented next month.\"},{\"type\":\"熟語\",\"front\":\"mitigate the risk of\",\"meaning\":\"～のリスクを軽減する\",\"example\":\"The company took steps to mitigate the risk of delays.\"},{\"type\":\"熟語\",\"front\":\"subject to approval\",\"meaning\":\"承認を条件として、承認が必要で\",\"example\":\"The proposal is subject to approval by the director.\"},{\"type\":\"単語\",\"front\":\"verify\",\"meaning\":\"確認する、検証する\",\"example\":\"Please verify the information before submitting the form.\"},{\"type\":\"単語\",\"front\":\"subsequent\",\"meaning\":\"その後の、次に続く\",\"example\":\"Subsequent meetings will be held online.\"},{\"type\":\"単語\",\"front\":\"prospective\",\"meaning\":\"見込みの、将来の\",\"example\":\"The company met with prospective clients.\"},{\"type\":\"単語\",\"front\":\"reconcile\",\"meaning\":\"照合する、調整する\",\"example\":\"The accountant will reconcile the bank statements.\"},{\"type\":\"単語\",\"front\":\"scrutinize\",\"meaning\":\"精査する、詳しく調べる\",\"example\":\"The committee will scrutinize the report.\"},{\"type\":\"単語\",\"front\":\"substantiate\",\"meaning\":\"裏付ける、立証する\",\"example\":\"The applicant must substantiate the claim with documents.\"},{\"type\":\"熟語\",\"front\":\"local resident\",\"meaning\":\"地元住民\",\"example\":\"Local residents attended the public meeting.\"},{\"type\":\"熟語\",\"front\":\"public official\",\"meaning\":\"公務員、政府職員\",\"example\":\"A public official explained the new rules.\"},{\"type\":\"熟語\",\"front\":\"sales projection\",\"meaning\":\"売上予測\",\"example\":\"The sales projection was revised upward.\"},{\"type\":\"単語\",\"front\":\"heighten\",\"meaning\":\"高める、増大させる\",\"example\":\"The campaign will heighten awareness of the issue.\"},{\"type\":\"単語\",\"front\":\"favorable\",\"meaning\":\"好ましい、有利な\",\"example\":\"The product received favorable reviews.\"},{\"type\":\"単語\",\"front\":\"constructive\",\"meaning\":\"建設的な\",\"example\":\"We received constructive feedback.\"},{\"type\":\"単語\",\"front\":\"distribute\",\"meaning\":\"配布する、分配する\",\"example\":\"Please distribute the materials to all participants.\"},{\"type\":\"単語\",\"front\":\"interact\",\"meaning\":\"交流する、やり取りする\",\"example\":\"Employees can interact with customers online.\"},{\"type\":\"熟語\",\"front\":\"demand exceeds production\",\"meaning\":\"需要が生産量を上回る\",\"example\":\"Demand exceeds production during the busy season.\"},{\"type\":\"熟語\",\"front\":\"as of today\",\"meaning\":\"今日現在で\",\"example\":\"As of today, the project is on schedule.\"},{\"type\":\"熟語\",\"front\":\"lag behind\",\"meaning\":\"遅れをとる\",\"example\":\"The project is lagging behind schedule.\"},{\"type\":\"熟語\",\"front\":\"on leave\",\"meaning\":\"休暇中で\",\"example\":\"The manager is on leave this week.\"},{\"type\":\"単語\",\"front\":\"flooding\",\"meaning\":\"洪水、浸水\",\"example\":\"Heavy rain caused flooding in the area.\"},{\"type\":\"単語\",\"front\":\"precaution\",\"meaning\":\"用心、予防措置\",\"example\":\"As a precaution, the building was evacuated.\"},{\"type\":\"熟語\",\"front\":\"exhaust system\",\"meaning\":\"排気装置、排気システム\",\"example\":\"The exhaust system requires regular maintenance.\"},{\"type\":\"熟語\",\"front\":\"order from\",\"meaning\":\"～から注文する\",\"example\":\"We will order supplies from a local vendor.\"},{\"type\":\"単語\",\"front\":\"package\",\"meaning\":\"荷物、小包\",\"example\":\"The package will arrive tomorrow.\"},{\"type\":\"単語\",\"front\":\"dedication\",\"meaning\":\"献身、熱意／落成式\",\"example\":\"Her dedication to the project was recognized.\"},{\"type\":\"単語\",\"front\":\"relocation\",\"meaning\":\"移転、移動\",\"example\":\"The office relocation is scheduled for January.\"},{\"type\":\"単語\",\"front\":\"store-wide\",\"meaning\":\"全店舗の、店全体の\",\"example\":\"The store-wide sale starts on Friday.\"},{\"type\":\"熟語\",\"front\":\"pass out\",\"meaning\":\"配布する\",\"example\":\"Please pass out the handouts before the presentation.\"},{\"type\":\"熟語\",\"front\":\"take note\",\"meaning\":\"注意する、書き留める\",\"example\":\"Please take note of the revised deadline.\"},{\"type\":\"熟語\",\"front\":\"quite a bit\",\"meaning\":\"かなり、相当\",\"example\":\"Sales increased quite a bit this quarter.\"}]")
path = Path("index.html")
source = path.read_text(encoding="utf-8")
marker = "const BASE="
assert source.count(marker) == 1, "Unexpected app structure"
start = source.index(marker) + len(marker)
cards, consumed = json.JSONDecoder().raw_decode(source[start:])
assert isinstance(cards, list) and len(cards) >= 100, "Unexpected card data"
existing = {str(c.get("front", "")).strip().casefold() for c in cards}
ids = {str(c.get("id","")) for c in cards}
next_id = max([int(x[1:]) for x in ids if x.startswith("s") and x[1:].isdigit()] or [0]) + 1
added = 0
for card in NEW:
    key = card["front"].strip().casefold()
    if key in existing:
        continue
    while f"s{next_id}" in ids:
        next_id += 1
    card["id"] = f"s{next_id}"
    ids.add(card["id"])
    existing.add(key)
    cards.append(card)
    next_id += 1
    added += 1
assert len(cards) >= 200, "Existing cards must remain intact"
replacement = json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
updated = source[:start] + replacement + source[start+consumed:]
assert updated.rstrip().endswith("</html>"), "HTML was truncated"
assert updated.count("const BASE=") == 1
if added:
    path.write_text(updated, encoding="utf-8")
print(f"Added {added} of {len(NEW)} photographed entries; total {len(cards)} cards.")


# Export only vocabulary text so the user's locally saved cards can be reviewed
# without transferring illustrations or study progress.
html = path.read_text(encoding="utf-8")
menu_anchor = '  <button id="showPoints" class="m3">POINT</button>'
export_button = '  <button id="exportCards" class="m3" type="button">全カードを書き出す</button>'
export_js = r'''
document.getElementById("exportCards").onclick = () => {
  const cards = studyDeck().map(x => ({
    type: x.type,
    front: x.front,
    meaning: x.meaning,
    id: x.id
  }));
  const payload = {
    exportedAt: new Date().toISOString(),
    total: cards.length,
    cards: cards
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type:"application/json;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "TOEIC全カード一覧.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
};
'''
if 'id="exportCards"' not in html:
    assert html.count(menu_anchor) == 1, "Cannot locate card menu"
    html = html.replace(menu_anchor, menu_anchor + "\n" + export_button)
    assert html.count("\n</script>\n</body>") == 1
    html = html.replace("\n</script>\n</body>", "\n" + export_js + "\n</script>\n</body>")
    assert html.rstrip().endswith("</html>")
    assert html.count('id="exportCards"') == 1
    path.write_text(html, encoding="utf-8")
    print("Added browser-only full-deck vocabulary export button.")
else:
    print("Export button already present; no changes.")

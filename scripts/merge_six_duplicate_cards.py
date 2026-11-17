#!/usr/bin/env python3
"""Merge exactly six user-approved duplicate pairs from the live TOEIC app.
Preserve earlier card IDs, review history, and any imagery on either copy."""
from pathlib import Path
import json
from collections import defaultdict

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
start=src.index("const BASE=")+len("const BASE=")
base,consumed=json.JSONDecoder().raw_decode(src[start:])
push_start=src.index("BASE.push(")+len("BASE.push(")
push_end=src.index("\n);",push_start)
extra=json.loads("["+src[push_start:push_end].strip().strip(",")+"]")
assert len(base)==233 and len(extra)==169, (len(base),len(extra))
approved={
 "interact":"交流する",
 "dedication":"献身、落成式",
 "take note":"留意する",
 "lag behind":"遅れをとる",
 "on leave":"休暇中で",
 "flooding":"洪水、浸水",
}
whole=base+extra
groups=defaultdict(list)
for card in whole: groups[card["front"].strip().casefold()].append(card)
duplicates={k:v for k,v in groups.items() if len(v)>1}
assert set(duplicates)==set(approved), {k:[x.get("id") for x in v] for k,v in duplicates.items()}
assert all(len(v)==2 for v in duplicates.values())
removed_ids=[]
migrations=[]
for word,meaning in approved.items():
 first,second=duplicates[word]
 assert first in base and second in extra, (word,first["id"],second["id"])
 # The earlier card keeps its stable ID (and its established review history).
 # Preserve imagery, examples and other resources on the removed copy.
 for k in ("image","example","hint","note","audio"):
  if not first.get(k) and second.get(k):
   first[k]=second[k]
 first["meaning"]=meaning
 removed_ids.append(second["id"])
 migrations.append([second["id"], first["id"]])
extra=[c for c in extra if c["id"] not in removed_ids]
assert len(base)==233 and len(extra)==163 and len(base)+len(extra)==396
assert len({c["front"].casefold().strip() for c in base+extra})==396

# Patch first JSON literal without affecting the existing picture assets.
src=src[:start]+json.dumps(base,ensure_ascii=False,separators=(",",":"))+src[start+consumed:]
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
src=src[:a]+"\n"+",\n".join(json.dumps(c,ensure_ascii=False,separators=(",",":")) for c in extra)+src[b:]

# Preserve review data from any deleted duplicate, only if kept card has none.
# This runs once per page view and does not touch the old record.
migration_js="""
// Preserve study history when duplicate vocabulary entries are consolidated.
(function preserveMergedCardProgress(){
 const mapping=__MAP__;
 let updated=false;
 for(const [removed,kept] of mapping){
  if(progress && progress[removed] && !progress[kept]){
   progress[kept]={...progress[removed]};
   updated=true;
  }
 }
 if(updated)saveProgress();
})();
""".replace("__MAP__",json.dumps(migrations,ensure_ascii=False))
anchor="\nrenderHome();\n</script>"
assert src.count(anchor)==1
assert "preserveMergedCardProgress" not in src
src=src.replace(anchor,"\n"+migration_js+anchor,1)
assert "cardEditLayer" not in src and 'id="exportCards"' not in src
assert src.rstrip().endswith("</html>")
path.write_text(src,encoding="utf-8")
print("Verified final:",len(base),"+",len(extra),"=",len(base)+len(extra))
for word,v in duplicates.items():
 print("Merged:",word, "kept",v[0]["id"],"removed",v[1]["id"],"meaning",v[0]["meaning"],"image preserved",bool(v[0].get("image")))

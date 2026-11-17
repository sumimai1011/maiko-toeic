#!/usr/bin/env python3
"""Add two requested TOEIC cards while preserving all 316 existing entries."""
import json
import re
import subprocess
from pathlib import Path

path=Path("index.html")
src=path.read_text(encoding="utf-8")
assert src.count("const BASE=")==1 and src.count("BASE.push(")==1
p=src.index("const BASE=")+len("const BASE=")
base,used=json.JSONDecoder().raw_decode(src[p:])
a=src.index("BASE.push(")+len("BASE.push(")
b=src.index("\n);",a)
extra=json.loads("["+src[a:b].strip().strip(",")+"]")
assert (len(base),len(extra))==(188,128), (len(base),len(extra))
assert len(base)+len(extra)==316
allcards=base+extra
assert not any(c["front"].strip().lower() in ("call off","mail") for c in allcards), "One of the new cards already exists"
existing={c["id"] for c in allcards}
new=[
 {"id":"new_call_off_20261117","type":"熟語","front":"call off","meaning":"中止する","example":"The meeting was called off due to bad weather."},
 {"id":"new_mail_20261117","type":"単語","front":"mail","meaning":"郵便（email＝電子メール）","example":"Please send the documents by mail.","note":"mail＝郵便 / email＝電子メール"}
]
assert all(c["id"] not in existing for c in new)
base.extend(new)
assert len(base)+len(extra)==318
src=src[:p]+json.dumps(base,ensure_ascii=False,separators=(",",":"))+src[p+used:]
ids={c["id"] for c in base+extra}
startup_ids=re.findall(r'Object\.assign\(BASE\.find\(x=>x\.id==="([^"]+)"\)',src)
assert all(id in ids for id in startup_ids),("Invalid startup refs",startup_ids)
assert "preserveMergedCardProgress" in src
assert src.rstrip().endswith("</html>")
scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)
assert len(scripts)==1
js=Path("/tmp/toeic_add2.js")
js.write_text(scripts[0],encoding="utf-8")
result=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
assert result.returncode==0,result.stderr
path.write_text(src,encoding="utf-8")
print("Added call off / 中止する and mail / 郵便（email＝電子メール）")
print("Validated 190 base + 128 additional = 318 cards")
print("Existing 316 cards, embedded images, history and startup refs remain intact")

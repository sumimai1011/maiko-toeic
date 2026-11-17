#!/usr/bin/env python3
"""Check published TOEIC inline JS for syntax errors and home initialization."""
from pathlib import Path
import re, subprocess
src=Path("index.html").read_text(encoding="utf-8")
print("HTML length:",len(src),"inline script matches:",len(re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>",src,re.S|re.I)))
for i,m in enumerate(re.finditer(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S|re.I)):
    script=m.group(1)
    p=Path(f"/tmp/check_toeic_{i}.js")
    p.write_text(script,encoding="utf-8")
    x=subprocess.run(["node","--check",str(p)],text=True,capture_output=True)
    print("Script",i,"bytes",len(script),"node exit",x.returncode)
    if x.returncode: print("NODE SYNTAX ERROR:",x.stderr[-3000:])
    print("start snippet",repr(script[:160]),"end snippet",repr(script[-300:]))
    print("renderHome calls:",script.count("renderHome();"),"BASE.push calls:",script.count("BASE.push("),"progress safeguard",script.count("preserveMergedCardProgress"))
    if x.returncode: raise SystemExit(1)

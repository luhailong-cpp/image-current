import json,subprocess,sys
from pathlib import Path
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/12-yuexianshi")
for n in [1,2,4,5,6]:
    tag=f"{n:02}.guardfix-20261008"
    p=root/"records"/"hit-W"/f"{tag}.receipt.json"
    d=json.loads(p.read_text(encoding="utf-8"))
    if n in [1,2,4]:
        d["candidateOnly"]=True
        d["disposition"]="rejected: correct narrow feet but upper-body hit stage was overwritten toward full baseline pose"
    else:d["disposition"]="selected: near/final recovery stance, independent AI correction"
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    subprocess.run([sys.executable,str(root/"record_guard_hit.py"),str(n)],check=True)


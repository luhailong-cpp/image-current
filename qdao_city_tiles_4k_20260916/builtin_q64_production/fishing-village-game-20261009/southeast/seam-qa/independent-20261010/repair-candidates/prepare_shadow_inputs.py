import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence,read_json,sha
s=Sources()
t=s.tile('r11_c08')
p=BASE/'r11_c08/colorpass-selected.json'
t.update(selection=read_json(p),selectedPath=p,selectedSha256=sha(p))
for name,box,focus in [('S1-hull-shadow',[30050,41400,31304,42654],[30680,41700,30830,42480]),('S2-stone-shadow',[31700,42350,32954,43604],[32625,42945,32700,43080])]:
 rec=write_evidence(s,HERE,name+'-input',box,{'purpose':'shadow shape repair target from current color candidate; r11c08 selection overridden in memory only','focusBoxGlobal':focus})
 assert rec['sourceComplete']
 print(json.dumps({'name':name,'file':rec['image']['file'],'sha256':rec['image']['sha256'],'globalBox':box}))

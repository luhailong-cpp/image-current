import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess
Z=Path(__file__).resolve().parents[1];Q=Z/'qa';N=Z/'native'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'path':Path(p).as_posix(),'sha256':sha(p)}
wr=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plans=json.loads((Q/'r08c05-internal-audit-v1.json').read_text())['repairsPlanned']
settings={
 'a_stair':([0,340,1254,1230],40,['left']),
 'b_parapet':([0,300,1180,1254],35,[]),
 'c_lily':([0,270,940,880],45,[]),
 'd_shadow':([260,0,1080,1254],40,['top']),
 'e_water':([0,240,1254,1030],40,[]),
 'f_rail_arms':([120,300,1150,770],45,[]),
 'g_postbeam':([100,380,1080,1254],35,[]),
 'h_goldfinial':([520,280,960,760],40,[]),
 'i_lowerstone':([0,280,1170,1050],35,[])}
rep=[]
for x in plans:
 bounds,margin,edges=settings[x['id']];stem=x['stem'];rep.append({'id':x['id'],'source':x['source'],'repair':ref(N/(stem+'.png')),'generationRecord':ref(N/(stem+'.png.generation.json')),'tileContextBox':x['tileContextBox'],'contextBox':x['contextBox'],'repairBounds':bounds,'margin':margin,'openSides':edges})
base=Q/'full-tile-r08_c05-assembly.json';a=json.loads(base.read_text());m={'schemaVersion':1,'outputPrefix':'repair-r08_c05-internal-v1','baseAssembly':ref(base),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':rep}
mp=Q/'repair-r08_c05-internal-v1.manifest.json';assert not mp.exists();wr(mp,m)
src=(Q/'repair-compose.py').read_text(encoding='utf-8')
src=src.replace('context_box, minimum_seam):','context_box, minimum_seam, open_sides=()):')
old='chosen = ((xx >= paths["left"][:, None]) & (xx < paths["right"][:, None]) &\n              (yy >= paths["top"][None, :]) & (yy < paths["bottom"][None, :]))'
new='chosen = ((True if "left" in open_sides else xx >= paths["left"][:, None]) & (True if "right" in open_sides else xx < paths["right"][:, None]) &\n              (True if "top" in open_sides else yy >= paths["top"][None, :]) & (True if "bottom" in open_sides else yy < paths["bottom"][None, :]))'
assert old in src;src=src.replace(old,new)
src=src.replace('"pixels": repair})','"pixels": repair, "openSides": item.get("openSides", [])})')
src=src.replace('item["contextBox"], helper._minimum_vertical_seam)','item["contextBox"], helper._minimum_vertical_seam, item["openSides"])')
src=src.replace('prepared.append({"id": rid', 'for side in item.get("openSides", []):\n            require((side == "left" and x1 == 0 and l == 0) or (side == "top" and y1 == 0 and t == 0), "Open side allowed only at true context perimeter")\n        prepared.append({"id": rid')
tool=Q/'repair-compose-open-perimeter-v1.py';assert not tool.exists();tool.write_text(src,encoding='utf-8')
subprocess.run([sys.executable,'-B',str(tool),'--manifest',str(mp)],check=True)
from PIL import Image
out=Image.open(Q/'repair-r08_c05-internal-v1-context-native.png')
for p in plans:out.crop(p['contextBox']).save(Q/('repair-r08_c05-internal-v1-'+p['id']+'-after-100pct.png'))

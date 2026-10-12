from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
p=D/'apply.py';s=p.read_text(encoding='utf-8')
s=s.replace("[(118,846),(817,233),(855,315),(825,425),(260,932),(137,916)]","[(99,819),(805,204),(886,280),(862,429),(270,951),(110,939)]")
s=s.replace("[(490,588),(529,597),(551,641),(545,688),(519,719),(490,689)]","[(478,577),(551,586),(576,691),(516,744),(477,718)]")
s=s.replace("name+'.png')\n  if ingest:mp.parent", "name+'-v2.png')\n  if ingest:mp.parent")
s=s.replace("name+'-integrated-100pct.png'","name+'-v2-integrated-100pct.png'")
s=s.replace("D/'replay.json'","D/'replay-v2.json'").replace("D/'verification.json'","D/'verification-v2.json'")
s=s.replace("assert sha(C)==sha(B),'Refuse overwrite non-baseline candidate'","assert sha(C)=='b935db8e1e765a866c2a295d7e57b177f68f331ee4093331a2bb7c450c65b6a5','Refuse unexpected candidate'")
s=s.replace("D/'before.candidate.png'","D/'before-v2.candidate.png'").replace("D/'before.generation.json'","D/'before-v2.generation.json'")
q=D/'apply-v2.py';assert not q.exists();q.write_text(s,encoding='utf-8')
T=D.parents[1];Z=T.parent
north=Z/'r06_c13/candidates/r06_c13.candidate.png'
base=T/'qa/core-baseline/f30ef04cf1155a6e57a2/r07_c13-core-baseline.candidate.png'
im=Image.new('RGB',(1254,1254))
im.paste(Image.open(north).crop((2445,3796,3699,4096)),(0,0))
im.paste(Image.open(base).crop((2445,0,3699,954)),(0,300))
f=D/'contexts/m04-upper-pipe.png';im.save(f)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Path(str(f)+'.generation.json').write_text(json.dumps({'file':str(f),'sha256':sha(f),'derivedFrom':[{'file':str(north),'sha256':sha(north),'crop':[2445,3796,3699,4096],'paste':[0,0]},{'file':str(base),'sha256':sha(base),'crop':[2445,0,3699,954],'paste':[0,300]}],'operation':'integer native pixel crops/pastes, no resizing','tileOrigin':[2445,-300]},indent=2)+'\n',encoding='utf-8')


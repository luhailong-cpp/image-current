"""Input guides from authoritative selected cores, excluding unselected native halos."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
from review_external_seams import Sources
import tile_native_workflow as wf
Z=Path(__file__).resolve().parent
tile,pid=sys.argv[1:3]; T=wf.writable_tile(tile)
base=Path(sys.argv[3]) if len(sys.argv)>3 else Path(wf.patch(wf.read(wf.plan_path(tile)),pid)['file'])
label=sys.argv[4] if len(sys.argv)>4 else 'v1'
plan=wf.patch(wf.read(wf.plan_path(tile)),pid); box=plan['globalBox']
S=Sources();unused,pieces,missing=S.extract(box)
im=Image.open(base).convert('RGB');assert im.size==(1254,1254)
adopted=[]
for p in pieces:
 if p['tile']==tile and p['patch']==pid:continue
 im.paste(S.images[Path(p['file'])].crop(p['sourceCrop']),tuple(p['destination']))
 adopted.append(p)
out=T/'layout-only'/f'{pid}-true-core-conditioned-{label}.png';assert not out.exists();im.save(out)
wf.write(out.with_suffix('.png.derivation.json'),{'createdAt':wf.now(),'file':str(out),'sha256':wf.sha(out),'tile':tile,'patch':pid,'targetGlobalBox':box,'baseInput':{'path':str(base),'sha256':wf.sha(base)},'classification':'Input only; not final art','operation':'Exact native pixels belonging only to currently selected 1024 cores pasted over the input frame; no neighbor halo used, no resampling','nativeSources':adopted,'missingSources':missing,'outputDimensions':[1254,1254],'coreCrop':[115,115,1139,1139]})
print(json.dumps({'guide':str(out),'sha256':wf.sha(out),'realCorePieces':len(adopted),'resampling':False}))

from pathlib import Path
from PIL import Image
import sys,runpy
from workflow import ROOT,read,write,sha,now
tid='r12_c11'
tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==tid)
sys.argv=['prepare_tile.py',tid];runpy.run_path(str(ROOT/'prepare_tile.py'),run_name='__main__')
p=ROOT/'progress-r12_c11.json'
if not p.exists():write(p,{'tile':tid,'updatedAt':now(),'status':'prepared','generatedNativeCount':0,'selectedCoordinateCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'missingPatches':[x['id'] for x in tile['patches']],'inFlightRequests':[],'lastError':None,'nextStep':'Generate from true north and approved east native overlaps, then verify source and actual joins'})
s=ROOT/'selection-r12_c11.json'
if not s.exists():write(s,{'tile':tid,'patchVersions':{},'pendingFindings':[]})
qa=ROOT/'qa'/'r12_c11-preparation';qa.mkdir(exist_ok=True)
im=Image.new('RGB',(4096,4096))
for p in tile['patches']:
 src=Image.open(ROOT/'guides'/f"{p['id']}.layout-only.png")
 im.paste(src.crop((115,115,1139,1139)),((p['subcolumn']-1)*1024,(p['subrow']-1)*1024))
im.resize((1024,1024),Image.Resampling.LANCZOS).save(qa/'layout-preview.png')
print(tile['origin'],tile['coreGlobalBox'])

"""Exact native QA only for seams and crosses touching named changed patches."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import sys, json, hashlib
import tile_native_workflow as wf

tile, changed_arg, label = sys.argv[1:4]
T = wf.writable_tile(tile)
changed = set(changed_arg.split(','))
Q = T / 'qa' / label
Q.mkdir(parents=True, exist_ok=False)
selection = T / 'selected-patches.json'
sel = wf.read(selection)
assert changed.issubset(sel['patches'])
ox, oy = (int(tile[5:7])-1)*4096, (int(tile[1:3])-1)*4096
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources = {}
records = []
def record(name, box, pids):
    if not changed.intersection(pids) or not all(p in sel['patches'] for p in pids): return
    out = Image.new('RGB', (box[2]-box[0], box[3]-box[1]))
    used = []
    for pid in pids:
        path = T / sel['patches'][pid]
        image = Image.open(path).convert('RGB')
        assert image.size == (1254,1254)
        x,y = (int(pid[2])-1)*1024,(int(pid[1])-1)*1024
        ix0,iy0,ix1,iy1 = max(x,box[0]),max(y,box[1]),min(x+1024,box[2]),min(y+1024,box[3])
        crop = [ix0-x+115,iy0-y+115,ix1-x+115,iy1-y+115]
        destination = [ix0-box[0],iy0-box[1]]
        out.paste(image.crop(crop),destination)
        source = {'patch':pid,'file':str(path),'sha256':sha(path)}
        sources[pid] = source
        used.append(dict(source,sourceCrop=crop,destination=destination))
    path = Q / (name+'.png')
    out.save(path)
    item = {'file':str(path),'sha256':sha(path),'globalBox':[box[0]+ox,box[1]+oy,box[2]+ox,box[3]+oy],
            'sources':used,'resamplingApplied':False,'visualReview':'pending'}
    wf.write(path.with_suffix('.png.derivation.json'),item)
    records.append(item)
for r in range(1,5):
    for c in range(1,5):
        if c<4: record(f'p{r}{c}--p{r}{c+1}',[c*1024-256,(r-1)*1024,c*1024+256,r*1024],[f'p{r}{c}',f'p{r}{c+1}'])
        if r<4: record(f'p{r}{c}--p{r+1}{c}',[(c-1)*1024,r*1024-256,c*1024,r*1024+256],[f'p{r}{c}',f'p{r+1}{c}'])
for r in range(1,4):
    for c in range(1,4):
        record(f'cross-r{r}-c{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256],
               [f'p{rr}{cc}' for rr in (r,r+1) for cc in (c,c+1)])
wf.write(Q/'manifest.json',{'tile':tile,'createdAt':datetime.now(timezone.utc).isoformat(),
    'selection':str(selection),'selectionSha256':sha(selection),'selectedCount':len(sel['patches']),
    'changedPatches':sorted(changed),'sources':list(sources.values()),'evidence':records,
    'classification':'native QA only; no art generated or resized','internalReady':False,'formalAccepted':False})
print(json.dumps({'directory':str(Q),'QAImageCount':len(records),'evidence':[Path(i['file']).name for i in records]}))

"""Read only selected existing sources; write native-pixel QA crops here only."""
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
TILE = OUT.parents[1]
ZONE = TILE.parent
spec = importlib.util.spec_from_file_location('existing_assemble', ZONE / 'assemble.py')
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)
tile, plan = assembly.load_plan('r06_c13')
ids = [f'p{r}{c}' for r in (1, 2) for c in range(1, 5)] + ['p31']
items = {item['id']: item for item in plan['patches']}
sources, evidence = {}, []
for patch_id in ids:
    pixels, record = assembly.inspect_source(tile, items[patch_id])
    sources[patch_id] = pixels
    evidence.append(record)
canvas = assembly.compose(plan, sources)
ox, oy = plan['coreWorldBox'][:2]
artifacts, seams = [], []

def save(pixels, name, **metadata):
    target = OUT / name
    pixels.save(target)
    with Image.open(target) as saved:
        assert saved.size == pixels.size and saved.mode == pixels.mode
        assert saved.tobytes() == pixels.tobytes()
    artifact = {'file': str(target), 'sha256': assembly.sha(target),
                'pixels': list(pixels.size), 'resized': False,
                'blurred': False, **metadata}
    artifacts.append(artifact)
    return artifact

def native_crop(patch_id, box, name):
    cx, cy = items[patch_id]['contextWorldBox'][:2]
    return save(sources[patch_id].crop(box), name, sourceIds=[patch_id],
                nativeBox=list(box), worldBox=[cx+box[0],cy+box[1],cx+box[2],cy+box[3]])

native_crop('p23', (60, 130, 365, 365), 'p23-mixed-flower-leaf-100pct.png')
for patch_id in ['p21', 'p22', 'p23', 'p24']:
    native_crop(patch_id, (115, 955, 1139, 1254), f'{patch_id}-lower-core-and-halo-100pct.png')
for axis, first, second, x, y in assembly.seam_pairs():
    if first not in sources or second not in sources:
        continue
    a, b = sources[first], sources[second]
    if axis == 'vertical':
        box = [x-192, y, x+192, y+1024]
        overlap_a, overlap_b = a.crop((1024,0,1254,1254)), b.crop((0,0,230,1254))
    else:
        box = [x,y-192,x+1024,y+192]
        overlap_a, overlap_b = a.crop((0,1024,1254,1254)), b.crop((0,0,1254,230))
    artifact = save(canvas.crop(box), f'{axis}-{first}-{second}-join-100pct.png',
                    sourceIds=[first,second], tileBox=box,
                    worldBox=[ox+box[0],oy+box[1],ox+box[2],oy+box[3]])
    seams.append({'axis':axis,'sourceIds':[first,second],
                  'worldSeam':ox+x if axis=='vertical' else oy+y,
                  'crop':artifact['file'], 'overlapMetrics':assembly.difference_metrics(overlap_a,overlap_b)})
for col in (1,2,3):
    box = [col*1024-300,724,col*1024+300,1324]
    save(canvas.crop(box),f'intersection-r1-c{col}-100pct.png',
         sourceIds=[f'p{r}{c}' for r in (1,2) for c in (col,col+1)],tileBox=box,
         worldBox=[ox+box[0],oy+box[1],ox+box[2],oy+box[3]])
assert all(assembly.sha(record['file']) == record['sha256'] for record in evidence)
report={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r06_c13',
        'reviewScope':ids,'excludedNewSources':'p32 onward deliberately unread',
        'selectedNative':{'p21':'p21-v2.png'},'sources':evidence,'artifacts':artifacts,
        'seams':seams,'sourceCount':len(evidence),'inspectedPairCount':len(seams),
        'sourceHashesUnchangedAtEnd':True,'resized':False,'formalAcceptance':False,
        'writableDirectory':str(OUT),'progressModified':False}
(OUT/'source-inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources':len(evidence),'seams':len(seams),'crops':len(artifacts),
                  'report':str(OUT/'source-inspection.json')},ensure_ascii=False))

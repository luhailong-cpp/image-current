"""Verify delivery bytes, lineage, common transforms and active preview references."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=load(ROOT/'final/manifest.json');rows=load(ROOT/'final-selection.json')
currentTiming=load(ROOT/'animation-timing.json')
runTiming=currentTiming['run']
assert runTiming['frames']==16 and runTiming['frameMs']==60 and runTiming['cycleMs']==960
assert runTiming['uniform'] is True and runTiming['frames']*runTiming['frameMs']==runTiming['cycleMs']
for action,frames,frameMs,cycleMs in [('hit',6,40,240),('attack',12,30,360),('cast',16,45,720)]:
    assert (currentTiming[action]['frames'],currentTiming[action]['frameMs'],currentTiming[action]['cycleMs'])==(frames,frameMs,cycleMs)
assert len(rows)==196 and manifest['frames']==rows
assert len({r['sha256'] for r in rows})==196
assert len({r['nativeSha256'] for r in rows})==196
reg=load(ROOT/'registration.json');sequences={};records=[]
for r in rows:
    p=ROOT/r['file'];d=load(ROOT/r['generationRecord'])
    assert p.resolve().is_relative_to((ROOT/'final').resolve())
    assert sha(p)==r['sha256']==d['sha256'] and d['finalVisualPassed'] is True
    assert d['source']['sha256']==d['sourceGeneration']['sha256']==r['nativeSha256']
    assert d['source']['file']==r['nativeSourceFile']
    # Embedded historical records may keep an earlier machine's absolute path;
    # their bytes are bound above by the same native SHA, not by that old path.
    assert (ROOT/d['offlineAcceptance']).is_file()
    assert min(d['source']['nativeSize'])>=1024
    assert d['actualModel'] is None and d['actualQuality'] is None
    with Image.open(p) as im:
        im.load();assert im.size==(1024,1024) and im.mode=='RGBA'
        a=im.getchannel('A');assert a.getextrema()==(0,255)
        assert max(a.crop(b).getextrema()[1] for b in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])==0
    key=r['action']+'/'+r['direction'];t=d['transform']
    assert t['globalScale']==reg['globalScale'] and t['targetRoot']==[512,942]
    assert t['sourceRoot']==reg['sequences'][key]['sourceRoot'] and t['perFrameNormalization'] is False
    sequences.setdefault(key,[]).append(r['frame']);records.append({'file':r['file'],'sha256':r['sha256'],'pass':True})
for action,s in manifest['specifications'].items():
    assert s['frameMs']==currentTiming[action]['frameMs']
    assert s['cycleOrClipMs']==currentTiming[action]['cycleMs']
    for direction in s['directions']:
        assert sorted(sequences[action+'/'+direction])==list(range(1,s['framesPerDirection']+1))
        assert s['framesPerDirection']*s['frameMs']==s['cycleOrClipMs']
preview=load(ROOT/'preview/manifest.json')
finalHashByFile={r['file']:r['sha256'] for r in rows}
assert preview['summary']['present']==preview['summary']['format1024RGBA']==preview['summary']['withGenerationRecord']==196
assert preview['summary']['missing']==preview['summary']['duplicateFileSlots']==0
for seq in preview['sequences']:
    assert seq['frameMs']==currentTiming[seq['action']]['frameMs']
    assert seq['durationMs']==currentTiming[seq['action']]['cycleMs']
    for frame in seq['frames']:
        assert (ROOT/frame['file']).is_file() and frame['file'].startswith('final/')
        assert frame['sha256']==finalHashByFile[frame['file']]
timing=load(ROOT/'preview/timing-grounding-final-data.json')
assert timing['uniformCycleDurationsMs']==[runTiming['cycleMs']] and timing['frameMs']==runTiming['frameMs']
assert timing['phaseWeightsApplied'] is False
assert all((ROOT/f['file']).is_file() and f['file'].startswith('final/') for frames in timing['sequences'].values() for f in frames)
result={'checkedAt':datetime.now(timezone.utc).isoformat(),'finalFrames':196,'uniqueNativeFrames':196,'uniqueFinalFrames':196,'canvas':'1024 RGBA','allTransparentBorders':True,'constantTransformPerSequence':True,'globalScale':reg['globalScale'],'activePreviewReferencesComplete':True,'sequenceCount':len(sequences),'clientIntegrated':False,'clientRuntimeValidated':False,'checks':records}
(ROOT/'provenance/final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))

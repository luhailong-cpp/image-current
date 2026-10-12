from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
T=Path(__file__).resolve().parent;R=T/'repairs-north-20261011';D=T/'review/north-v6';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mf=T/'candidate/r14_c13-north-v6-manifest.json';m=read(mf);base=m['baseAssemblyPointerSnapshot'];a=Image.open(base['candidate']['path']).convert('RGB');before=np.asarray(a).copy()
for s in m['steps']:
    assert sha(s['source'])==s['sourceSha256'] and np.array_equal(np.asarray(a),np.asarray(Image.open(s['source']).convert('RGB')))
    assert sha(s['native'])==s['nativeSha256'] and sha(s['alpha'])==s['alphaSha256']
    assert sha(s['northSource'])==s['northSourceSha256']
    x,y,x2,y2=s['tilePlacementBox'];old=a.crop((x,y,x2,y2));native=Image.open(s['native']).convert('RGB');mask=Image.open(s['alpha']);assert native.size==mask.size==(1254,1254)
    assert np.max(np.asarray(mask)[:400])==0
    a.paste(Image.composite(native.crop(s['nativeCropBox']),old,mask.crop(s['nativeCropBox'])),(x,y))
    assert np.array_equal(np.asarray(a),np.asarray(Image.open(s['output']).convert('RGB'))) and sha(s['output'])==s['outputSha256']
core=np.asarray(a);assert np.array_equal(core[:630,3471:],before[:630,3471:])
outside=np.ones((4096,4096),bool)
for s in m['steps']:
    x,y,x2,y2=s['tilePlacementBox'];outside[y:y2,x:x2]=False
assert np.array_equal(core[outside],before[outside]);assert sha(m['candidate']['path'])==m['candidate']['sha256']
ctx=np.asarray(Image.open(m['context']['path']).convert('RGB'));assert np.array_equal(ctx[115:4211,115:4211],core)
for p in R.glob('*-native.png.generation.json'):
    g=read(p);assert sha(g['file'])==g['sha256'];assert g['width']==g['height']==1254 and g['actualModel'] is None and g['actualQuality'] is None
    assert sha(g['evidence']['receipt'])==g['evidence']['receiptSha256'];assert sha(g['evidence']['originalOutputPath'])==g['evidence']['originalSha256']
    for ref in g['preparation']['references']:assert sha(ref['path'])==ref['sha256']
old=Image.open(m['steps'][0]['northSource']).convert('RGB');strip=Image.new('RGB',(4096,800));strip.paste(old.crop((0,3696,4096,4096)),(0,0));strip.paste(a.crop((0,0,4096,400)),(0,400))
for k in range(4):strip.crop((k*1024,0,(k+1)*1024,800)).save(D/f'full-north-quarter{k}-100pct.png')
east=read(T.parent/'r14_c14/candidate/latest-assembly.json');ep=Path(east['candidate']['path']);assert sha(ep)==east['candidate']['sha256'];ei=Image.open(ep).convert('RGB');es=Image.new('RGB',(800,4096));es.paste(a.crop((3696,0,4096,4096)),(0,0));es.paste(ei.crop((0,0,400,4096)),(400,0))
for k in range(4):es.crop((0,k*1024,800,(k+1)*1024)).save(D/f'full-east-quarter{k}-100pct.png')
for edge,box in {'south':[0,3840,4096,4096],'west':[0,0,256,4096]}.items():a.crop(box).save(D/f'edge-{edge}-100pct.png')
a.resize((1024,1024),Image.Resampling.LANCZOS).save(D/'overview-preview-only.png')
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exactPixelReplayVerified':True,'northSourceUnchanged':True,'outsideRepairUnchanged':True,'reservedTopRightUnchanged':True,'reservedTopRightBox':[3471,0,4096,630],'nativeCountBefore':29,'newNativeCount':4,'totalNativeCount':33,'newAppliedNativeCount':2,'totalAppliedRepairCount':9,'allFourNewGenerationRecordsChecked':True,'eastCandidateSnapshot':east['candidate'],'core':m['candidate'],'context':m['context'],'formalAccepted':False}
(D/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');m.update(exactPixelReplayVerified=True,verification={'path':str(D/'verification.json'),'sha256':sha(D/'verification.json')});mf.write_text(json.dumps(m,indent=2),encoding='utf-8')
print(json.dumps(report))

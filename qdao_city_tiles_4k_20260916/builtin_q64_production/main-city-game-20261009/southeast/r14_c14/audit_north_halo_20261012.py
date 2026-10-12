from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;N=T.parent/'r13_c14';D=T/'repairs/north-halo-audit-20261012';D.mkdir(exist_ok=True)
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':str(p),'sha256':sha(p)}
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def png(p,a):
 with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
selected=rd(N/'repairs/latest-repair.json');assert selected['candidate']['sha256']=='89c0bd8fcf2a507c90a1b690a2e0911a8b490f195820502eb026c56f298bc2d4'
for a in [selected['candidate'],selected['context']]:assert sha(a['path'])==a['sha256']
baseptr=rd(N/'candidate/latest-assembly.json');m=rd(baseptr['manifest']['path']);assert sha(baseptr['manifest']['path'])==baseptr['manifest']['sha256']
seams=m['seamPathsAndAlpha'];assert sha(seams['path'])==seams['sha256'];z=np.load(seams['path'],allow_pickle=False)
sources=[s for s in m['nativeSources'] if s['logicalId'].startswith('p04_')]
strip=np.zeros((1254,4326,3),np.uint8);first=np.zeros((115,4326),np.uint8);second=first.copy();weight=first.copy();provenance=[]
for i,s in enumerate(sources):
 assert sha(s['native'])==s['nativeSha256']; im=Image.open(s['native']);assert im.size==(1254,1254)
 g=rd(s['generationRecord']);assert sha(s['generationRecord'])==s['generationRecordSha256'];assert g['actualModel'] is None and g['actualQuality'] is None and g['route']=='builtin'
 e=g['evidence'];checks=[]
 for path,expected in [(e['receipt'],e['receiptSha256']),(e['request'],e['requestSha256']),(e['preparation'],e['preparationSha256']),(e['originalOutputPath'],e['originalSha256']),(g['prompt'],g['promptSha256'])]+[(r['path'],r['sha256']) for r in g['references']]:
  assert sha(path)==expected;checks.append({'path':path,'sha256':expected})
 assert rd(e['receipt'])['status'].startswith('succeeded')
 a=np.array(im.convert('RGB'));x=i*1024
 if i==0:strip[:,:1254]=a
 else:
  alpha=z[f'row04_c{i:02d}_c{i+1:02d}_alpha'].astype(np.uint32);assert alpha.shape==(1254,230)
  strip[:,x:x+230]=((strip[:,x:x+230].astype(np.uint32)*(255-alpha[:,:,None])+a[:,:230].astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
  strip[:,x+230:x+1254]=a[:,230:]
  first[:,x:x+230]=i-1;second[:,x:x+230]=i;weight[:,x:x+230]=alpha[1139:]
  first[:,x+230:x+1254]=i;second[:,x+230:x+1254]=i;weight[:,x+230:x+1254]=0
 provenance.append({'logicalId':s['logicalId'],'native':art(s['native']),'generation':art(s['generationRecord']),'checks':checks,'rowContextX':x,'childPixelToNativeXY':'nativeX = childX + 115 - rowContextX; nativeY = 1139 + childY','actualModel':None,'actualQuality':None})
halo=strip[1139:,115:4211];ctx=np.array(Image.open(selected['context']['path']).convert('RGB'));core=np.array(Image.open(selected['candidate']['path']).convert('RGB'))
assert np.array_equal(ctx[115:4211,115:4211],core)
assert np.array_equal(halo,ctx[4211:4326,115:4211])
origctx=np.array(Image.open(m['context']['path']).convert('RGB'));assert sha(m['context']['path'])==m['context']['sha256']
# First230 rows are the historical vertical blend with row3; the entire
# region used here starts at native499 and is beyond that overlap.
assert np.array_equal(strip[230:],origctx[3302:4326])
upper=strip[499:1139,115:4211]
same=np.all(upper==core[3456:4096],axis=2)
png(D/'native-row4-4326x1254-replay.png',strip);png(D/'south-halo-4096x115-exact.png',halo)
with (D/'halo-native-contributors.npz').open('xb') as f:np.savez_compressed(f,first_source_index=first[:,115:4211],second_source_index=second[:,115:4211],second_source_weight=weight[:,115:4211])
cur=rd(T/'candidate/latest-assembly.json');assert cur['candidate']['sha256']=='66848fcdb5ff648de5f448588dbb4cd1c70693dee07ea43f3b15da0ed353d377'
child=np.array(Image.open(cur['candidate']['path']).convert('RGB'))
diagnostics=[]
for x in [630,1600,2842]:
 join=np.concatenate([core[3456:4096,x:x+1254],child[:614,x:x+1254]],axis=0)
 png(D/f'current-joined-x{x}-1254.png',join)
 continuation=join.copy();continuation[640:755]=halo[:,x:x+1254];png(D/f'full-halo-diagnostic-x{x}-1254.png',continuation)
 diagnostics.append({'x':x,'current':art(D/f'current-joined-x{x}-1254.png'),'full115Diagnostic':art(D/f'full-halo-diagnostic-x{x}-1254.png'),'notCandidate':True})
report={'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'provenance_pass_art_qa_pending','selectedNeighbor':selected['candidate'],'selectedNeighborContext':selected['context'],'originalAssemblyManifest':baseptr['manifest'],'originalAssemblyContext':m['context'],'nativeSources':provenance,'savedHorizontalSeamAlpha':seams,'nativeRow4Replay':art(D/'native-row4-4326x1254-replay.png'),'halo':art(D/'south-halo-4096x115-exact.png'),'perPixelContributors':art(D/'halo-native-contributors.npz'),'contributorFormula':'For each child x,y: sourceA/sourceB read indexes0..3 into nativeSources; nativeX=x+115-1024*index, nativeY=1139+y. mix (A*(255-w)+B*w+127)//255. Every overlap uses original row4 alpha. Outside overlap weight0 with same source indexes.','selectedHaloEqualsReplayedNativePixels':True,'selectedCoreMatchesItsContext':True,'selectedLast640CoreEqualsOriginalRow4ForX630Onward':bool(same[:,630:].all()),'mismatchingPixelsLast640OutsideFrozenCorner':int((~same[:,630:]).sum()),'baseChild':cur['candidate'],'diagnostics':diagnostics,'frozenRegion':[0,0,630,630],'newImagegenCalls':0,'resized':False,'sourceRGBChanged':False,'neighborWritten':False,'formalAccepted':False}
put(D/'provenance.json',report);print(json.dumps({'proof':art(D/'provenance.json'),'allHaloPixelsExact':True,'unmodifiedCoreContinuityX630Onward':report['selectedLast640CoreEqualsOriginalRow4ForX630Onward'],'sourcePaths':[s['native']['path'] for s in provenance]},indent=2))


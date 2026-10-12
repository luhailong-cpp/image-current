from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012';Q=R/'local-qa';N=T.parent/'r14_c13'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
mp=N/'candidate/r14_c13-assembly-adae1ee1a52acb231d63.json';m=read(mp);s=[v for v in m['nativeSources'] if v['logicalId'].startswith('p04_')];z=np.load(m['seamPathsAndAlpha']['path']);assert sha(m['seamPathsAndAlpha']['path'])==m['seamPathsAndAlpha']['sha256']
sources=[];strip=np.zeros((1254,4326,3),np.uint8)
for i,v in enumerate(s):
 assert sha(v['native'])==v['nativeSha256'];im=Image.open(v['native']);assert im.size==(1254,1254);a=np.asarray(im.convert('RGB'))
 g=read(v['generationRecord']);assert sha(v['generationRecord'])==v['generationRecordSha256'];assert g['actualModel'] is None and g['actualQuality'] is None
 ev=g['evidence'];checks=[]
 for path,expected in [(ev['receipt'],ev['receiptSha256']),(ev['request'],ev['requestSha256']),(ev['preparation'],ev['preparationSha256']),(ev['originalOutputPath'],ev['originalSha256']),(g['prompt'],g['promptSha256'])]+[(r['path'],r['sha256']) for r in g['references']]:
  assert sha(path)==expected;checks.append({'path':path,'sha256':expected})
 if i==0:strip[:,:1254]=a
 else:
  x=i*1024;alpha=z['row04_c%02d_c%02d_alpha'%(i,i+1)].astype(np.uint32);left=strip[:,x:x+230].astype(np.uint32);strip[:,x:x+230]=((left*(255-alpha[:,:,None])+a[:,:230].astype(np.uint32)*alpha[:,:,None]+127)//255).astype('uint8');strip[:,x+230:x+1254]=a[:,230:]
 sources.append({'logicalId':v['logicalId'],'native':info(v['native']),'size':[1254,1254],'generationRecord':info(v['generationRecord']),'provenanceChecks':checks,'sourceCropRelevantToHalo':[0,1139,1254,1254],'actualModel':None,'actualQuality':None})
halo=strip[1139:1254,115:4211];ctx=N/'candidate/r14_c13-context-4326-north-v6.png';expected=np.asarray(Image.open(ctx).convert('RGB'))[4211:4326,115:4211];assert np.array_equal(halo,expected)
hp=R/'north-native-halo-row4-replay.png';Image.fromarray(halo).save(hp)
record={'tile':'r15_c13','reusedNeighbor':'r14_c13','status':'all_halo_pixels_exactly_replayed_from_four_real_native_sources','baseAssembly':info(mp),'nativeSources':sources,'horizontalRowAlpha':m['seamPathsAndAlpha'],'sourceCoreHaloContext':info(ctx),'sourceHaloCrop':[115,4211,4211,4326],'row4ReplayCrop':[115,1139,4211,1254],'replayedHalo':info(hp),'allPixelsExact':True,'allPromptRequestReferenceReceiptOriginalHashesVerified':True,'resized':False,'sourceRGBChanged':False,'imagegenCalled':False,'neighborFilesWritten':False};out=Q/'native-halo-provenance-verification.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'proof':info(out),'allPixelsExact':True,'realNativeCount':4,'replayedHalo':info(hp)},indent=2))

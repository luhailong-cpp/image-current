"""Finalize native-only repairs with exhaustive per-pixel source provenance."""
from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib, shutil, datetime

R = Path(__file__).parent
Q = R / 'qa' / 'r11_c12-v02'
Q.mkdir(exist_ok=True)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d): Path(p).write_text(json.dumps(d, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
base = R/'tiles/r11_c12.candidate-v01.png'
stage = R/'tiles/r11_c12.candidate-deckjoin_v01-ownership.png'
final = R/'tiles/r11_c12.candidate-v02.png'
assert not final.exists(), 'Version already exists; do not overwrite'
oldim = Image.open(base).convert('RGB')
im = Image.open(stage).convert('RGB')
assert im.size == oldim.size == (4096,4096)
actual = np.asarray(im)
ids = np.full((4096,4096),255,dtype=np.uint8)
coverage = np.zeros((4096,4096),dtype=np.uint8)
sources = []
selected = read(R/'selected-native-r11_c12.json')
for i,e in enumerate(selected['entries']):
    p = Path(e['file']); assert sha(p)==e['sha256']
    native = Image.open(p); assert native.size==(1254,1254)
    x0,y0,x1,y1 = e['destinationBox']; sx0,sy0,sx1,sy1 = e['sourceCrop']
    assert (x1-x0,y1-y0)==(sx1-sx0,sy1-sy0)
    ids[y0:y1,x0:x1] = i; coverage[y0:y1,x0:x1] += 1
    sources.append({'id':i,'file':str(p),'sha256':sha(p),'nativePixels':[1254,1254],
                    'tileToNativeOffset':[sx0-x0,sy0-y0],'generationRecord':e['record'],
                    'generationRecordSha256':sha(e['record'])})
assert len(sources)==16 and np.all(coverage==1)
repairs = []
for name in ['r11_c12_railjoin_v02','r11_c12_deckjoin_v01']:
    r = read(R/'qa'/f'{name}-ownership'/'source-replay.json')
    localp = Path(r['sourceIdMap']); assert sha(localp)==r['sourceIdMapSha256']
    m = np.asarray(Image.open(localp)) == 1
    x0,y0,x1,y1 = r['targetTileBox']; height=min(y1,4096)-y0
    i=len(sources); region=ids[y0:y0+height,x0:x1]; region[m[:height]]=i
    p=Path(r['native']); recp=Path(str(p)+'.generation.json'); rec=read(recp)
    assert sha(p)==r['nativeSha256']==rec['sha256']
    assert Image.open(p).size==(1254,1254)
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert sha(rec['prompt'])==rec['promptSha256']
    refs=[]
    for ref in rec['references']:
        assert sha(ref['file'])==ref['sha256']
        refs.append({'file':ref['file'],'sha256':ref['sha256'],'replayVerified':True})
    receiptp=R/rec['evidence']['toolReceipt']; receipt=read(receiptp)
    assert receipt['model'] is None and receipt['quality'] is None
    args=receipt['submittedArguments']
    assert args['prompt']==Path(rec['prompt']).read_text(encoding='utf-8')
    assert args['referenced_image_paths']==[x['file'] for x in rec['references']]
    assert args['transparent_background'] is False
    sources.append({'id':i,'file':str(p),'sha256':sha(p),'nativePixels':[1254,1254],
                    'tileToNativeOffset':[-x0,-y0],'generationRecord':str(recp),
                    'generationRecordSha256':sha(recp),'ownershipEvidence':str(R/'qa'/f'{name}-ownership'/'source-replay.json')})
    repairs.append({'native':str(p),'sha256':sha(p),'generationRecord':str(recp),
                    'receipt':str(receiptp),'receiptSha256':sha(receiptp),
                    'promptSha256':rec['promptSha256'],'references':refs,
                    'actualModel':None,'actualQuality':None,'submittedArgumentsVerified':True})
assert np.all(ids<18)
for s in sources:
    yy,xx=np.where(ids==s['id']); dx,dy=s['tileToNativeOffset']
    nx=xx+dx; ny=yy+dy
    assert nx.min()>=0 and ny.min()>=0 and nx.max()<1254 and ny.max()<1254
    arr=np.asarray(Image.open(s['file']).convert('RGB'))
    assert np.array_equal(actual[yy,xx],arr[ny,nx]),s['file']
    s['selectedPixelCount']=len(xx);s['exactPixelReplayVerified']=True
assert sum(s['selectedPixelCount'] for s in sources)==4096*4096
idp=Q/'source-id.png';Image.fromarray(ids).save(idp)
shutil.copy2(stage,final);assert sha(final)==sha(stage)
manifest={'tile':'r11_c12','createdAt':stamp,'candidate':str(final),'sha256':sha(final),
          'nativePixels':[4096,4096],'baseCandidate':str(base),'baseSha256':sha(base),
          'sourceIdMap':str(idp),'sourceIdMapSha256':sha(idp),'sources':sources,
          'sourceCount':18,'selectedPixelCount':4096*4096,'exactPixelReplayVerified':True,
          'operations':'Each source-ID chooses the unmodified native pixel at the same world coordinate. No resize, blend, filter or generated colors.',
          'formalAcceptedCount':0,'status':'pending_final_visual_review'}
write(R/'selected-native-r11_c12-repaired-v02.json',manifest)
write(str(final)+'.sources.json',manifest)
write(Q/'source-audit.json',{'candidateSha256':sha(final),'nativeSources':18,
                          'allSelectedSourceHashesVerified':True,'exactPixelReplayVerified':True,
                          'newNativeEvidence':repairs,'formalAcceptedCount':0})
crops=[]
for e in read(R/'qa/r11_c12-v01/seams.json')['entries']:
    box=e['sourceCrop'];path=Q/(e['id']+'.png'); crop=im.crop(box);crop.save(path)
    unchanged=crop.tobytes()==oldim.crop(box).tobytes()
    crops.append({'id':e['id'],'sourceCrop':box,'file':str(path),'sha256':sha(path),
                  'identicalToV01':unchanged,'status':'inherited_prior_review' if unchanged else 'pending_visual_review'})
junctions=[]
for r in range(1,4):
    for c in range(1,4):
        x,y=c*1024,r*1024;box=[x-256,y-256,x+256,y+256]
        name=f'junction_{r}{c}';path=Q/(name+'.png');crop=im.crop(box);crop.save(path)
        unchanged=crop.tobytes()==oldim.crop(box).tobytes()
        junctions.append({'id':name,'sourceCrop':box,'file':str(path),'sha256':sha(path),
                          'identicalToV01':unchanged,'status':'inherited_prior_review' if unchanged else 'pending_visual_review'})
boundaries=[]
for name in ['r11_c12_railjoin_v02','r11_c12_deckjoin_v01']:
    r=read(R/'qa'/f'{name}-ownership'/'source-replay.json');x0,y0,x1,y1=r['targetTileBox']
    boxes={'left':[x0-70,y0,x0+370,min(y1,4096)],'right':[x0+884,y0,x1+70,min(y1,4096)],
           'top':[x0,y0-70,x1,y0+140],
           'bottom':[x0,y0+1010,x1,min(y1+70,4096)] if y1<=4096 else [x0,3856,x1,4096]}
    for edge,box in boxes.items():
        path=Q/f'{name}-{edge}.png';im.crop(box).save(path)
        boundaries.append({'id':f'{name}-{edge}','sourceCrop':box,'file':str(path),'sha256':sha(path),
                           'status':'pending_visual_review','externalTileJoin':False})
edges={}
for edge,box in {'north':[0,0,4096,256],'south':[0,3840,4096,4096],
                 'west':[0,0,256,4096],'east':[3840,0,4096,4096]}.items():
    edges[edge]={'sourceCrop':box,'identicalToV01':im.crop(box).tobytes()==oldim.crop(box).tobytes()}
write(Q/'qa-index.json',{'createdAt':stamp,'candidate':str(final),'candidateSha256':sha(final),
                       'seams':crops,'junctions':junctions,'repairBoundaries':boundaries,'outer256Bands':edges})
print(json.dumps({'candidate':str(final),'sha256':sha(final),'changedSeams':[x['id'] for x in crops if not x['identicalToV01']],
                  'changedJunctions':[x['id'] for x in junctions if not x['identicalToV01']],
                  'outer256Bands':edges,'sourceIdMapSha256':sha(idp),'exactReplay':True}))

from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
ROOT=Path('D:/work/image')
B=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def reference(p):return {'file':str(Path(p).resolve()),'sha256':sha(p)}
m=read(D/'crop-manifest.json')
inputs=[x for x in m['inputs'] if x['tile'] in ('r13_c14','r14_c14')]
for t in inputs:
    assert sha(t['file'])==t['sha256']
    progress=read(B/t['tile']/'progress.json')
    assert Path(progress['candidate']).resolve()==Path(t['file']).resolve()
    with Image.open(t['file']) as im:assert im.size==(4096,4096)
repair=B/'r14_c14/repairs/north-far-east-ledges-20261012-v1'
composition=read(repair/'composition.json')
qa=read(repair/'root-visual-qa-20261013.json')
old=next(x for x in qa['actualNativeEvidence'] if x.get('role')=='x2842 context and adoption starts x2874')
assert sha(old['path'])==old['sha256']
assert composition['pasteBoxIn4096']==[2842,0,4096,300]
assert composition['nativeCrop']==[0,640,1254,940]
assert old['cropBoxInJoined1254']==[0,512,420,1012]
# joined1254 origin: child x2842, child y-640. Boundary in joined image is y640.
old_local=[2842+old['cropBoxInJoined1254'][0],old['cropBoxInJoined1254'][1]-640,
           2842+old['cropBoxInJoined1254'][2],old['cropBoxInJoined1254'][3]-640]
old_world=[53248+old_local[0],53248+old_local[1],53248+old_local[2],53248+old_local[3]]
box=[55548,52768,56748,54048] # child-local x2300..3500,y-480..800:1200x1280
out=Image.new('RGB',(1200,1280));parts=[]
for t in inputs:
    w=t['worldBox'];inter=[max(box[0],w[0]),max(box[1],w[1]),min(box[2],w[2]),min(box[3],w[3])]
    local=[inter[0]-w[0],inter[1]-w[1],inter[2]-w[0],inter[3]-w[1]]
    dest=[inter[0]-box[0],inter[1]-box[1]]
    with Image.open(t['file']) as im:out.paste(im.crop(local),dest)
    parts.append({'tile':t['tile'],'sourceSHA256':t['sha256'],'worldBox':inter,'sourceLocalBox':local,'pasteXY':dest})
p=D/'crops/endpoint-current-wide-v01.png';assert not p.exists();out.save(p)
with Image.open(p) as saved:assert saved.tobytes()==out.tobytes()
evidence={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'inputs':inputs,
 'currentProgressEvidence':[reference(B/t['tile']/'progress.json') for t in inputs],
 'oldEndpointReport':reference(repair/'root-visual-qa-20261013.json'),
 'oldIndependentReport':reference(repair/'visual-qa.json'),'composition':reference(repair/'composition.json'),
 'oldEndpointCrop':{'file':old['path'],'sha256':old['sha256'],'pixels':old['pixels'],'cropBoxInJoined1254':old['cropBoxInJoined1254'],
   'joined1254WorldOrigin':[56090,52608],'childRelativeBox':old_local,'worldBox':old_world,
   'coordinateDerivation':'Composition nativeCrop starts y640 and is pasted at child y0; joined core image contains north640 then child614. Thus joined origin child(2842,-640).'},
 'endpointCoordinates':{'contextLeftChildX':2842,'recordedAdoptionStartChildX':2874,'actualChangedPixelStartChildX':composition['verification']['actualChangeBox'][0],
   'worldContextX':56090,'worldRecordedAdoptionX':56122,'worldActualChangedPixelStartX':56123},
 'crop':{'file':str(p),'sha256':sha(p),'pixels':[1200,1280],'worldBox':box,'sourceParts':parts,'trueCoreBoundaryCropY':480,
   'purpose':'Wide native context includes both sides of endpoint and complete old420x500 endpoint inspection box, plus800px of current child depth.',
   'resampled':False,'interpolated':False,'nativePixelScale':1},
 'existingReviewPreserved':reference(D/'review.json'),'newGenerationPerformed':False,'productionFilesModified':False}
with (D/'endpoint-crop-manifest-v01.json').open('x',encoding='utf-8') as f:f.write(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'crop':str(p),'worldBox':box,'oldEndpointWorldBox':old_world,'trueCoreBoundaryCropY':480},ensure_ascii=False,indent=2))

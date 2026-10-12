from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image, ImageChops

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009'
INDEX=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/main-city-game-20261009/east-census/v20261013-01/current-tiles.json'
OUT=Path(__file__).resolve().parent
CROPS=OUT/'crops'
CROPS.mkdir(exist_ok=False)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def savejson(p,d):
    with Path(p).open('x',encoding='utf-8') as f:f.write(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
index=json.loads(INDEX.read_text(encoding='utf-8-sig'))
targets=['r13_c13','r13_c14','r13_c15','r14_c13','r14_c14','r14_c15']
tiles=[]
for name in targets:
    t=next(x for x in index if x['tile']==name);c=t['currentCandidate'];p=Path(c['path'])
    digest=sha(p);assert digest==c['sha256'],(name,digest,c['sha256'])
    with Image.open(p) as im:
        assert im.size==(4096,4096) and im.mode=='RGB'
        dimensions=list(im.size);mode=im.mode
    tiles.append({'tile':name,'file':str(p),'sha256':digest,'pixels':dimensions,'mode':mode,'worldBox':t['worldCoreBox']})

def worldcrop(name,box,rotation=False):
    width,height=box[2]-box[0],box[3]-box[1]
    im=Image.new('RGB',(width,height));parts=[];count=0
    for t in tiles:
        w=t['worldBox'];ix=[max(w[0],box[0]),max(w[1],box[1]),min(w[2],box[2]),min(w[3],box[3])]
        if ix[0]>=ix[2] or ix[1]>=ix[3]:continue
        local=[ix[0]-w[0],ix[1]-w[1],ix[2]-w[0],ix[3]-w[1]];dest=[ix[0]-box[0],ix[1]-box[1]]
        with Image.open(t['file']) as source:piece=source.crop(local)
        im.paste(piece,dest);count+=(ix[2]-ix[0])*(ix[3]-ix[1])
        parts.append({'tile':t['tile'],'sourceSHA256':t['sha256'],'sourceLocalBox':local,'worldBox':ix,'pasteXY':dest})
    assert count==width*height,(name,count,width*height)
    path=CROPS/(name+'.png');im.save(path)
    with Image.open(path) as saved:assert saved.tobytes()==im.tobytes()
    r={'id':name,'file':str(path),'sha256':sha(path),'pixels':[width,height],'worldBox':box,'sourceParts':parts,
       'nativePixelScale':1,'resampled':False,'interpolated':False,'actualViewedThisReview':False,'localVerdict':'pending'}
    if rotation:
        rp=CROPS/(name+'-rotate90ccw.png');rotated=im.transpose(Image.Transpose.ROTATE_90);rotated.save(rp)
        r['displayRotation']={'file':str(rp),'sha256':sha(rp),'pixels':list(rotated.size),'operation':'PIL transpose ROTATE_90; exact pixel permutation, no interpolation',
          'mapping':'Canonical pixel(u,v) -> display pixel(v,319-u). Canonical world=(worldBox.left+u,worldBox.top+v); east/right tile appears above the horizontal seam, west/left below.'}
    return r,im

oldreviewpath=BASE/'southeast/r14_c15/review/assembly-c162322cbdcca7cb2291/visual-qa.json'
oldreview=json.loads(oldreviewpath.read_text(encoding='utf-8-sig'))
entries=[]
for q in range(4):
    start=49152+q*1024
    r,_=worldcrop(f'E-r13_c13-r13_c14-q{q+1}',[53248-160,start,53248+160,start+1024],True)
    r.update(axis='x',boundaryWorldCoordinate=53248,segment=q+1,pair=['r13_c13','r13_c14']);entries.append(r)
for col in (14,15):
    for q in range(4):
        start=(col-1)*4096+q*1024
        r,im=worldcrop(f'N-r13_c{col}-r14_c{col}-q{q+1}',[start,53248-160,start+1024,53248+160])
        r.update(axis='y',boundaryWorldCoordinate=53248,segment=q+1,pair=[f'r13_c{col}',f'r14_c{col}'])
        if col==15:
            e=next(x for x in oldreview['evidence'] if x['id']==f'ext-north-q{q}');p=Path(e['path']);assert sha(p)==e['sha256']
            with Image.open(p) as old:
                assert old.size==(1024,512);center=old.crop((0,96,1024,416));same=center.tobytes()==im.tobytes()
                diffbox=ImageChops.difference(center,im).getbbox()
            r['priorEvidenceComparison']={'report':str(oldreviewpath),'reportSHA256':sha(oldreviewpath),'file':str(p),'sha256':sha(p),
                'priorCropCenterSubset':[0,96,1024,416],'pixelIdentical':same,'changedPixelBoundingBoxInNewCrop':diffbox,
                'priorActuallyViewed':e['actuallyViewedAtOriginalPixelSize'],'priorStatus':e['status'],'priorObservation':e['observation']}
            if same and e['status']=='pass_observed':
                r.update(localVerdict='PASS_LOCAL_MAJOR_GEOMETRY_REUSED_PIXEL_IDENTICAL',reviewMethod='Reuse actual prior native-view evidence after byte-for-byte RGB center crop comparison',actualViewedThisReview=False)
        entries.append(r)
for x in (53248,57344):
    r,_=worldcrop(f'J-{x}-53248',[x-320,53248-320,x+320,53248+320]);r.update(kind='four-tile-junction',junctionWorldXY=[x,53248]);entries.append(r)
changed=[t['tile'] for t in tiles if sha(t['file'])!=t['sha256']]
manifest={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'index':{'file':str(INDEX),'sha256':sha(INDEX)},
 'inputs':tiles,'entries':entries,'inputsUnchangedAfterCropBuild':not changed,'changedInputs':changed,
 'scope':'Three specified boundaries and two junctions only; no deliverable group mosaic because other known existing FAILs remain',
 'mechanicalOperationsOnly':['integer source cropping','same-coordinate paste of true candidate core pixels','optional exact 90-degree rotation'],
 'newGenerationPerformed':False,'productionFilesModified':False,'formalAccepted':False}
savejson(OUT/'crop-manifest.json',manifest)
print(json.dumps({'output':str(OUT),'entries':len(entries),'reused':sum('REUSED' in e['localVerdict'] for e in entries),
 'requiresNewView':[e['id'] for e in entries if e['localVerdict']=='pending'],'inputsUnchanged':not changed},ensure_ascii=False,indent=2))

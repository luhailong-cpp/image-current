"""Freeze a manual 1:1 review of an existing complete baseline; no production writes."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

OUT = Path(__file__).resolve().parent
BASE = OUT.parent/'core-baseline'/'6c2e5c13cfbe255b4af6'
MANIFEST = BASE/'assembly.json'
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
artifacts = {Path(a['file']).name:a for a in manifest['artifacts']}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ox, oy = manifest['coreWorldBox'][:2]
sources = {s['id']:s for s in manifest['inputs']['nativeSources']}
reviewed = [a for a in manifest['artifacts'] if a['kind'] in ('native-pixel-seam-crop','native-pixel-intersection-crop')]
assert len([a for a in reviewed if a['kind']=='native-pixel-seam-crop'])==24
assert len([a for a in reviewed if a['kind']=='native-pixel-intersection-crop'])==9
for a in reviewed:
    assert sha(a['file']) == a['sha256']
    with Image.open(a['file']) as pixels:
        assert list(pixels.size)==a['pixels']
candidate=next(a for a in manifest['artifacts'] if a['kind']=='complete-4k-candidate-unreviewed')
assert sha(candidate['file'])==candidate['sha256']

def wb(tilebox):
    return [ox+tilebox[0],oy+tilebox[1],ox+tilebox[2],oy+tilebox[3]]

def nativebox(patch, box):
    px,py=sources[patch]['coordinates']['contextWorldBox'][:2]
    return [box[0]-px,box[1]-py,box[2]-px,box[3]-py]

def focused(name, crop, target):
    a=artifacts[name]
    with Image.open(a['file']) as original:
        pixels=original.crop(crop)
    dest=OUT/target
    pixels.save(dest)
    with Image.open(dest) as saved:
        assert saved.tobytes()==pixels.tobytes() and saved.size==pixels.size
    tx,ty=a['crop'][:2]
    tilebox=[tx+crop[0],ty+crop[1],tx+crop[2],ty+crop[3]]
    return {'file':str(dest),'sha256':sha(dest),'sourceArtifact':a['file'],
            'sourceArtifactSha256':a['sha256'],'sourceCrop':crop,'tileBox':tilebox,
            'worldBox':wb(tilebox),'nativePixels':list(pixels.size),'resized':False}

step=focused('intersection-r3-c2-100pct.png',[480,500,880,850],'complete-p43-eave-step-100pct.png')
roof1=focused('intersection-r2-c1-100pct.png',[350,430,600,850],'complete-roof-color-r2-c1-100pct.png')
roof2=focused('intersection-r3-c1-100pct.png',[350,50,600,800],'complete-roof-color-r3-c1-100pct.png')
wall=focused('intersection-r2-c3-100pct.png',[130,350,300,550],'complete-wall-horizontal-tone-100pct.png')

measurements=[]
for name,axis,z,start,end in [
 ('intersection-r2-c1-100pct.png','vertical',450,480,850),
 ('intersection-r3-c1-100pct.png','vertical',450,80,750),
 ('intersection-r2-c3-100pct.png','horizontal',450,170,260)]:
    with Image.open(BASE/name) as source:
        pixels=source.convert('RGB')
    if axis=='vertical':
        a,b=(z-1,start,z,end),(z,start,z+1,end)
    else:
        a,b=(start,z-1,end,z),(start,z,end,z+1)
    left,right=pixels.crop(a),pixels.crop(b)
    ma,mb=ImageStat.Stat(left).mean,ImageStat.Stat(right).mean
    measurements.append({'artifact':name,'axis':axis,'coordinate':z,'span':[start,end],
       'adjacentPixelMeanSignedRGBStep':[round(mb[k]-ma[k],4) for k in range(3)],
       'adjacentPixelMeanAbsoluteRGBStep':round(sum(ImageStat.Stat(ImageChops.difference(left,right)).mean)/3,4),
       'interpretation':'diagnostic supporting visible straight discontinuity; not an independent acceptance criterion'})

old=json.loads((OUT/'visual-review.json').read_text(encoding='utf-8'))
known={**old['findings'][0],'id':'FULL-01','knownBeforeThisReview':True,
       'status':'present in this baseline; parent is repairing separately'}
soft={**old['findings'][1],'id':'FULL-05','knownBeforeThisReview':True}
findings=[known,
 {'id':'FULL-02','priority':'P2','status':'repair-required','title':'p43 前后檐口在连续瓦坡上突然形成台阶',
  'sourceIds':['p42','p43'],'primarySource':'p43',
  'primaryNativeBox':[200,225,545,515],
  'primaryWorldBox':[51285,23662,51630,23952],
  'description':'p43 约 x=230 处，左侧瓦当/红檐梁的退后终止线突然跳到右侧更靠前的檐口；上方却是连续同坡瓦列，没有脊、谷或屋面折角解释深度变化。基线四角中呈明显前后两层阶梯。',
  'recommendation':'按同一檐线统一末排瓦长与红檐梁，保留蓝瓦圆头花纹和梁下结构；修复时纳入左邻末排瓦当。修后复核p42/p43竖接缝及p33/p43横接缝。',
  'evidence':[step],
  'parentRequestedCheck':'Confirmed visible eave step near p43 native x=230; final intended architecture is for parent to resolve.'},
 {'id':'FULL-03','priority':'P2','status':'repair-required','title':'左下两排屋瓦沿 x=50176 形成明显颜色断层',
  'sourceIds':['p31','p32','p41','p42'],'primaryWorldSeamX':50176,
  'primaryWorldBoxes':[[50136,22528,50216,22978],[50136,23552,50216,23902]],
  'nativeBoxes':[
      {'source':'p31','box':[1099,115,1139,565]},
      {'source':'p32','box':[115,115,155,565]},
      {'source':'p41','box':[1099,115,1139,465]},
      {'source':'p42','box':[115,115,155,465]}],
  'description':'屋瓦轮廓多数对齐，但色温/亮度在固定拼片竖线突然变化，且跨多条瓦列维持矩形边界；r2-c1与r3-c1四角均明显。',
  'recommendation':'在不移动瓦列、不模糊边缘的前提下统一相邻屋瓦材质与光照；需要覆盖这条竖线的上下连续范围，并在四角复核。',
  'measurements':measurements[:2],'evidence':[roof1,roof2]},
 {'id':'FULL-04','priority':'P3','status':'minor-material-continuity','title':'y=22528 墙面和红柱的轻微水平色阶',
  'sourceIds':['p22','p23','p24','p32','p33','p34'],'primaryWorldSeamY':22528,
  'inspectionWorldBoxes':[[51030,22428,51470,22628],[51904,22428,52074,22628]],
  'description':'r2-c2及r2-c3四角可见沿核心区横切线的细浅明暗边，墙体/窗棂/柱线几何连续；程度低于左下屋瓦竖直色阶。',
  'recommendation':'局部统一墙灰纹理和红柱光照，不改变窗格、柱边或阴影几何；无需因此整块重画。',
  'measurements':measurements[2:],'evidence':[wall]},soft]

notes={
 'vertical-p31-p32-join-100pct.png':['FULL-03'],
 'vertical-p41-p42-join-100pct.png':['FULL-03'],
 'vertical-p42-p43-join-100pct.png':['FULL-02'],
 'horizontal-p33-p43-join-100pct.png':['FULL-02'],
 'horizontal-p22-p32-join-100pct.png':['FULL-03','FULL-04'],
 'horizontal-p23-p33-join-100pct.png':['FULL-04'],
 'horizontal-p24-p34-join-100pct.png':['FULL-04'],
 'vertical-p22-p23-join-100pct.png':['FULL-01'],
 'horizontal-p13-p23-join-100pct.png':['FULL-01'],
 'vertical-p11-p12-join-100pct.png':['FULL-05'],
 'intersection-r1-c2-100pct.png':['FULL-01'],
 'intersection-r2-c1-100pct.png':['FULL-03'],
 'intersection-r3-c1-100pct.png':['FULL-03'],
 'intersection-r3-c2-100pct.png':['FULL-02'],
 'intersection-r2-c2-100pct.png':['FULL-04'],
 'intersection-r2-c3-100pct.png':['FULL-04']}
review_entries=[]
for a in reviewed:
    name=Path(a['file']).name
    issues=notes.get(name,[])
    review_entries.append({'file':a['file'],'sha256':a['sha256'],'kind':a['kind'],
      'tileBox':a['crop'],'worldBox':wb(a['crop']),'pixels':a['pixels'],
      'sourceIds':a['sourceIds'],'viewedAtOriginalPixels':True,
      'findingIds':issues,'status':'see linked finding; some defects lie inside context crop rather than exactly on core cut' if issues else 'no additional P2 geometry or color defect identified in this crop'})
result={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),
  'tile':'r06_c13','baseline':{'assembly':str(MANIFEST),'assemblySha256':sha(MANIFEST),
    'createdAt':manifest['createdAt'],'inputSignature':manifest['inputSignature'],
    'candidate':candidate['file'],'candidateSha256':candidate['sha256'],'pixels':[4096,4096]},
  'reviewScope':'all 24 native-pixel seam joins and all 9 native-pixel intersections from the named baseline',
  'method':'read existing original-resolution crops, compare geometry/material continuity; focused crops are exact integer subcrops only',
  'coordinateConvention':'[x0,y0,x1,y1), right/bottom exclusive; world refers to art-canvas pixels',
  'counts':{'seamJoinsReviewed':24,'intersectionsReviewed':9,'knownP2':1,'newP2':2,'P3IncludingPreviouslyKnown':2},
  'allReviewedCropHashesMatchManifest':True,'baselineCandidateHashVerified':True,
  'findings':findings,'reviewedArtifacts':review_entries,
  'decision':'Do not mark this baseline internally accepted until FULL-01/FULL-02/FULL-03 are repaired and rechecked.',
  'limits':['Parent p23 repair is not included or awaited.','External tile borders are outside this review.','No runtime, client or model research performed.'],
  'writes':{'directory':str(OUT),'productionFilesModified':False,'nativeModified':False,'selectionModified':False,'candidateModified':False,'progressModified':False,'imageGenerationCalls':0}}
target=OUT/'complete-baseline-review-6c2e5c13.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(target),'reviewedCrops':len(review_entries),'newP2':2,'candidateSha256':candidate['sha256']},ensure_ascii=False))

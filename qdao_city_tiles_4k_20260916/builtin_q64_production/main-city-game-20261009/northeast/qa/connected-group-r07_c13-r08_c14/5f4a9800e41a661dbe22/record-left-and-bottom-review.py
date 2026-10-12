from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
M=D/'manifest.json';m=read(M)
notes={
'south-west-east-1-100pct.png':'Tree leaves, branch strokes and lower ground continue through x512; no clipped leaf or abrupt stem end at shared edge.',
'south-west-east-2-100pct.png':'Red chest lid, diagonal gold frame, front panels and shadows continue through x512; no broken ornament or double edge.',
'south-west-east-3-100pct.png':'Chest base and diagonal stone courses continue through x512. Horizontal blue road upper/lower borders remain continuous.',
'south-west-east-4-100pct.png':'Blue paving band, cream edging and lower diagonal slab joints continue through x512. Foliage crosses naturally in lower portion.',
'west-north-south-1-100pct.png':'Lantern crown, gold rib, ground and rear brickwork continue through y512 with coherent contours and shading.',
'west-north-south-2-100pct.png':'Brick course diagonals, right red column and wall surface cross y512 without a structural step.',
'west-north-south-3-100pct.png':'Red column and pale wall continue across y512. Window sill above and brick base below remain coherent; no seam cut.',
'west-north-south-4-100pct.png':'Window sill shadow, plaster and eastern leaf tip cross y512 coherently in this exact snapshot. Rightmost45px may change under parent leaf-tip append; review must be refreshed if pixels change.'
}
sources={}
for tile,v in m['sources'].items():
 current=sha(v['file']);sources[tile]={**v,'currentFileSha256AtReport':current,'matchesSnapshot':current==v['sha256']}
records=[]
for e in m['exports']:
 name=Path(e['file']).name
 if name not in notes:continue
 actual=sha(e['file']);assert actual==e['sha256']
 im=Image.open(e['file']).convert('RGB');assert list(im.size)==e['dimensions']
 vertical=name.startswith('south-')
 pairs=e['operation']['integerCrops'];reconstruction=Image.new('RGB',im.size)
 pairs_match=True
 for i,pair in enumerate(pairs):
  tile,box=next(iter(pair.items()));pairs_match &= sources[tile]['matchesSnapshot']
  crop=Image.open(sources[tile]['file']).convert('RGB').crop(box)
  reconstruction.paste(crop,(512*i,0) if vertical else (0,512*i))
 if pairs_match:assert ImageChops.difference(im,reconstruction).getbbox() is None
 firstbox=next(iter(pairs[0].values()))
 wb=[52736,28672+firstbox[1],53760,28672+firstbox[3]] if vertical else [49152+firstbox[0],28160,49152+firstbox[2],29184]
 records.append({'file':e['file'],'sha256':actual,'dimensions':e['dimensions'],'worldBox':wb,'kind':e['kind'],'operation':e['operation'],'actuallyViewed':True,'inspection':'native-resolution raster via view_image, entire window','visualStatus':'passed_for_this_snapshot','finding':notes[name],'P2':[],'currentSourceCropsReconstructedPixelIdentical':True if pairs_match else None,'pendingPossibleSourceChange':name=='west-north-south-4-100pct.png'})
assert len(records)==8
report={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'reviewer':'native_quality','mode':'read-only visual and source-hash review; no generation or art changes','snapshotSignature':m['signature'],'manifest':{'file':str(M),'sha256':sha(M)},'scope':['r08_c13 east to r08_c14 west, four native windows','r07_c13 south to r08_c13 north, four native windows'],'sourceCandidates':sources,'actualViewedWindowCount':8,'passedForThisSnapshot':8,'stableReviewedWindowCount':7,'requiresConditionalRecheck':['west-north-south-4-100pct.png after possible r07_c13 eastmost45px leaf-tip append; if unchanged SHA, same review applies'],'P2Count':0,'P2Coordinates':[],'P3':[{'priority':3,'status':'record only','description':'Minor mineral texture and tonal variation in paving; no geometry repair required at shared seam. Blue band edges are continuous.','windows':['south-west-east-3-100pct.png','south-west-east-4-100pct.png']}],'windows':records,'formalAcceptedCount':0,'limits':'This record covers these8 snapshot windows only, not parent-reviewed remaining9 windows or future candidate changes.'}
(D/'left-and-bottom-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reviewFile':str(D/'left-and-bottom-review.json'),'reviewSha256':sha(D/'left-and-bottom-review.json'),'viewed':8,'P2':0,'allSourcesStillMatch':all(v['matchesSnapshot'] for v in sources.values()),'conditionalRecheck':'west-north-south-4'},ensure_ascii=False))


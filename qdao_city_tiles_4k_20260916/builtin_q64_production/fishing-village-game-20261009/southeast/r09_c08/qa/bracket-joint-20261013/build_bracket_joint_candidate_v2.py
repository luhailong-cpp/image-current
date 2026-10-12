from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
Q=Path(__file__).resolve().parent;Z=Q.parents[2];T=Z/'r09_c08'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
base=np.asarray(Image.open(Q/'joint-input-v1-1254.png').convert('RGB')).copy()
raw1=np.asarray(Image.open(Q/'bracket-v1-raw.png').convert('RGB'))
raw2=np.asarray(Image.open(Q/'bracket-v2-raw.png').convert('RGB'))
poly=[(617,222),(651,212),(725,239),(731,250),(859,304),(861,411),(817,478),(604,478),(604,271)]
# These binary masks select actual AI pixels; they never draw artwork.
m1=Image.new('L',(1254,1254));ImageDraw.Draw(m1).polygon(poly,fill=255)
m2=Image.new('L',(1254,1254));d=ImageDraw.Draw(m2)
d.rectangle((604,452,730,521),fill=255)
d.rectangle((604,522,634,539),fill=255)
a1=np.asarray(m1)>0;a2=np.asarray(m2)>0;union=a1|a2
result=base.copy();result[a1]=raw1[a1];result[a2]=raw2[a2]
assert np.array_equal(result[~union],base[~union])
assert np.array_equal(result[540:],base[540:])
for name,im in [('upper-bracket-mask-v2.png',m1),('cup-mask-v2.png',m2),('joint-mask-v2.png',Image.fromarray(union.astype('uint8')*255)),('joint-candidate-v2-1254.png',Image.fromarray(result))]:
    p=Q/name;assert not p.exists();im.save(p)
rows=[]
plan=read(T/'coordinate-plan.json');patches={p['id']:p for p in plan['patches']}
expected={'p43':'1a3a552d30b455ecbd3277f7543510df413177a10c05a19250626356fb1612e4','p44':'65460e7999a2f127e892daaa8772217be8c78d6f72db5da66293ac9bb5ae5720'}
native_candidates={}
for pid in ['p43','p44']:
    original=T/'native'/f'{pid}-v2.png';assert sha(original)==expected[pid]
    a=np.asarray(Image.open(original).convert('RGB')).copy();b=a.copy();mask=np.zeros((1254,1254),bool)
    nx,ny=patches[pid]['globalBox'][:2];fx,fy=31117,35840
    x0,y0,x1,y1=max(nx,fx),max(ny,fy),min(nx+1254,fx+1254),min(ny+1254,fy+1254)
    fm=union[y0-fy:y1-fy,x0-fx:x1-fx]
    view=a[y0-ny:y1-ny,x0-nx:x1-nx]
    view[fm]=result[y0-fy:y1-fy,x0-fx:x1-fx][fm]
    mask[y0-ny:y1-ny,x0-nx:x1-nx]=fm
    assert np.array_equal(a[~mask],b[~mask])
    p=Q/f'{pid}-bracket-joint-v2-native.png';Image.fromarray(a).save(p)
    mp=Q/f'{pid}-bracket-joint-v2-mask.png';Image.fromarray(mask.astype('uint8')*255).save(mp)
    native_candidates[pid]=a
    rows.append(dict(patch=pid,original=str(original),originalSha256=expected[pid],file=str(p),sha256=sha(p),
       nativeDimensions=[1254,1254],globalBox=patches[pid]['globalBox'],mask=str(mp),maskSha256=sha(mp),
       changedPixels=int(np.any(a!=b,axis=2).sum()),outsideMaskUnchanged=True,sourceResampling=False,
       sourceBlur=False,sourcePixelBlending=False,sourceCoordinateMovement=False,canonicalModified=False))
seam=np.concatenate([native_candidates['p43'][115:1139,883:1139],native_candidates['p44'][115:1139,115:371]],axis=1)
Image.fromarray(seam).save(Q/'p43--p44-bracket-joint-v2-100pct.png')
qa=[]
for name,box in [('all-boundaries',[550,170,910,600]),('cup-stem',[580,435,755,570]),('top-boundary',[580,185,890,340]),('left-boundary',[575,210,655,540]),('right-boundary',[800,260,890,520])]:
    p=Q/f'bracket-v2-{name}-100pct.png';Image.fromarray(result).crop(box).save(p)
    qa.append(dict(file=str(p),sha256=sha(p),frameBox=box,resized=False))
doc=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='candidate_pending_native_visual_review',
 frameGlobalBox=[31117,35840,32371,37094],newBuiltinCalls=2,actualModel=None,actualQuality=None,
 rawSources=[dict(file=str(Q/f'bracket-v{v}-raw.png'),sha256=sha(Q/f'bracket-v{v}-raw.png')) for v in [1,2]],
 maskDefinitions=dict(upperPolygon=poly,cupRectangleHalfOpen=[604,452,731,522],ghostRemovalRectangleHalfOpen=[604,522,635,540]),
 operation='Exact unscaled AI pixels at same global coordinates through saved binary masks; original pixels outside masks unchanged; no color processing.',
 originalStemFromFrameY540DownUnchanged=True,southernNeighborUnchanged=True,blueRoofOutsideMaskUnchanged=True,
 candidates=rows,qa=qa,joint=str(Q/'joint-candidate-v2-1254.png'),jointSha256=sha(Q/'joint-candidate-v2-1254.png'),
 upperMask=str(Q/'upper-bracket-mask-v2.png'),cupMask=str(Q/'cup-mask-v2.png'),
 canonicalModified=False,formalAccepted=False,adoptRecommended=False)
(Q/'bracket-joint-v2-proof.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidates=rows,proof=str(Q/'bracket-joint-v2-proof.json'))))

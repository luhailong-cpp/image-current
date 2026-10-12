from native_work import *
import numpy as np, subprocess, sys
ident='r04_c12_cross_01_02_jar_paint_repair_v2'
for oid in [ident,'r03_c12_cross_04_02_jar_paint_bridge']:
 p=ZONE/'qa'/f'{oid}.overlay.json';q=read(p)
 assert sha(q['source'])==q['sha256']
 q.update(review='passed_native_geometry_color_and_four_perimeters',reviewedAtUtc=now(),reviewerEvidence='root direct100% inspection of four outer edges and actual4K boundary; center reviewed from full native')
 write(p,q)
p=ZONE/'native'/f'{ident}.png.generation.json';rec=read(p)
rec.update(status='usable',internalSeams='passed smooth jar paint and continuous paving',externalSeams='passed four overlay perimeters and paired4K boundary',selectedCoverage='two complementary upper256/lower768 native subcrops')
write(p,rec)
tid='r03_c12';p=ZONE/'tiles'/f'{tid}.png';d=read(p.with_suffix('.png.derivation.json'))
assert d['sha256']=='0405a72d05a7e7cb6982dde405eb6aa1188079af02c77848bba5940f283292e1'
hist=ZONE/'qa/history';hist.mkdir(exist_ok=True)
for src in [p,p.with_suffix('.png.derivation.json')]:
 dst=hist/('0405a72d05a7-'+src.name)
 if not dst.exists():shutil.copy2(src,dst)
cores=[[None]*4 for _ in range(4)]
for s in d['sources']:
 x,y=s['tileLocalPaste'];cores[y//1024][x//1024]=s['id']
overlay=[]
for o in d['requiredOverlays']:
 oid=Path(o['source']).stem;overlay.append(oid);q=ZONE/'qa'/f'{oid}.overlay.json'
 if not q.exists():write(q,o)
overlay.append('r03_c12_cross_04_02_jar_paint_bridge')
write(ZONE/f'selection-{tid}.json',{'tileId':tid,'cores':cores,'overlays':overlay,'priorRevision':d['sha256']})
subprocess.run([sys.executable,str(ZONE/'assemble_tile.py'),tid],check=True)
p=ZONE/'tiles'/f'{tid}.png';n=read(p.with_suffix('.png.derivation.json'))
a=np.array(Image.open(hist/'0405a72d05a7-r03_c12.png'));b=np.array(Image.open(p));mask=np.zeros((4096,4096),bool);mask[3840:4096,1536:2560]=True
assert not np.any(np.any(a!=b,axis=2)&~mask)
re=Image.new('RGB',(4096,4096))
for s in n['sources']:re.paste(Image.open(s['file']).crop(s['coreCrop']),s['tileLocalPaste'])
for s in n['requiredOverlays']:re.paste(Image.open(s['source']).crop(s['coreCrop']),s['tileLocalPaste'])
assert np.array_equal(np.array(re),b)
review={'tileId':tid,'sha256':sha(p),'status':'passed_internal_visual_and_native_provenance','reviewedAtUtc':now(),'scope':'Prior whole-tile review retained for unchanged pixels. Changed bottom256 x1536..2560 visually inspected with cross-boundary companion; four outer edges and actual4K seam passed.','priorDerivation':(hist/'0405a72d05a7-r03_c12.png.derivation.json').as_posix(),'overlay':'r03_c12_cross_04_02_jar_paint_bridge','pixelDifferenceOutsideChangedRectangle':0,'nativeRebuildDifference':0,'unchangedLeftRightTopBoundaries':True,'pairedLowerOverlay':ident,'formalAccepted':False,'actualModel':None,'actualQuality':None}
write(ZONE/'qa/r03_c12-jar-bridge-review.json',review)
n.update(internalReview='passed',status='internal_candidate_passed',reviewRecord=(ZONE/'qa/r03_c12-jar-bridge-review.json').as_posix());write(p.with_suffix('.png.derivation.json'),n)
for tids,name,size in [(['r03_c12','r03_c13'],'r03_c12-r03_c13-adjacent-preview.png',(2048,1024)),(['r03_c12','r03_c13','r03_c14'],'r03_c12-c14-contiguous-preview.png',(3072,1024))]:
 im=Image.new('RGB',(4096*len(tids),4096))
 for i,t in enumerate(tids):im.paste(Image.open(ZONE/'tiles'/f'{t}.png'),(i*4096,0))
 im.resize(size,Image.Resampling.LANCZOS).save(ZONE/'qa'/name)
 if len(tids)==2:im.save(ZONE/'qa/r03_c12-r03_c13-adjacent-context.png')
print(json.dumps(review))


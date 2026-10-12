"""Mechanical guide only: full wrong overlap replaced by correct western knot context."""
from pathlib import Path
import json,hashlib,sys,importlib.util
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
 p=Path(p);return p if p.is_absolute() else R/p
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
box=[11648,15104,12902,16358];core=[11763,15219,12787,16243]
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
western=read(R/'work-r04_c03/assembly-plan.json')['sources'];partial=read(R/'work-r04_c04/tiles/r04_c04.first-three-rows.assembly.json')
extra={'sourceId':13,'file':'native/r04_c04_s04_s01_v01.png','generationRecord':'native/r04_c04_s04_s01_v01.png.generation.json','sha256':'986154f1498f6268f6e16edbbae88c31b2b26a26114042e91cb3208ef3c08e8d','generationRecordSha256':'07405401ff47b06273fcb764d8bfc2d14eefb02dc59ac5d8a42f6a1c818abe52'}
registry=[];arrays={}
for tile,entries,off in [('r04_c03',western,0),('r04_c04',partial['sources']+[extra],100)]:
 for e in entries:
  p=path(e['file']);rp=path(e['generationRecord']);g=read(rp);sid=e['sourceId']+off
  assert sha(p)==e['sha256'] and sha(rp)==e['generationRecordSha256']
  a=np.asarray(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3);arrays[sid]=a
  registry.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':g['globalNativeBox']})
rows=[];rowids=[]
for rr in range(4):
 a=arrays[rr*4+1];ids=np.full((1254,1254),rr*4+1,np.uint8)
 for cc in range(1,4):
  sid=rr*4+cc+1;a,ids,_=h.append_hard(a,ids,arrays[sid],np.full((1254,1254),sid,np.uint8),'guide-left-row')
 rows.append(a);rowids.append(ids)
left=rows[0];li=rowids[0]
for rr in range(1,4):
 a,ids,_=h.append_hard(left.transpose(1,0,2),li.T,rows[rr].transpose(1,0,2),rowids[rr].T,'guide-left-stack');left=a.transpose(1,0,2);li=ids.T
oldleft=np.asarray(Image.open(R/'work-r04_c03/output/r04_c03.candidate.png').convert('RGB'))
assert np.array_equal(left[115:4211,115:4211],oldleft)
right=np.asarray(Image.open(partial['candidate']).convert('RGB'));ri=np.asarray(Image.open(partial['sourceIdMap']))+100
assert sha(partial['candidate'])==partial['sha256'] and sha(partial['sourceIdMap'])==partial['sourceIdSha256']
guide=np.empty((1254,1254,3),np.uint8);gids=np.zeros((1254,1254),np.uint8)
# Left fill includes its true 115px eastern halo: retain the complete correct knot near x12296,y15755.
cut=12403-box[0]
guide[:,:cut]=left[box[1]-12173:box[3]-12173,box[0]-8077:12403-8077];gids[:,:cut]=li[box[1]-12173:box[3]-12173,box[0]-8077:12403-8077]
# Right fill uses the already assembled first3 rows above y15360 and explicit v01 below.
ysplit=15360-box[1]
guide[:ysplit,cut:]=right[box[1]-12288:3072,12403-12288:box[2]-12288];gids[:ysplit,cut:]=ri[box[1]-12288:3072,12403-12288:box[2]-12288]
guide[ysplit:,cut:]=arrays[113][15360-15245:box[3]-15245,12403-12173:box[2]-12173];gids[ysplit:,cut:]=113
count=0
for s in registry:
 yy,xx=np.nonzero(gids==s['sourceId'])
 if not len(xx):continue
 bx,by,_,_=s['globalNativeBox'];sx=xx+box[0]-bx;sy=yy+box[1]-by
 assert np.array_equal(guide[yy,xx],arrays[s['sourceId']][sy,sx]);count+=len(xx)
assert count==1254*1254
gp=D/'blue-net-corner-bridge-v01.guide.png';ip=D/'blue-net-corner-bridge-v01.guide-source-id.png';Image.fromarray(guide).save(gp);Image.fromarray(gids).save(ip)
refs=read(R/'native/r04_c04_s04_s01_v01.png.generation.json')['references'][:3]
request_refs=[{'file':str(gp),'sha256':sha(gp),'role':'ONLY framing/edit target; exact coordinate-matched current native pixels; full correct western knot is authoritative'}]+refs
rec={'status':'guide-only-await-root-preview-no-generation','nativeGlobalBox':box,'nativeCoreBox':core,'nativeSize':[1254,1254],'tileBoundaryInGuideX':12288-box[0],'nativePasteBoundaryX':cut,'correctKnotApproxGlobal':[12296,15755],'correctKnotApproxGuide':[648,651],'rightFalseKnotRemovedFromGuideByOwnership':True,'guide':{'file':str(gp),'sha256':sha(gp)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':registry,'mechanicalPixelProvenanceVerified':count,'operation':'Integer native crop+hardpaste only. Western halo owns x<12403; right partial/v01 own x>=12403. No RGB painting, feather, resampling, or new image request.','defectToRedraw':'Whole blue net corner, upper support rope and mesh transition around guide x620..980,y300..1100. Current right strands rise too early; retain one authoritative western knot near guide(648,651), reconnect toward upper-right without displaced/doubled knots.','fixedConnections':{'north':'top115px from existing row3 native pixels','west':'left115px from existing western native pixels','east':'right115px from current right partial/v01 including edge of main pole; preserve post silhouette','south':'bottom115px from current western net and right v01 net native pixels'},'notes':['Sharp paste step near x755 is defect evidence, not a desired edge. Do not freeze this internal step.','All repairs belong inside same global frame; no relocation/zoom. Four outer115px are connection constraints.','This bridge source box spans both tiles. Assembly must insert via one shared global source mask, then crop both tiles; cannot apply separately with independent masks.'],'recommendedReferences':request_refs}
rec['fixedConnections']['south']='Match actual lower edge connections except around the defect crossing near guide x755; that lower crossing may need AI repair and subsequent south-boundary verification.'
rec['notes'].append('Do not freeze all bottom115 pixels indiscriminately: the existing mesh mismatch crosses the bottom near x755. This is explicit unresolved south-connection scope, not a claimed closed repair.')
write(D/'blue-net-corner-bridge-v01.plan.json',rec)
print(json.dumps({'guide':rec['guide'],'globalBox':box,'correctKnotGuide':rec['correctKnotApproxGuide'],'references':request_refs}))

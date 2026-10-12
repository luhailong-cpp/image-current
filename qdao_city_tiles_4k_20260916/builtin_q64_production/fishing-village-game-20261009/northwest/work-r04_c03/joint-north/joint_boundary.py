"""Native-only joint seam diagnostic; writes isolated proposals, never source candidates."""
from pathlib import Path
import json,hashlib,sys,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
 p=Path(p);return p if p.is_absolute() else ROOT/p
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def artifact(p):return {'file':str(p),'sha256':sha(p)}
def png(p,a):Image.fromarray(a).save(p)
spec=importlib.util.spec_from_file_location('native_hard_cut',ROOT/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
up_record=ROOT/'tiles/r03_c03.repair-v5.assembly.json';dn_record=ROOT/'work-r04_c03/output/r04_c03.assembly.json'
up=read(up_record);dn=read(dn_record)
up_file=path(up['candidate']['file']);dn_file=ROOT/'work-r04_c03/output/r04_c03.candidate.png'
up_id_file=path(up['sourceIdMap']['file']);dn_id_file=ROOT/'work-r04_c03/output/r04_c03.source-id.png'
baselines=[artifact(p) for p in [up_file,dn_file,up_id_file,dn_id_file,up_record,dn_record]]
assert sha(up_file)==up['candidate']['sha256']
for e in dn['artifacts']:
 if Path(e['file']).name==dn_file.name:assert sha(dn_file)==e['sha256']
registry=[];arrays={}
for tile,record,offset,origin in [('r03_c03',up,0,(8192,8192)),('r04_c03',dn,len(up['sources']),(8192,12288))]:
 for e in record['sources']:
  sid=e['sourceId']+offset;p=path(e['file']);rp=path(e['generationRecord']);g=read(rp)
  assert sha(p)==e['sha256'] and sha(rp)==e['generationRecordSha256']
  box=g['globalNativeBox'];a=np.asarray(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3)
  arrays[sid]=a
  registry.append({'jointSourceId':sid,'tile':tile,'tileSourceId':e['sourceId'],'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':box,'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'nativeScaleResampled':g.get('nativeScaleResampled'),'route':g.get('route')})
def verify(pixels,ids,origin):
 total=0;counts=[]
 for s in registry:
  yy,xx=np.nonzero(ids==s['jointSourceId'])
  if not len(xx):continue
  bx,by,_,_=s['globalNativeBox'];sx=xx+origin[0]-bx;sy=yy+origin[1]-by
  assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254))
  assert np.array_equal(pixels[yy,xx],arrays[s['jointSourceId']][sy,sx])
  total+=len(xx);counts.append({'jointSourceId':s['jointSourceId'],'pixels':len(xx)})
 assert total==pixels.shape[0]*pixels.shape[1]
 return {'verifiedPixels':int(total),'counts':counts}
old_up=np.asarray(Image.open(up_file).convert('RGB')).copy();old_dn=np.asarray(Image.open(dn_file).convert('RGB')).copy()
ids_up=np.asarray(Image.open(up_id_file)).copy();ids_dn=np.asarray(Image.open(dn_id_file)).copy()+len(up['sources'])
before_proof=[verify(old_up,ids_up,(8192,8192)),verify(old_dn,ids_dn,(8192,12288))]
def row(tile,y):
 entries=sorted([s for s in registry if s['tile']==tile and s['globalNativeBox'][1]==y],key=lambda s:s['globalNativeBox'][0]);assert len(entries)==4
 a=arrays[entries[0]['jointSourceId']].copy();ids=np.full((1254,1254),entries[0]['jointSourceId'],np.uint8);cuts=[]
 for s in entries[1:]:
  a,ids,cut=m.append_hard(a,ids,arrays[s['jointSourceId']],np.full((1254,1254),s['jointSourceId'],np.uint8),f'{tile}-row-col{s["tileSourceId"]}');cuts.append(cut)
 return a,ids,cuts
top,topids,topcuts=row('r03_c03',11149);bottom,bottomids,bottomcuts=row('r04_c03',12173)
# Confirm the existing tile ends match these independently replayed native row strips.
assert np.array_equal(old_up[-115:],top[1024:1139,115:4211])
assert np.array_equal(old_dn[:115],bottom[115:230,115:4211])
a=top[1024:1254];b=bottom[:230]
cut,cost=m.minimum_vertical_seam(a.transpose(1,0,2),b.transpose(1,0,2))
take=np.arange(230)[:,None]>=cut[None,:]
band=np.where(take[:,:,None],b,a);bids=np.where(take,bottomids[:230],topids[1024:1254])
assert np.all(np.abs(np.diff(cut))<=1)
band=band[:,115:4211];bids=bids[:,115:4211]
new_up=old_up.copy();new_dn=old_dn.copy();new_ui=ids_up.copy();new_di=ids_dn.copy()
new_up[-115:]=band[:115];new_dn[:115]=band[115:]
new_ui[-115:]=bids[:115];new_di[:115]=bids[115:]
assert np.array_equal(new_up[:-115],old_up[:-115]) and np.array_equal(new_dn[115:],old_dn[115:])
proof=[verify(new_up,new_ui,(8192,8192)),verify(new_dn,new_di,(8192,12288))]
for name,pix,sids in [('r03_c03',new_up,new_ui),('r04_c03',new_dn,new_di)]:
 png(OUT/f'{name}.joint-proposal.png',pix);png(OUT/f'{name}.joint-source-id.png',sids)
png(OUT/'joint-overlap-band.png',band);png(OUT/'joint-overlap-source-id.png',bids)
before=np.concatenate((old_up[-320:],old_dn[:320]),axis=0);after=np.concatenate((new_up[-320:],new_dn[:320]),axis=0)
png(OUT/'boundary-before-100pct.png',before);png(OUT/'boundary-after-100pct.png',after)
for c in range(8):
 png(OUT/f'before-segment-{c+1:02d}.png',before[:,c*512:(c+1)*512]);png(OUT/f'after-segment-{c+1:02d}.png',after[:,c*512:(c+1)*512])
for c in range(1,4):
 x=c*1024;png(OUT/f'cross-{c}-after.png',after[:,x-230:x+230])
path_record={'globalOverlapBox':[8077,12173,12403,12403],'fullPathGlobalYByX':(12173+cut).tolist(),'tileSpanX':[8192,12288],'tileSpanPathGlobalYByX':(12173+cut[115:4211]).tolist(),'samePathForBothTiles':True,'tileSplitGlobalY':12288,'pathCostSumSquaredRGB':cost,'maximumNeighborStep':int(np.abs(np.diff(cut)).max()),'rule':'south native row if globalY>=path[globalX]; north native row otherwise','blend':False,'scaling':False,'colorRewrite':False,'topRowHorizontalCuts':topcuts,'bottomRowHorizontalCuts':bottomcuts}
write(OUT/'joint-path.json',path_record)
stats=[]
for c in range(4):
 sl=slice(c*1024,(c+1)*1024)
 def edge(p):return float(np.abs(p[319,sl].astype(np.int16)-p[320,sl].astype(np.int16)).mean())
 stats.append({'column':c+1,'beforeTileEdgeMeanAbsRGB':edge(before),'afterTileEdgeMeanAbsRGB':edge(after),'note':'Adjacent-pixel change only; not a geometry acceptance metric'})
for e in baselines:assert sha(e['file'])==e['sha256']
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'isolated-joint-proposals-pending-visual-review','formalAccepted':False,'generationUsed':False,'currentCandidatesModified':False,'inFlight':False,'inputBaselines':baselines,'algorithm':artifact(ROOT/'assemble_r03_c03.py'),'script':artifact(Path(__file__)),'sources':registry,'beforePixelProof':before_proof,'proposalPixelProof':proof,'outsideGlobalOverlapUnchanged':True,'globalOverlapCoreSpan':[8192,12173,12288,12403],'path':artifact(OUT/'joint-path.json'),'method':'Replay both row strips at true global coordinates, compute exactly one 4326-long min-error horizontal hard path, split shared result at global y12288 into two isolated tile proposals. RGB copied unaltered from one native source per pixel.','tileEdgeMetrics':stats,'changedPixels':{'r03_c03':int(np.any(new_up!=old_up,axis=2).sum()),'r04_c03':int(np.any(new_dn!=old_dn,axis=2).sum())},'artifacts':[artifact(p) for p in sorted(OUT.glob('*.png'))]}
write(OUT/'joint-assembly.json',manifest)
print(json.dumps({'manifest':artifact(OUT/'joint-assembly.json'),'verifiedPixels':sum(p['verifiedPixels'] for p in proof),'changedPixels':manifest['changedPixels'],'pathGlobalYRange':[int(cut.min()+12173),int(cut.max()+12173)],'edgeMetrics':stats}))

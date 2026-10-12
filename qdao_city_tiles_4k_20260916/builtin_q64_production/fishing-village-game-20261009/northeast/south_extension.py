import argparse, json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
Z=Path(__file__).resolve().parent
C=json.loads((Z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG=Path('D:/work/image/config/image-generation.json')
T='r07_c12'; ORIGIN=(45056,24576); CORE=1024; H=115; N=1254
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def meta(p,role): return {'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p),'role':role}
def coords(p):
 r,c=int(p[-2]),int(p[-1]); x=ORIGIN[0]+(c-1)*CORE; y=(20480 if 'northrepair' in p else ORIGIN[1])+(r-1)*CORE
 return {'patchId':p,'coreGlobalBox':[x,y,x+CORE,y+CORE],'nativeGlobalBox':[x-H,y-H,x+CORE+H,y+CORE+H],'coreLocalBox':[H,H,H+CORE,H+CORE]}
def prepare(p,top=None,left=None,bottom=None,right=None,target=None):
 co=coords(p); box=co['nativeGlobalBox']; s=1254/57344
 im=Image.open(C['layoutReference']).convert('RGB').transform((N,N),Image.Transform.EXTENT,tuple(v*s for v in box),Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png'; im.save(pure)
 sources=[meta(C['layoutReference'],'overview_layout_only')]
 target_path=None
 if target:
  target_path=Path(target);target_path=target_path if target_path.is_absolute() else Z/target_path
  im=Image.open(target_path).convert('RGB');assert im.size==(N,N)
  sources.append(meta(target_path,'edit_target_base'))
 for src,edge in [(left,'left'),(bottom,'bottom'),(right,'right'),(top,'top')]:
  if src:
   src=Path(src); src=src if src.is_absolute() else Z/src
   q=Image.open(src).convert('RGB'); assert q.size==(N,N)
   crop={'left':(1024,0,1254,1254),'top':(0,1024,1254,1254),'bottom':(0,0,1254,230),'right':(0,0,230,1254)}[edge]
   pos={'left':(0,0),'top':(0,0),'bottom':(0,1024),'right':(1024,0)}[edge]
   im.paste(q.crop(crop),pos); sources.append(dict(meta(src,f'exact_native_{edge}_230px'),cropBox=list(crop),pasteAt=list(pos)))
 alias=Z/'guides'/f'{p}.native-edge-layout.png'; im.save(alias)
 guide=Z/'guides'/f'{p}.native-edge-layout-{sha(alias)[:16]}.png'; shutil.copy2(alias,guide)
 write(guide.with_suffix('.derived.json'),{'operation':'layout-only resample plus exact native overlap; not final art','coordinate':co,'sources':sources,'output':meta(guide,'generation_reference')})
 refs=[meta(C['layoutReference'],'wholemap_layout_only'),meta(C['detailStyleReference'],'material_style_only'),meta(C['primaryStyleReference'],'user_primary_art_style_only'),meta(guide,'exact_layout_and_native_edge_constraints')]
 if target_path: refs.append(meta(target_path,'edit_target'))
 context=Z/'guides'/f'{T}.context-layout-only.png'
 # Keep coordinate/native-edge guide last; wider context is inspected separately.
 plan={'patchId':p,'createdAtUtc':now(),'coordinate':co,'referenceImages':refs,'nativeEdgeSources':[s for s in sources if s['role'].startswith('exact_native')],'expectedNativeDimensions':[N,N],'generationRoute':'builtin','actualModel':None,'actualQuality':None}
 write(Z/'records'/f'{p}.plan.json',plan)
 print(json.dumps(plan,ensure_ascii=False))
def ingest(p,src,ver):
 plan=json.loads((Z/'records'/f'{p}.plan.json').read_text(encoding='utf-8')); dst=Z/'native'/f'{p}-{ver}.png'
 if dst.exists(): raise RuntimeError('Refusing overwrite '+str(dst))
 shutil.copy2(src,dst); im=Image.open(dst)
 prompt=Z/'records'/f'{p}-{ver}.prompt.txt'; receipt=Z/'records'/f'{p}-{ver}.receipt.json'
 assert prompt.exists() and receipt.exists()
 rec={'schemaVersion':1,'patchId':p,'generatedAtUtc':now(),'status':'native_candidate_pending_visual_QA','image':meta(dst,'native_generated_image'),'nativeDimensions':list(im.size),'coordinate':plan['coordinate'],'generationRoute':'builtin_image_gen','configTarget':json.loads(CONFIG.read_text(encoding='utf-8-sig')),'submittedSelectors':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'actualEvidence':'Host image_gen exposes no model or quality selectors or return values; PNG metadata is not model evidence.','actualReferenceImages':plan['referenceImages'],'nativeEdgeSources':plan['nativeEdgeSources'],'prompt':meta(prompt,'actual_submitted_prompt'),'receipt':meta(receipt,'actual_tool_receipt'),'sourceHostPath':str(src),'formalAccepted':False}
 write(str(dst)+'.generation.json',rec)
 qa=[]
 if im.size==(N,N):
  for edge in plan['nativeEdgeSources']:
   q=Image.open(edge['path']).convert('RGB'); out=Image.new('RGB',(N,256) if ('top' in edge['role'] or 'bottom' in edge['role']) else (256,N))
   if 'top' in edge['role']:
    out.paste(q.crop((0,1011,N,1139)),(0,0));out.paste(im.crop((0,115,N,243)),(0,128))
   elif 'bottom' in edge['role']:
    out.paste(im.crop((0,1011,N,1139)),(0,0));out.paste(q.crop((0,115,N,243)),(0,128))
   elif 'right' in edge['role']:
    out.paste(im.crop((1011,0,1139,N)),(0,0));out.paste(q.crop((115,0,243,N)),(128,0))
   else:
    out.paste(q.crop((1011,0,1139,N)),(0,0));out.paste(im.crop((115,0,243,N)),(128,0))
   qp=Z/'qa'/f'{p}-{ver}-{edge["role"]}.png';out.save(qp);qa.append(str(qp))
 print(json.dumps({'saved':str(dst),'dimensions':im.size,'sha256':sha(dst),'qa':qa}))
def assemble(ver,north):
 versions={'11':'v3','12':'v3','13':'v1','14':'v1','21':'v1','22':'v1','23':'v1','24':'v2','31':'v1','32':'v1','33':'v1','34':'v1','41':'v1','42':'v2','43':'v2','44':'v2'}
 tile=Image.new('RGB',(4096,4096)); selected={}; contributions=[]
 qa=Z/'qa'/f'{T}-{ver}';qa.mkdir(exist_ok=True)
 for rc,v in versions.items():
  p=f'{T}_p{rc}';src=Z/'native'/f'{p}-{v}.png';im=Image.open(src).convert('RGB');assert im.size==(1254,1254)
  x=(int(rc[1])-1)*1024;y=(int(rc[0])-1)*1024;core=im.crop((115,115,1139,1139));tile.paste(core,(x,y))
  selected[p]=dict(meta(src,'selected_native_candidate'),generationRecord=str(src)+'.generation.json');contributions.append(dict(source=meta(src,'native_source'),cropBox=[115,115,1139,1139],pasteAt=[x,y]))
  core.save(qa/f'core_p{rc}.native-1to1.png')
 out=Z/'tiles'/f'{T}.candidate-{ver}.png'
 if out.exists():raise RuntimeError('Refusing overwrite '+str(out))
 tile.save(out)
 write(str(out)+'.derived.json',{'operation':'16 exact native 1024 core crops and integer pastes; no resize, blend or paint','dimensions':[4096,4096],'origin':ORIGIN,'contributions':contributions,'output':meta(out,'tile_candidate'),'formalAccepted':False})
 selection={'schemaVersion':1,'tile':T,'origin':ORIGIN,'patches':selected,'candidate':meta(out,'tile_candidate'),'formalAccepted':False}
 write(Z/'records'/f'{T}.working-selection.json',selection);write(Z/'records'/f'{T}.selection-{ver}.json',selection)
 edges=[];junctions=[]
 for r in range(4):
  for c in range(1,4):
   name=f'v_p{r+1}{c}_p{r+1}{c+1}';im=tile.crop((c*1024-128,r*1024,c*1024+128,(r+1)*1024));im.save(qa/f'{name}.native-1to1.png');edges.append((name,im))
 for r in range(1,4):
  for c in range(4):
   name=f'h_p{r}{c+1}_p{r+1}{c+1}';im=tile.crop((c*1024,r*1024-128,(c+1)*1024,r*1024+128));im.save(qa/f'{name}.native-1to1.png');edges.append((name,im))
 for offset,kind in [(0,'vertical'),(12,'horizontal')]:
  for group in range(3):
   sheet=Image.new('RGB',(1024,1024))
   for i,(_,im) in enumerate(edges[offset+group*4:offset+group*4+4]):sheet.paste(im,(i*256,0) if kind=='vertical' else (0,i*256))
   sheet.save(qa/f'{kind}-batch{group+1}.native-1to1.png')
 grid=Image.new('RGB',(768,768))
 for r in range(1,4):
  for c in range(1,4):
   name=f'junction_r{r}_c{c}';im=tile.crop((c*1024-128,r*1024-128,c*1024+128,r*1024+128));im.save(qa/f'{name}.native-1to1.png');grid.paste(im,((c-1)*256,(r-1)*256));junctions.append(name)
 grid.save(qa/'junctions-all9.native-1to1.png')
 northmeta=None
 if north:
  n=Path(north);n=n if n.is_absolute() else Z/n;ni=Image.open(n).convert('RGB');assert ni.size==(4096,4096)
  seam=Image.new('RGB',(4096,256));seam.paste(ni.crop((0,3968,4096,4096)),(0,0));seam.paste(tile.crop((0,0,4096,128)),(0,128));seam.save(qa/'north-full4096.native-1to1.png')
  sheet=Image.new('RGB',(1024,1024))
  for c in range(4):
   segment=seam.crop((c*1024,0,(c+1)*1024,256));segment.save(qa/f'north-segment{c+1}.native-1to1.png');sheet.paste(segment,(0,c*256))
  sheet.save(qa/'north-all4segments.native-1to1.png');northmeta=meta(n,'north_neighbor_candidate')
 write(qa/'manifest.json',{'tile':meta(out,'tile_candidate'),'edgeCount':24,'edges':[x[0] for x in edges],'junctionCount':9,'junctions':junctions,'northSource':northmeta,'allQARendersNative1to1':True,'visualInspection':'pending'})
 print(json.dumps({'tile':str(out),'sha256':sha(out),'qa':str(qa),'selectedCount':16,'actualGenerationCount':len(list((Z/'native').glob('r07_c12*.png.generation.json')))}))

def audit_refs():
 results=[];failures=[];replayed=[]
 for recpath in sorted((Z/'native').glob('r07_c12*.png.generation.json')):
  rec=json.loads(recpath.read_text(encoding='utf-8'));checks=[]
  for ref in rec['actualReferenceImages']:
   p=Path(ref['path']);match=p.exists() and sha(p)==ref['sha256'];snapshot=None
   if not match and ref['role']=='exact_layout_and_native_edge_constraints':
    co=rec['coordinate'];s=1254/57344;im=Image.open(C['layoutReference']).convert('RGB').transform((N,N),Image.Transform.EXTENT,tuple(v*s for v in co['nativeGlobalBox']),Image.Resampling.BICUBIC)
    for edge in rec['nativeEdgeSources']:
     assert sha(edge['path'])==edge['sha256'];im.paste(Image.open(edge['path']).convert('RGB').crop(edge['cropBox']),edge['pasteAt'])
    snap=Z/'guides'/f'{rec["patchId"]}.reference-replay-{ref["sha256"][:16]}.png';im.save(snap)
    if sha(snap)==ref['sha256']:
     snapshot=meta(snap,'byte_exact_historical_reference_snapshot');match=True;replayed.append(snapshot)
    else:failures.append({'record':str(recpath),'reference':ref,'replayedSha':sha(snap)})
   elif not match:failures.append({'record':str(recpath),'reference':ref,'reason':'source missing or hash changed'})
   checks.append({'actualReference':ref,'currentlyResolvableExactHash':match,'snapshot':snapshot})
  for key in ['image','prompt','receipt']:
   item=rec[key]
   if not Path(item['path']).exists() or sha(item['path'])!=item['sha256']:failures.append({'record':str(recpath),'item':key,'reason':'hash mismatch'})
  results.append({'generationRecord':str(recpath),'references':checks,'dimensions':rec['nativeDimensions'],'actualModel':rec['actualModel'],'actualQuality':rec['actualQuality']})
 out=Z/'records'/f'{T}.reference-snapshots.json';write(out,{'createdAtUtc':now(),'purpose':'Resolve historical actual-reference paths by stored SHA without modifying submitted arguments or generation records','generationCount':len(results),'records':results,'failures':failures})
 print(json.dumps({'generationCount':len(results),'replayedSnapshotCount':len(replayed),'failures':failures,'audit':str(out)}))

def main():
 a=argparse.ArgumentParser();a.add_argument('op');a.add_argument('patch');a.add_argument('--top');a.add_argument('--left');a.add_argument('--bottom');a.add_argument('--right');a.add_argument('--target');a.add_argument('--source');a.add_argument('--version',default='v1');q=a.parse_args()
 if q.op=='assemble':assemble(q.version,q.source)
 elif q.op=='auditrefs':audit_refs()
 elif q.op=='prepare':prepare(q.patch,q.top,q.left,q.bottom,q.right,q.target)
 elif q.op=='ingest':ingest(q.patch,q.source,q.version)
 elif q.op=='init':write(Z/'records'/f'{T}.coordinates.json',{'tile':T,'origin':ORIGIN,'patches':[coords(f'{T}_p{r}{c}') for r in range(1,5) for c in range(1,5)]})
 elif q.op=='bridge':
  a=Z/'native/r07_c12_northrepair43-v1.png';b=Z/'native/r07_c12_northrepair44-v2.png';can=Image.new('RGB',(2278,1254));can.paste(Image.open(a).crop((0,0,1139,1254)),(0,0));can.paste(Image.open(b).crop((115,0,1254,1254)),(1139,0));im=can.crop((512,0,1766,1254));f=Z/'guides/r07_c12_northrepair-curb-bridge-input.png';im.save(f)
  co={'patchId':q.patch,'nativeGlobalBox':[47501,23437,48755,24691],'coreGlobalBox':[47616,23552,48640,24576],'coreLocalBox':[115,115,1139,1139]}
  sources=[meta(a,'left_native'),meta(b,'right_native')]
  write(f.with_suffix('.derived.json'),{'operation':'exact native 1:1 join at core boundary then crop; no resample','sources':sources,'canvasGlobalOrigin':[46989,23437],'cropBox':[512,0,1766,1254],'output':meta(f,'bridge_edit_target')})
  refs=[meta(C['layoutReference'],'wholemap_layout_only'),meta(C['detailStyleReference'],'material_style_only'),meta(C['primaryStyleReference'],'user_primary_art_style_only'),meta(f,'native_bridge_edit_target')]
  plan={'patchId':q.patch,'createdAtUtc':now(),'coordinate':co,'referenceImages':refs,'nativeEdgeSources':[],'bridgeSources':sources,'expectedNativeDimensions':[1254,1254]};write(Z/'records'/f'{q.patch}.plan.json',plan);print(json.dumps(plan))
 elif q.op=='composebridge':
  a=Z/'native/r07_c12_northrepair43-v1.png';b=Z/'native/r07_c12_northrepair44-v2.png';bridge=Z/'native/r07_c12_northrepair-curb-bridge-v1.png';can=Image.new('RGB',(2278,1254));can.paste(Image.open(a),(0,0));can.paste(Image.open(b),(1024,0));can.paste(Image.open(bridge),(512,0))
  sources=[meta(a,'original_left'),meta(b,'original_right'),meta(bridge,'native_bridge')]
  for col,box in [(43,(0,0,1254,1254)),(44,(1024,0,2278,1254))]:
   out=Z/'native'/f'r07_c12_northrepair{col}-bridge-candidate.png';can.crop(box).save(out);write(str(out)+'.derived.json',{'operation':'exact opaque native composite and crop; no resize/blend','sources':sources,'compositePaste':[{'source':str(a),'at':[0,0]},{'source':str(b),'at':[1024,0]},{'source':str(bridge),'at':[512,0]}],'cropBox':box,'coordinate':coords(f'r07_c12_northrepair{col}'),'output':meta(out,'candidate_not_accepted'),'formalAccepted':False})
  for name,x in [('left-outer',512),('core-seam',1139),('right-outer',1766)]:can.crop((x-128,0,x+128,1254)).save(Z/'qa'/f'r07_c12_northrepair-bridge-{name}.png')
  print('Derived bridge candidates and 3 native boundary QA strips saved')
if __name__=='__main__': main()

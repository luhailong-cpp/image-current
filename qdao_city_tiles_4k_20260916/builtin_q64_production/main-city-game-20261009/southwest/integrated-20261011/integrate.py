"""Merge independently reviewed native overlays in world coordinates, preserving source files."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
D=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'pipeline-tools'))
from quilt import assemble_pixels
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):return np.array(Image.open(p).convert('RGB'))
def info(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
def checked(p,h):
 assert sha(p)==h, 'Hash mismatch: '+str(p)
 return Path(p)
def intersection(a,b):
 r=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
 return r if r[0]<r[2] and r[1]<r[3] else None
def sub(a,box,world):
 x0,y0,x1,y1=box
 return a[y0-world[1]:y1-world[1],x0-world[0]:x1-world[0]]
input_path=Path(sys.argv[1]) if len(sys.argv)>1 else D/'integration-inputs.json'
cfg=read(input_path)
OUT=D/cfg['version'];OUT.mkdir(exist_ok=True)
assert not (OUT/'assembly.json').exists(),'Version already exists.'
before={};after={};cores={};source_records={};allmasks={};worlds={}
for tile,s in cfg['tiles'].items():
 corep=checked(s['candidate'],s['sha256']);core=image(corep);assert core.shape==(4096,4096,3)
 x=(int(tile[5:7])-1)*4096;y=(int(tile[1:3])-1)*4096
 coreworld=[x,y,x+4096,y+4096];ctxworld=[x-115,y-115,x+4211,y+4211];worlds[tile]={'core':coreworld,'context':ctxworld}
 if s.get('context'):
  ctxp=checked(s['context'],s['contextSha256']);ctx=image(ctxp);ctx_record=info(ctxp)
 else:
  assemblyp=ROOT/tile/'output/assembly.json';m=read(assemblyp);arrays={}
  for item in m['nativeSources']:
   p=Path(item['nativeFile']);p=p if p.is_absolute() else ROOT/p
   checked(p,item['nativeSha256']);arrays[(item['row'],item['column'])]=image(p)
  ctx,_=assemble_pixels(arrays,tuple(m['selectedRectangleInclusive']),m['composition']['maximumFeatherRadiusPixels'])
  ctx[115:4211,115:4211]=core
  ctx_record={'replayedNativeAssembly':str(assemblyp),'assemblySha256':sha(assemblyp),'repairedCoreSubstitutedPixelExactly':True,'unchangedOriginalHalos':True,'pixelSha256':hashlib.sha256(ctx.tobytes()).hexdigest()}
 assert ctx.shape==(4326,4326,3) and np.array_equal(ctx[115:4211,115:4211],core)
 before[tile]=ctx;after[tile]=ctx.copy();cores[tile]=core;allmasks[tile]=np.zeros((4326,4326),bool)
 source_records[tile]={'candidate':info(corep),'context':ctx_record,**worlds[tile]}
patches=[]
for entry in cfg['overlays']:
 manifestp=Path(entry['manifest']);m=read(manifestp)
 if entry['kind']=='local-premixed':
  for key in ('base','nativeSource','premixed','pasteMask','proposal'):
   checked(m[key]['file'],m[key]['sha256'])
  patch=image(m['premixed']['file'])
  mask=np.array(Image.open(m['pasteMask']['file']))
  expected=sub(image(m['base']['file']),m['candidateBox'],[0,0,4096,4096])
  patches.append({'id':entry['id'],'worldBox':m['worldBox'],'patch':patch,'mask':mask,'expected':expected,'manifest':str(manifestp),'manifestSha256':sha(manifestp),'patchEvidence':m['premixed'],'maskEvidence':m['pasteMask']})
 elif entry['kind']=='geometry':
  native=m['nativeSource'];checked(native['file'],native['sha256'])
  target=image(checked(m['sourceEvidence']['file'],m['sourceEvidence']['sha256']))
  for p in m['patches']:
   patch=image(checked(p['patch']['file'],p['patch']['sha256']))
   mask=np.array(Image.open(checked(p['mask']['file'],p['mask']['sha256'])))
   expected=sub(target,p['worldBox'],m['sourceWorldBox'])
   patches.append({'id':p['id'],'worldBox':p['worldBox'],'patch':patch,'mask':mask,'expected':expected,'manifest':str(manifestp),'manifestSha256':sha(manifestp),'patchEvidence':p['patch'],'maskEvidence':p['mask']})
 else:
  patch=image(checked(m['premixed'],m['premixedSha256']))
  mask=np.array(Image.open(checked(m['copyMask'],m['copyMaskSha256'])))
  inputp=Path(m.get('input',manifestp.parent/'input.png'))
  expected=image(inputp)
  if m.get('inputSha256'):checked(inputp,m['inputSha256'])
  for original in m['sourceCrops']:
   checked(original['file'],original['sha256'])
   target=sub(expected,original['destinationBox'],[0,0,expected.shape[1],expected.shape[0]])
   assert np.array_equal(target,sub(image(original['file']),original['sourceCrop'],[0,0,4096,4096]))
  patches.append({'id':entry['id'],'worldBox':m['worldBox'],'patch':patch,'mask':mask,'expected':expected,'manifest':str(manifestp),'manifestSha256':sha(manifestp),'patchEvidence':info(m['premixed']),'maskEvidence':info(m['copyMask'])})
records=[]
for p in patches:
 box=p['worldBox'];patch=p['patch'];mask=p['mask'];expected=p['expected']
 assert patch.shape==expected.shape and mask.shape==patch.shape[:2]
 assert set(np.unique(mask)).issubset({0,255})
 mask=mask>0;applications=[];rebases=[]
 for tile in cores:
  coreintersection=intersection(box,worlds[tile]['core'])
  if coreintersection:
   old=sub(cores[tile],coreintersection,worlds[tile]['core'])
   ref=sub(expected,coreintersection,box);active=sub(mask,coreintersection,box)
   if not np.array_equal(old[active],ref[active]):
    key=p['id']+':'+tile
    allowed=cfg.get('intentionalRebases',{}).get(key)
    assert allowed, 'Changed base pixels under mask: '+key
    baselinep=checked(allowed['baselineCandidate'],allowed['sha256'])
    baseline=sub(image(baselinep),coreintersection,worlds[tile]['core'])
    assert np.array_equal(baseline[active],ref[active]),'Rebase baseline mismatch: '+key
    changed=np.any(old!=ref,axis=2)&active
    ys,xs=np.where(changed);cx,cy=worlds[tile]['core'][:2]
    changed_box=[int(xs.min())+coreintersection[0]-cx,int(ys.min())+coreintersection[1]-cy,int(xs.max())+1+coreintersection[0]-cx,int(ys.max())+1+coreintersection[1]-cy]
    bounds=allowed['allowedCandidateBox']
    assert bounds[0]<=changed_box[0] and bounds[1]<=changed_box[1] and bounds[2]>=changed_box[2] and bounds[3]>=changed_box[3]
    rebases.append({'tile':tile,'changedPixelCount':int(changed.sum()),'changedCandidateBox':changed_box,'baselineCandidate':str(baselinep),'baselineSha256':allowed['sha256'],'reason':allowed['reason']})
  ci=intersection(box,worlds[tile]['context'])
  if not ci:continue
  active=sub(mask,ci,box);paint=sub(patch,ci,box)
  existing=sub(allmasks[tile],ci,worlds[tile]['context'])
  assert not np.logical_and(existing,active).any(),'Overlapping proposals: '+tile+' '+p['id']
  target=sub(after[tile],ci,worlds[tile]['context'])
  target[active]=paint[active];existing|=active
  applications.append({'tile':tile,'worldBox':ci,'activeContextPixels':int(active.sum()),'coreSourcePixelsVerifiedBeforeRebase':True,'haloCopiesUpdatedFromSameWorldPatch':True})
 records.append({k:v for k,v in p.items() if k not in ['patch','mask','expected']}|{'applications':applications,'intentionalRebases':rebases,'activePixels':int(mask.sum())})
outputs={};qa=OUT/'qa';qa.mkdir(exist_ok=True)
for tile in cores:
 assert np.array_equal(before[tile][~allmasks[tile]],after[tile][~allmasks[tile]])
 core=after[tile][115:4211,115:4211];cores[tile]=core
 corep=OUT/(tile+'.candidate.png');ctxp=OUT/(tile+'.candidate.context.png')
 assert not corep.exists() and not ctxp.exists()
 Image.fromarray(core).save(corep);Image.fromarray(after[tile]).save(ctxp)
 outputs[tile]={'candidate':info(corep),'context':info(ctxp),'coreWorldBox':worlds[tile]['core'],'outsideMasksExact':True,'coreEqualsContextCrop':True,'activeOverlayContextPixels':int(allmasks[tile].sum()),'formalAccepted':False,'internalPassed':False}
for name,a,b,axis in [('north_vertical','r10_c05','r10_c06',1),('south_vertical','r11_c05','r11_c06',1),('west_horizontal','r10_c05','r11_c05',0),('east_horizontal','r10_c06','r11_c06',0)]:
 strip=np.concatenate([cores[a][:,-384:],cores[b][:,:384]],1) if axis==1 else np.concatenate([cores[a][-384:],cores[b][:384]],0)
 Image.fromarray(strip).save(qa/(name+'.actual.png'))
 for i in range(4):
  part=strip[i*1024:(i+1)*1024] if axis==1 else strip[:,i*1024:(i+1)*1024]
  Image.fromarray(part).save(qa/(name+'.segment'+str(i+1)+'.png'))
montage=np.concatenate([np.concatenate([cores['r10_c05'],cores['r10_c06']],1),np.concatenate([cores['r11_c05'],cores['r11_c06']],1)],0)
previewp=OUT/'2x2.preview-2048.png'
Image.fromarray(montage).resize((2048,2048),Image.Resampling.LANCZOS).save(previewp)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'merged_candidate_pending_cross_edge_visual_review','inputsFile':str(input_path),'inputsSha256':sha(input_path),'sources':source_records,'patches':records,'outputs':outputs,'preview':info(previewp)|{'sourcePixels':[8192,8192],'resizedForQaOnly':True},'sourceFilesUnchanged':all(sha(s['candidate']['file'])==s['candidate']['sha256'] for s in source_records.values()),'patchesPreblendedCopiedWithoutSecondAlpha':True,'candidateImageResampling':False,'newImageGenerationCalls':0,'allCrossEdgesPassed':False,'formalAcceptedCount':0,'remainingIssues':cfg['remainingIssues']}
(OUT/'assembly.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'outputs':outputs,'assembly':str(OUT/'assembly.json')},indent=2))

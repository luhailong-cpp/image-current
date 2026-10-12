from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib,uuid,importlib.util
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs'
spec=importlib.util.spec_from_file_location('internal',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
def put(p,v):
 p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(v,indent=2),encoding='utf-8');tmp.replace(p)
def prepare(label,y,boxes,instruction):
 y=int(y);boxes=json.loads(boxes);I.need(0<=y<=2842,'Y outside')
 cur=I.read(T/'candidate/latest-assembly.json');west=I.read(T.parent/'r14_c13/candidate/latest-assembly.json')
 for a in [cur['candidate'],cur['context'],west['candidate']]:I.checked(a)
 contract=I.read(T.parent.parent/'production-contract.json')
 I.need(contract['newArtworkGenerationAllowed'] and I.read(contract['productionResumeControl'])['newArtworkGenerationAllowed'],'Gate')
 refs=[]
 for k,h in [('layoutReference','layoutSha256'),('detailStyleReference','detailSha256'),('primaryStyleReference','primaryStyleSha256')]:
  a=I.art(contract[k]);I.need(a['sha256']==contract[h],'Style changed');a['role']=k+' style only';refs.append(a)
 ver=label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
 raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(west['candidate']['path']).convert('RGB').crop((3781,y,4096,y+1254)),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop((0,y,939,y+1254)),(315,0));I.png(d/'source-1254.png',raw)
 guide=raw.copy();dr=ImageDraw.Draw(guide)
 for a,b,c,e in boxes:
  I.need(315<=a<c<=1248 and 0<=b<e<=1254,'Guide must stay on current tile side');dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
 I.png(d/'target-1254.png',guide)
 prompt='''Use case: precise-object-edit. Edit only the LAST exact1254x1254 crop of our existing chibi Taoist game map. The first3 images are style references only. Fill only the solid magenta region; every visible non-magenta pixel is fixed context. The LEFT315px are an immutable already-made neighboring stone pavement, the RIGHT939px are the current tile. Join the stone pavement seamlessly across x315. Preserve the exact stone size, perspective, existing shadows and lighting. Match every fixed dark grout endpoint on the left, right, top and bottom sides of the magenta area; produce continuous natural grooves, coherent closed LARGE stone slabs and continuous grey stone tone/texture. Do not create a vertical strip or border at x315. No blue bands, new objects, red paper, foliage, text, UI, zoom, pan or scaling. Avoid dangling grooves, doubled lines, partial corners and tiny slivers. Preserve existing red paper and shadows outside the magenta area. Output one opaque native1254x1254PNG at unchanged framing.
SPECIFIC REPAIR:
'''+instruction
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');refs.append({**I.art(d/'target-1254.png'),'role':'LAST IMAGE only edit target, native joined verified core crops'})
 req={'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False};I.js(d/'request.json',req)
 prep={'version':ver,'tile':'r14_c14','preparedAt':I.now(),'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'westCore':west['candidate'],'westCrop':[3781,y,4096,y+1254],'currentCrop':[0,y,939,y+1254],'rawTarget':I.art(d/'source-1254.png'),'guide':I.art(d/'target-1254.png'),'guideHoles':boxes,'guideFillRGB':[255,0,255],'targetSeamX':315,'references':refs,'request':I.art(d/'request.json'),'prompt':I.art(d/'prompt.txt'),'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'resized':False,'formalAccepted':False,'reservedCorner':[0,0,630,630]}
 I.js(d/'preparation.json',prep)
 return {'version':ver,'request':str(d/'request.json'),'target':str(d/'target-1254.png')}
def compose(version):
 d=R/version;p=I.read(d/'preparation.json');g=I.read(d/'generation.json');cur=I.read(T/'candidate/latest-assembly.json')
 for a in [g['native'],g['receipt'],g['originalOutput'],g['preparation'],cur['candidate'],cur['context'],p['westCore']]:I.checked(a)
 y=p['currentCrop'][1];base=np.array(Image.open(cur['candidate']['path']).convert('RGB'));raw=np.array(Image.open(p['rawTarget']['path']).convert('RGB'));native=np.array(Image.open(g['native']['path']).convert('RGB'))
 alpha=np.zeros((1254,1254),np.uint8)
 for a,b,c,e in p['guideHoles']:
  a=max(315,a-12);b=max(0,b-12);c=min(1254,c+12);e=min(1254,e+12)
  yy,xx=np.mgrid[b:e,a:c]
  dims=[c-1-xx]
  if a>315:dims.append(xx-a)
  if y+b>630:dims.append(yy-b)
  if y+e<4096:dims.append(e-1-yy)
  dist=np.minimum.reduce(dims);alpha[b:e,a:c]=np.maximum(alpha[b:e,a:c],np.uint8(np.clip(dist/16,0,1)*255))
 yy,xx=np.mgrid[0:1254,0:1254];alpha[(xx<315)|(((xx-315)<630)&((y+yy)<630))]=0
 own=alpha[:,315:];old=base[y:y+1254,:939].copy()
 I.need(np.array_equal(old[own>0],raw[:,315:][own>0]),'Applied current source changed')
 I.need(not np.any((native[:,:,0]==255)&(native[:,:,1]==0)&(native[:,:,2]==255)&(alpha>0)),'Magenta remains')
 a=own[:,:,None].astype(np.uint32);base[y:y+1254,:939]=((old.astype(np.uint32)*(255-a)+native[:,315:].astype(np.uint32)*a+127)//255).astype(np.uint8)
 I.png(d/'alpha.png',Image.fromarray(alpha));out=T/'candidate'/('r14_c14-4k-'+version+'.png');I.png(out,Image.fromarray(base))
 ctx=np.array(Image.open(cur['context']['path']).convert('RGB'));ctx[115:4211,115:4211]=base;west=np.array(Image.open(p['westCore']['path']).convert('RGB'));ctx[115:4211,:115]=west[:,3981:4096]
 cp=T/'candidate'/('r14_c14-context-'+version+'.png');I.png(cp,Image.fromarray(ctx))
 review=Image.new('RGB',(1254,1254));review.paste(Image.fromarray(west[y:y+1254,3781:4096]),(0,0));review.paste(Image.fromarray(base[y:y+1254,:939]),(315,0));I.png(d/'review-composed-1254.png',review)
 m={'version':version,'tile':'r14_c14','sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'candidate':I.art(out),'context':I.art(cp),'westCore':p['westCore'],'preparation':I.art(d/'preparation.json'),'generation':I.art(d/'generation.json'),'native':g['native'],'originalOutput':g['originalOutput'],'receipt':g['receipt'],'alpha':I.art(d/'alpha.png'),'nativeAppliedCrop':[315,0,1254,1254],'placementInCore':[0,y,939,y+1254],'compositor':I.art(Path(__file__)),'rule':'Actual unscaled native right939px only. Guide holes expanded12;16px linear transition on current-side outer perimeter, full alpha at fixed west core seam; northwest630 square zero alpha. uint32 rounded. Context west115 strip copied from verified west4096core. No neighbor write or resize.','formalAccepted':False}
 I.js(d/'composition.json',m);return {'manifest':str(d/'composition.json'),'review':str(d/'review-composed-1254.png'),'candidate':m['candidate'],'replay':replay(version)}
def replay(version):
 d=R/version;m=I.read(d/'composition.json');p=I.read(d/'preparation.json');g=I.read(d/'generation.json')
 for k in ['sourceCandidate','sourceContext','candidate','context','westCore','preparation','generation','native','originalOutput','receipt','alpha','compositor']:I.checked(m[k])
 for a in p['references']+[p['request'],p['prompt'],p['rawTarget'],p['guide'],p['sourceCandidate'],p['sourceContext']]:I.checked(a)
 y=p['currentCrop'][1];raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(p['westCore']['path']).convert('RGB').crop(tuple(p['westCrop'])),(0,0));raw.paste(Image.open(p['sourceCandidate']['path']).convert('RGB').crop(tuple(p['currentCrop'])),(315,0));I.need(np.array_equal(raw,Image.open(p['rawTarget']['path']).convert('RGB')),'Raw core target replay')
 dr=ImageDraw.Draw(raw)
 for a,b,c,e in p['guideHoles']:dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
 I.need(np.array_equal(raw,Image.open(p['guide']['path']).convert('RGB')),'Guide replay')
 base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));gen=np.array(Image.open(m['native']['path']).convert('RGB'));alpha=np.array(Image.open(m['alpha']['path']))
 I.need(not np.any(alpha[:,:315]),'No west neighbor can be changed');a=alpha[:,315:,None].astype(np.uint32)
 base[y:y+1254,:939]=((base[y:y+1254,:939].astype(np.uint32)*(255-a)+gen[:,315:].astype(np.uint32)*a+127)//255).astype(np.uint8)
 I.need(np.array_equal(base,np.array(Image.open(m['candidate']['path']).convert('RGB'))),'Core replay')
 original=np.array(Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB'));I.need(np.array_equal(base[:630,:630],original[:630,:630]),'Frozen corner changed')
 ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=base;ctx[115:4211,:115]=np.array(Image.open(m['westCore']['path']).convert('RGB'))[:,3981:4096]
 I.need(np.array_equal(ctx,np.array(Image.open(m['context']['path']).convert('RGB'))),'Context replay')
 return {'replayed':True,'reservedCornerUnchanged':True,'westCoreUnchanged':True,'candidateSha256':m['candidate']['sha256']}
def publish(version,note):
 d=R/version;v=I.read(d/'visual-review.json');I.need(v['status']=='local_pass','Local visual pass required');r=replay(version);m=I.read(d/'composition.json');old=I.read(T/'candidate/latest-assembly.json');I.need(old['candidate']['sha256']==m['sourceCandidate']['sha256'],'Current publish chain changed')
 m['candidate']['size']=[4096,4096];m['context']['size']=[4326,4326];put(R/'latest-repair.json',m)
 latest={**old,'publishedAt':I.now(),'status':'west_native_repair_partial_external_not_passed','candidate':m['candidate'],'context':m['context'],'manifest':I.art(d/'composition.json'),'formalAccepted':False,'externalNeighborSeamQA':'not_passed','latestWestRepair':version};put(T/'candidate/latest-assembly.json',latest)
 records=list((T/'native').glob('*.generation.json'))+list(R.glob('*/generation.json'));p=I.read(T/'progress.json');p.update(updatedAt=I.now(),status=latest['status'],generatedNativeCount=len(records),candidate=m['candidate']['path'],context=m['context']['path'],assemblyManifest=str(d/'composition.json'),currentPatch=version,nextStep=note);put(T/'progress.json',p)
 for f in ['local-continuation-20261011.json','continuation-round-20261011.json']:
  c=I.read(T/f);c.update(updatedAt=I.now(),candidate=m['candidate'],manifest=latest['manifest'],currentCoordinate=version,externalQA='not_passed',nextStep=note);put(T/f,c)
 return {'candidate':m['candidate'],'manifest':latest['manifest'],'nativeRecords':len(records),'replay':r}
if __name__=='__main__':print(json.dumps(globals()[sys.argv[1]](*sys.argv[2:]),indent=2))


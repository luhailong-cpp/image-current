"""Offline integer crop/alpha compositor for the two prepared 2026-10-12 repairs.
No network or artwork synthesis. PNG RGB values are only copied or mixed with
the alpha fixed before source receipt. No RGB correction, resizing or warping.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,uuid,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs'
spec=importlib.util.spec_from_file_location('internal_20261012',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
def put(p,value):
 p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');tmp.replace(p)
def rect_slice(b):x,y,x1,y1=b;return (slice(y,y1),slice(x,x1))
def replay_preparation(version):
 d=R/version;p=I.read(d/'preparation.json')
 for a in p['references']+[p[k] for k in ['sourceCandidate','sourceContext','neighborCore','rawTarget','guide','editMask','request','prompt']]:I.checked(a)
 raw=Image.new('RGB',(1254,1254))
 raw.paste(Image.open(p['neighborCore']['path']).convert('RGB').crop(tuple(p['neighborCoreCrop'])),tuple(p['neighborPlacement'][:2]))
 raw.paste(Image.open(p['sourceCandidate']['path']).convert('RGB').crop(tuple(p['currentCoreCrop'])),tuple(p['currentPlacement'][:2]))
 I.need(np.array_equal(raw,Image.open(p['rawTarget']['path']).convert('RGB')),'Raw target mismatch')
 mask=Image.new('L',(1254,1254),0);dr=ImageDraw.Draw(mask)
 for x,y,x1,y1 in p['rectanglesBeforeProtection']:dr.rectangle((x,y,x1-1,y1-1),fill=255)
 if 'protectionRule' in p:
  rule=p['protectionRule'];dark=np.array(raw).astype(np.uint16).sum(axis=2)<rule['rgbSumBelow'];protected=np.array(Image.fromarray(dark.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(rule['pillowMaxFilterSize'])))>0;a=np.array(mask);a[protected]=0;mask=Image.fromarray(a)
 I.need(np.array_equal(mask,Image.open(p['editMask']['path'])),'Edit mask replay')
 arr=np.array(raw);arr[np.array(mask)>0]=p['guideFillRGB'];I.need(np.array_equal(arr,Image.open(p['guide']['path']).convert('RGB')),'Guide replay')
 req=I.read(p['request']['path']);I.need(req['prompt']==Path(p['prompt']['path']).read_text(encoding='utf-8'),'Prompt/request mismatch');I.need(req['referenced_image_paths']==[a['path'] for a in p['references']],'Request refs mismatch')
 return p
def make_alpha(p):
 mask=np.array(Image.open(p['editMask']['path']).convert('L'));extended=mask.copy()
 # Mirror the boundary column/row into reference side for MASK erosion only.
 # This avoids fading at the joining seam; actual neighbor alpha remains zero.
 if p['direction']=='west':extended[:,:640]=extended[:,640:641]
 elif p['direction']=='north':extended[:640,:]=extended[640:641,:]
 else:raise ValueError('Unknown direction')
 alpha=np.zeros((1254,1254),np.uint16);im=Image.fromarray(extended)
 for radius in range(16):
  eroded=im if radius==0 else im.filter(ImageFilter.MinFilter(2*radius+1))
  alpha+=(np.array(eroded)>0).astype(np.uint16)*17
 alpha=alpha.astype(np.uint8);alpha[mask==0]=0
 current=np.zeros_like(mask,dtype=bool);current[rect_slice(p['currentPlacement'])]=True;alpha[~current]=0
 # NW reserved region cannot be touched even if a later caller mis-prepares.
 x,y,x1,y1=p['currentCoreCrop'];a,b,c,e=p['currentPlacement'];yy,xx=np.mgrid[b:e,a:c];own=alpha[b:e,a:c];own[((x+xx-a)<630)&((y+yy-b)<630)]=0
 return alpha
def stage(version):
 p=replay_preparation(version);d=R/version;alpha=make_alpha(p)
 I.need(not (d/'assembly-alpha.png').exists(),'Immutable alpha already exists')
 I.png(d/'assembly-alpha.png',Image.fromarray(alpha))
 record={'version':version,'stagedAt':I.now(),'preparation':I.art(d/'preparation.json'),'editMask':p['editMask'],'alpha':I.art(d/'assembly-alpha.png'),'compositor':I.art(Path(__file__)),'rule':'Alpha fixed before returned output is read. Sum of 16 square binary-mask erosions radius0..15, each weight17. Reference-side mask boundary extended only for erosion; all reference pixels and all outside-mask/protected grout pixels forced0. Actual current-native crop is integer and unscaled. RGB composition uint32 rounded (old*(255-a)+native*a+127)//255. No RGB correction or resampling.','nativeSourceCrop':p['currentPlacement'],'placementInCore':p['currentCoreCrop'],'actualOutputKnownAtStage':False,'reservedCorner':[0,0,630,630]}
 I.js(d/'assembly-plan.json',record)
 return record
def ingest(version,original_output,receipt_path):
 p=replay_preparation(version);d=R/version;plan=I.read(d/'assembly-plan.json')
 for a in [plan['preparation'],plan['alpha'],plan['compositor']]:I.checked(a)
 receipt=I.read(receipt_path);I.need(receipt.get('originalOutputPath')==str(original_output),'Receipt original path must exactly match tool-reported path')
 I.need(receipt.get('route')=='builtin','Builtin receipt route required')
 result=I.ingest(version,original_output,receipt_path)
 resume=I.read(T/'production-resume-20261012.json');g=I.read(d/'generation.json');entry={'recordedAt':I.now(),'version':version,'originalOutput':g['originalOutput'],'native':g['native'],'generation':I.art(d/'generation.json'),'receipt':g['receipt'],'source':'root builtin image_gen output delivered for offline ingest','actualModel':None,'actualQuality':None}
 if not resume.get('firstActualNewOutputAfterThisResume'):resume['firstActualNewOutputAfterThisResume']=entry
 resume.update(updatedAt=I.now(),newNativeOutputAfter20261012Resume=entry,status='native_received_offline_composition_pending');put(T/'production-resume-20261012.json',resume)
 return result
def compose(version,label):
 p=replay_preparation(version);d=R/version;plan=I.read(d/'assembly-plan.json');g=I.read(d/'generation.json');cur=I.read(T/'candidate/latest-assembly.json')
 for a in [plan['preparation'],plan['editMask'],plan['alpha'],plan['compositor'],g['native'],g['originalOutput'],g['receipt'],g['preparation'],cur['candidate'],cur['context']]:I.checked(a)
 I.need(plan['compositor']['sha256']==I.sha(Path(__file__)),'Use exact staged compositor')
 alpha=np.array(Image.open(plan['alpha']['path']).convert('L'));I.need(np.array_equal(alpha,make_alpha(p)),'Fixed alpha replay')
 native=np.array(Image.open(g['native']['path']).convert('RGB'));I.need(native.shape==(1254,1254,3),'No resize allowed')
 I.need(not np.any(np.all(native==[255,0,255],axis=2)&(alpha>0)),'Applied magenta remains')
 full=np.array(Image.open(cur['candidate']['path']).convert('RGB'));before=full.copy();raw=np.array(Image.open(p['rawTarget']['path']).convert('RGB'))
 source=rect_slice(p['currentPlacement']);target=rect_slice(p['currentCoreCrop']);a=alpha[source];old=full[target].copy()
 I.need(np.array_equal(old[a>0],raw[source][a>0]),'Current edited region changed since prepare')
 aa=a[:,:,None].astype(np.uint32);full[target]=((old.astype(np.uint32)*(255-aa)+native[source].astype(np.uint32)*aa+127)//255).astype(np.uint8)
 support=np.zeros((4096,4096),bool);support[target]=a>0;I.need(np.array_equal(before[~support],full[~support]),'Outside support changed')
 frozen=np.array(Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB'))[:630,:630];I.need(np.array_equal(full[:630,:630],frozen),'Reserved corner changed')
 out=R/label;out.mkdir();cp=T/'candidate'/('r14_c14-4k-'+label+'.png');I.png(cp,Image.fromarray(full))
 context=np.array(Image.open(cur['context']['path']).convert('RGB'));context[115:4211,115:4211]=full;ctx=T/'candidate'/('r14_c14-context-'+label+'.png');I.png(ctx,Image.fromarray(context))
 review=np.array(Image.open(p['rawTarget']['path']).convert('RGB'));review[source]=full[target];I.png(out/'review-composed-1254.png',Image.fromarray(review))
 m={'schemaVersion':1,'version':label,'tile':'r14_c14','composedAt':I.now(),'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'candidate':I.art(cp),'context':I.art(ctx),'preparation':I.art(d/'preparation.json'),'assemblyPlan':I.art(d/'assembly-plan.json'),'generation':I.art(d/'generation.json'),'native':g['native'],'originalOutput':g['originalOutput'],'receipt':g['receipt'],'alpha':plan['alpha'],'nativeSourceCrop':p['currentPlacement'],'placementInCore':p['currentCoreCrop'],'neighborCore':p['neighborCore'],'compositor':I.art(Path(__file__)),'resized':False,'rgbCorrectionPerformed':False,'contextHaloUpdated':False,'contextHaloIsAuthority':False,'outsideAlphaSupportUnchanged':True,'reservedCornerUnchanged':True,'formalAccepted':False,'status':'candidate_pending_visual_review'}
 I.js(out/'composition.json',m);report=replay(label);qa(label)
 return {'manifest':I.art(out/'composition.json'),'review':str(out/'review-composed-1254.png'),'candidate':m['candidate'],'replay':report}
def replay(label):
 d=R/label;m=I.read(d/'composition.json');p=replay_preparation(Path(m['preparation']['path']).parent.name)
 for a in [m[k] for k in ['sourceCandidate','sourceContext','candidate','context','preparation','assemblyPlan','generation','native','originalOutput','receipt','alpha','neighborCore','compositor']]:I.checked(a)
 plan=I.read(m['assemblyPlan']['path']);alpha=np.array(Image.open(m['alpha']['path']).convert('L'));I.need(np.array_equal(alpha,make_alpha(p)),'Alpha changed')
 native=np.array(Image.open(m['native']['path']).convert('RGB'));base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));old=base.copy()
 source=rect_slice(m['nativeSourceCrop']);target=rect_slice(m['placementInCore']);a=alpha[source][:,:,None].astype(np.uint32)
 base[target]=((base[target].astype(np.uint32)*(255-a)+native[source].astype(np.uint32)*a+127)//255).astype(np.uint8)
 I.need(np.array_equal(base,Image.open(m['candidate']['path']).convert('RGB')),'Core replay')
 ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=base;I.need(np.array_equal(ctx,Image.open(m['context']['path']).convert('RGB')),'Context replay')
 freeze=np.array(Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB'))[:630,:630];I.need(np.array_equal(base[:630,:630],freeze),'Corner')
 mask=np.array(Image.open(p['editMask']['path']))==0;I.need(not np.any(alpha[mask]),'Protected pixels altered')
 return {'replayed':True,'candidateSha256':m['candidate']['sha256'],'reservedCornerUnchanged':True,'outsideSavedMaskUnchanged':True,'neighborCoreUnchanged':True,'rgbCorrectionPerformed':False}
def qa(label):
 d=R/label;m=I.read(d/'composition.json');p=I.read(m['preparation']['path']);im=Image.open(d/'review-composed-1254.png').convert('RGB')
 # Native-scale rows/columns cross both the external seam and every mask transition.
 paths=[]
 for i in range(3):
  b=(0,i*418,1254,(i+1)*418);fp=d/('review-strip'+str(i)+'-100pct.png');I.png(fp,im.crop(b));paths.append(I.art(fp))
 before=np.array(Image.open(p['rawTarget']['path']).convert('RGB')).astype(np.float64);after=np.array(im).astype(np.float64)
 if p['direction']=='west':
  ranges=[(540,880),(400,1100)]
  metrics=[{'coreY':[a+2000,b+2000],'beforeRightMinusLeft4px':(before[a:b,640:644].mean(axis=(0,1))-before[a:b,636:640].mean(axis=(0,1))).round(3).tolist(),'afterRightMinusLeft4px':(after[a:b,640:644].mean(axis=(0,1))-after[a:b,636:640].mean(axis=(0,1))).round(3).tolist()} for a,b in ranges]
 else:metrics=[]
 report={'candidate':m['candidate'],'actualFixedNeighborComposite':I.art(d/'review-composed-1254.png'),'strips':paths,'descriptiveSeamMetrics':metrics,'metricsAreNotVisualApproval':True,'formalAccepted':False,'resized':False,'visualStatus':'pending'}
 I.js(d/'qa-evidence.json',report);return report
def publish(label,review_path):
 d=R/label;m=I.read(d/'composition.json');review=I.read(review_path);I.need(review.get('status')=='local_pass','Explicit truthful local visual pass required')
 I.need(review.get('candidateSha256')==m['candidate']['sha256'],'Review is not bound to this candidate')
 result=replay(label);current=I.read(T/'candidate/latest-assembly.json');I.need(current['candidate']['sha256']==m['sourceCandidate']['sha256'],'Published source changed')
 put(R/'latest-repair.json',m);latest={**current,'publishedAt':I.now(),'candidate':m['candidate'],'context':m['context'],'manifest':I.art(d/'composition.json'),'status':'native_external_repair_partial_pending_full_external_review','formalAccepted':False,'externalNeighborSeamQA':'not_passed'};put(T/'candidate/latest-assembly.json',latest)
 count=len(list((T/'native').glob('*.generation.json')))+len(list(R.glob('*/generation.json')))
 progress=I.read(T/'progress.json');progress.update(updatedAt=I.now(),status=latest['status'],generatedNativeCount=count,candidate=m['candidate']['path'],context=m['context']['path'],assemblyManifest=str(d/'composition.json'),currentPatch=label,inFlightImageGenCount=0,formalAccepted=False,externalNeighborSeamQA='not_passed');put(T/'progress.json',progress)
 resume=I.read(T/'production-resume-20261012.json');resume.update(updatedAt=I.now(),status=latest['status'],candidate=m['candidate'],context=m['context'],manifest=latest['manifest'],historicalNativeCount=count,lastLocalPassReview=I.art(review_path),formalAccepted=False);put(T/'production-resume-20261012.json',resume)
 return {'candidate':m['candidate'],'manifest':latest['manifest'],'nativeRecords':count,'replay':result}
if __name__=='__main__':print(json.dumps(globals()[sys.argv[1]](*sys.argv[2:]),indent=2))


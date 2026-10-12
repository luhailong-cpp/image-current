from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parent.parent;R=B/'records'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
oldp=R/'cast-E-02.generation.json'; old=load(oldp); candidate01=load(R/'cast-E-02-candidate01.generation.json')
ref=old['references'][-1]; wrong=ref['sha256']
ref['correctedFrom']={'sha256':wrong,'role':ref['role'],'reason':'export helper sampled overwritten output, causing self-reference'}
ref['sha256']=candidate01['sha256'];ref['role']='historical targeted edit input, candidate01 before fifth-paw removal'
ref['correctionEvidence']={'record':'records/cast-E-02-candidate01.generation.json','field':'sha256','request':'records/cast-E-02.request.json','basis':'request edits candidate01 residual low frontpaw; e_cast original author confirmed pre-edit input'}
old['disposition']='superseded by support-repair4; historical generation evidence retained'
old['supersededBy']='records/cast-E-02-support-repair4.generation.json'
save(oldp,old)
save(R/'cast-E-02-support-candidate02.generation.json',old)
records=[]
for k in range(1,5):
 tag=f'cast-E-02-support-repair{k}'
 req=load(R/f'{tag}.request.json');receipt=load(R/f'{tag}.receipt.json')
 src=Path(receipt['sourcePath']);im=Image.open(src);im.load()
 assert im.mode=='RGBA' and im.size==(1254,1254)
 rec={'file':str(src),'sha256':sha(src),'generatedAt':receipt['receivedAt'],'generationStartedAt':receipt['startedAt'],'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':old['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':req['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未开放model/quality且未披露实际值。','evidence':{'receipt':f'records/{tag}.receipt.json','outputHint':receipt['output_hint'],'returnedFields':['image_url','output_hint']},'prompt':f'records/{tag}.prompt.txt','request':f'records/{tag}.request.json','references':[{'path':p,'sha256':h,'role':f'input{i+1}; exact role in prompt'} for i,(p,h) in enumerate(zip(req['referenced_image_paths'],req['referenceSha256Before']))],'disposition':receipt['disposition'],'sourceRetention':'host cache outside assigned write scope; no local source duplicate made'}
 save(R/f'{tag}.generation.json',rec);records.append(rec)
src=Path(records[-1]['file']);out=B/'runtime/cast/E/02.png'
assert sha(out)==old['sha256']
Image.open(src).resize((1024,1024),Image.Resampling.LANCZOS).save(out)
im=Image.open(out);a=im.getchannel('A');threshold=a.point(lambda v:255 if v>=128 else 0)
derived={'file':'runtime/cast/E/02.png','sha256':sha(out),'exportedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','action':'cast','direction':'E','frame':2,'durationMs':45,'derivedFrom':{'file':str(src),'sha256':records[-1]['sha256'],'generationRecord':'records/cast-E-02-support-repair4.generation.json'},'operation':{'type':'whole-canvas-resize','sourceSize':[1254,1254],'outputSize':[1024,1024],'resampling':'LANCZOS','perFrameAlignment':False,'translation':[0,0]},'actualModel':None,'actualQuality':None,'visualStatus':'support and four-limb anatomy individually viewed, root sequence QA pending'}
save(out.with_suffix('.png.generation.json'),derived)
native=(B/old['native']['path']).resolve(); cleanup=[]
if native.exists():
 assert B.resolve() in native.parents and native.parent.name=='.native' and native.name=='02.png'
 assert sha(native)==old['native']['sha256']
 cleanup.append({'path':str(native),'sha256':sha(native),'reason':'superseded local native; replacement exported and checked'})
 native.unlink()
report={'frame':'cast-E-02','oldExportSha':old['sha256'],'newExportSha':sha(out),'nativeSha':records[-1]['sha256'],'size':im.size,'mode':im.mode,'alphaExtrema':a.getextrema(),'opaqueBBox':threshold.getbbox(),'leftHindRegionOpaqueBBox':threshold.crop((260,780,550,1024)).getbbox(),'rightHindRegionOpaqueBBox':threshold.crop((700,760,950,1024)).getbbox(),'historyCorrection':{'correctedFrom':wrong,'correctedTo':candidate01['sha256']},'deletedLocalSources':cleanup,'fixedDirectionOffset':'not applied; root will apply common E(0,-15)','hostSources':[r['file'] for r in records]}
save(R/'cast-E-02-support-validation.json',report)
print(json.dumps(report,ensure_ascii=False))


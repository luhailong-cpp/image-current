from pathlib import Path
from PIL import Image, ImageChops
import json, hashlib, datetime, re, numpy as np
D=Path(__file__).resolve().parent; TILE=D.parents[1]; BASE=TILE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
req=read(D/'request.json');rc=read(D/'receipt.json');raw=D/'native-result.png';im=Image.open(raw).convert('RGB');assert im.size==(1254,1254)
rc.setdefault('originalFile',re.search(r'as (C:\\[^\n]+?\.png) by default',rc['output_hint']).group(1).replace('\\','/'))
rc.setdefault('receivedAt',rc.get('completedAtUtc'))
g={'file':str(raw),'sha256':sha(raw),'nativeDimensions':list(im.size),'format':'PNG','nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin receipt exposes no verified model or quality metadata.','sourcePath':rc['originalFile'],'sourceSha256':sha(rc['originalFile']),'prompt':req['prompt'],'promptFile':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'requestFile':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'receiptFile':str(D/'receipt.json'),'receiptSha256':sha(D/'receipt.json'),'requestedAt':rc.get('requestedAt'),'receivedAt':rc['receivedAt'],'formalAccepted':False}
(D/'native-result.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
original=TILE/'native/p11-v1.png';guide=TILE/'guides/p11-v1-positional.png';target=TILE/'repairs/p11-north-net-v1/target-native.png'
base=Image.open(original).convert('RGB');base.paste(Image.open(guide).convert('RGB').crop((0,0,1254,115)),(0,0))
base.save(D/'composite-base-native.png')
y,x=np.mgrid[0:1254,0:1254]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
alpha=smooth((x-115)/12)*smooth((550-x)/20)*(y>=115)*smooth((550-y)/30)
mask=Image.fromarray(np.rint(alpha*255).astype('uint8'),'L');mp=D/'native-alpha-mask.png';mask.save(mp)
out=Image.composite(im,base,mask);op=D/'p11-composite-native.png';out.save(op)
core=out.crop((115,115,1139,1139));core.save(D/'p11-core1024-proposal.png')
q=D/'qa';q.mkdir(exist_ok=True)
out.crop((96,128,576,560)).save(q/'local-net-transition-native.png')
npath=BASE/'r04_c11/candidate/r04_c11-4096-candidate-v3.png';n=Image.open(npath).convert('RGB')
nseam=Image.new('RGB',(1024,256));nseam.paste(n.crop((0,3968,1024,4096)),(0,0));nseam.paste(core.crop((0,0,1024,128)),(0,128));nseam.save(q/'north-proposal-native.png')
wsel=read(BASE/'r05_c10/records/p14.selection.json');w=Image.open(wsel['file']).convert('RGB').crop((115,115,1139,1139));ws=Image.new('RGB',(256,1024));ws.paste(w.crop((896,0,1024,1024)),(0,0));ws.paste(core.crop((0,0,128,1024)),(128,0));ws.save(q/'west-proposal-native.png')
orig=Image.open(original).convert('RGB');diff=np.any(np.asarray(out)!=np.asarray(orig),axis=2);ys,xs=np.where(diff)
prop={'status':'proposal_pending_visual_review','formalAccepted':False,'tile':'r05_c11','core':'p11','outputNative':{'file':str(op),'sha256':sha(op),'dimensions':[1254,1254]},'outputCore':{'file':str(D/'p11-core1024-proposal.png'),'sha256':sha(D/'p11-core1024-proposal.png'),'dimensions':[1024,1024]},'baseNative':{'file':str(original),'sha256':sha(original)},'restoredGuide':{'file':str(guide),'sha256':sha(guide),'crop':[0,0,1254,230],'pasteAt':[0,0],'role':'exact approved native top context only; no blurred guide pixels'},'compositeBase':{'file':str(target),'sha256':sha(target)},'repairRaw':{'file':str(raw),'sha256':sha(raw),'generationRecord':str(D/'native-result.generation.json')},'mask':{'file':str(mp),'sha256':sha(mp),'formula':'round255(smooth((x-115)/12)*smooth((550-x)/20)*smooth((y-115)/28)*smooth((550-y)/30)); cubic clamped smoothstep'},'coreCrop':[115,115,1139,1139],'tileDestination':[0,0],'nativePixelsResized':False,'blendOperation':'PIL.Image.composite(repairRaw, restoredGuideTop230OverOriginalNative, L-mask)','changedNativeBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'top115MatchesApprovedGuide':ImageChops.difference(out.crop((0,0,1254,115)),Image.open(guide).convert('RGB').crop((0,0,1254,115))).getbbox() is None,'below550MatchesOriginal':ImageChops.difference(out.crop((0,550,1254,1254)),orig.crop((0,550,1254,1254))).getbbox() is None,'candidateChanged':False,'selectionChanged':False,'northCandidate':{'file':str(npath),'sha256':sha(npath)},'westSelectedNative':wsel,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
prop['status']='PASS_LOCAL_PROPOSAL'
prop['restoredGuide']['crop']=[0,0,1254,115]
prop['compositeBase']={'file':str(D/'composite-base-native.png'),'sha256':sha(D/'composite-base-native.png')}
prop['mask']['formula']='round255(smooth((x-115)/12)*smooth((550-x)/20)*(y>=115)*smooth((550-y)/30)); cubic clamped smoothstep'
prop['blendOperation']='PIL.Image.composite(repairRaw, originalNativeWithExactGuideTop115Only, L-mask)'
prop['qa']={'status':'PASS_LOCAL_PROPOSAL','northBoundary':'Reviewed against final r04_c11 v3; net and gold cords continuous.','westBoundary':'Reviewed against selected r05_c10 p14; net, sand and paving continuous.','localTransition':'y230 hard horizontal rope jump removed; net correctly hangs in front of post.','formalAccepted':False}
(D/'proposal.json').write_text(json.dumps(prop,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposal':str(D/'proposal.json'),'changedNativeBox':prop['changedNativeBox'],'top115Exact':prop['top115MatchesApprovedGuide'],'below550Exact':prop['below550MatchesOriginal']}))

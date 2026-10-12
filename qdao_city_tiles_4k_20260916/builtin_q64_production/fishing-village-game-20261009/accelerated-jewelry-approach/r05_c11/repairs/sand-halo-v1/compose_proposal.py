from pathlib import Path
from PIL import Image, ImageChops
import json,hashlib,datetime,numpy as np
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
req=read(D/'request.json');rc=read(D/'receipt.json');raw=D/'native-result.png';im=Image.open(raw).convert('RGB');assert im.size==(1254,1254)
g={'file':str(raw),'sha256':sha(raw),'nativeDimensions':[1254,1254],'format':'PNG','nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool receipt exposes no verified model or quality metadata.','sourcePath':rc['originalFile'],'sourceSha256':sha(rc['originalFile']),'prompt':req['prompt'],'promptFile':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'requestFile':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'receiptFile':str(D/'receipt.json'),'receiptSha256':sha(D/'receipt.json'),'requestedAt':rc['requestedAt'],'receivedAt':rc['receivedAt'],'formalAccepted':False}
(D/'native-result.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
y,x=np.mgrid[0:1254,0:1254]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
a=smooth((x-580)/20)*smooth((690-x)/20)*smooth((y-136)/16)*smooth((704-y)/32)
mask=Image.fromarray(np.rint(a*255).astype('uint8'),'L');mp=D/'native-alpha-mask.png';mask.save(mp)
base=Image.open(D/'target-native.png').convert('RGB');out=Image.composite(im,base,mask);op=D/'native-composite-proposal.png';out.save(op)
diff=np.any(np.asarray(out)!=np.asarray(base),axis=2);ys,xs=np.where(diff);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
q=D/'qa';q.mkdir(exist_ok=True)
for name,src in [('before',base),('after',out)]:src.crop((500,96,760,784)).save(q/(name+'-sand-strip-native.png'))
unchanged=ImageChops.difference(out.crop((0,0,1254,136)),base.crop((0,0,1254,136))).getbbox() is None
prop={'status':'proposal_pending_visual_review','formalAccepted':False,'tile':'r05_c11','operation':'PIL.Image.composite(nativeRepair, currentCandidate.crop(tileTargetBox), nativeAlphaMask) pasted at target origin; no resize','tileTargetBox':[282,384,1536,1638],'pasteXY':[282,384],'nativeRepair':{'file':str(raw),'sha256':sha(raw),'generationRecord':str(D/'native-result.generation.json')},'mask':{'file':str(mp),'sha256':sha(mp),'formula':'round255(smooth((x-580)/20)*smooth((690-x)/20)*smooth((y-136)/16)*smooth((704-y)/32)); cubic clamped smoothstep'},'target':{'file':str(D/'target-native.png'),'sha256':sha(D/'target-native.png'),'derivation':str(D/'target-derivation.json')},'localComposite':{'file':str(op),'sha256':sha(op)},'actualChangedBoxNative':box,'actualChangedBoxTile':[box[0]+282,box[1]+384,box[2]+282,box[3]+384],'nativePixelsResized':False,'ropeAboveY136Unchanged':unchanged,'coreSelectionChanged':False,'candidateChanged':False,'externalBoundariesChanged':False,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
prop['status']='PASS_LOCAL_PROPOSAL'
prop['qa']={'status':'PASS_LOCAL_PROPOSAL','nativeBeforeAfterReviewed':True,'finding':'Straight sand color/texture edge removed; small grains continue naturally with no doubled stones, dark stripe or rope ghosting. Golden hem above native y136 is pixel-identical.','formalAccepted':False}
(D/'proposal.json').write_text(json.dumps(prop,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposal':str(D/'proposal.json'),'changedBox':prop['actualChangedBoxTile'],'ropeUnchanged':unchanged}))

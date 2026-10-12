import sys,os
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));import pipeline as p
d=Path(sys.argv[1]);receipt=p.read(d/'receipt.json');args=p.read(d/'parameters.json');src=Path(receipt['hostSource']);dst=d/'raw-native.png';assert not dst.exists()
p.put_bytes(dst,src.read_bytes());im=Image.open(dst);assert im.size==(1254,1254)
rec={'file':str(dst),'sha256':p.sha(dst),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'opaque':im.convert('RGBA').getchannel('A').getextrema()==(255,255),'tool':'image_gen.imagegen','route':'builtin','hostSource':str(src),'hostBytesMatch':p.sha(src)==p.sha(dst),'actualModel':None,'actualQuality':None,'submittedParameters':args,'references':[p.reference(f,'actual submitted reference') for f in args.get('referenced_image_paths',[])],'preparation':str(d/'preparation.json'),'receipt':str(d/'receipt.json'),'resizedAfterGeneration':False,'finalArtUpscaled':False,'formalAccepted':False}
p.put_json(Path(str(dst)+'.generation.json'),rec)
statefile=ROOT/'production-resume-20261012.json';state=p.read(statefile)
new={'file':str(dst),'sha256':rec['sha256'],'pixels':[1254,1254],'record':str(dst)+'.generation.json','hostSource':str(src),'parameters':str(d/'parameters.json'),'savedAt':p.now()}
state.setdefault('newRawOutputsThisResume',[]).append(new);state['newRawOutputCount']=len(state['newRawOutputsThisResume']);state.setdefault('firstNewGeneratedOutput',None)
if state['firstNewGeneratedOutput'] is None:state['firstNewGeneratedOutput']=new
if state.get('currentToolError'):state.setdefault('historicalErrors',[]).append(state['currentToolError']);state['currentToolError']=None
state.update({'status':'builtin_success_native_repairs_in_progress','updatedAtUtc':p.now(),'generationCurrentlyOnHoldForActualPermissionFailure':False,'lastActualBuiltinSuccess':new,'nextStep':'Continue targeted native repairs and inspect only affected join crops before adopting.'})
tmp=ROOT/'finish-20261012/resume-writing.json';p.put_json(tmp,state);os.replace(tmp,statefile)
progress=p.read(ROOT/'progress.json');progress.update({'status':state['status'],'updatedAt':p.now(),'generationStopped':False,'generationHoldReason':None,'currentToolError':None,'newRawOutputCountThisResume':state['newRawOutputCount'],'firstNewGeneratedOutputThisResume':state['firstNewGeneratedOutput'],'lastActualBuiltinSuccess':new,'currentCoordinate':p.read(d/'preparation.json').get('tile'),'nextStep':state['nextStep']});p.replace_json(ROOT/'progress.json',progress)
print({'file':str(dst),'sha256':rec['sha256'],'pixels':im.size,'savedNewRawCount':state['newRawOutputCount']})


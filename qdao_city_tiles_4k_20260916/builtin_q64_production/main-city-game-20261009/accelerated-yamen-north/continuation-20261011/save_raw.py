import sys,json,shutil,os
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
d=Path(sys.argv[1]);version=sys.argv[2];receipt=p.read(d/f'receipt-{version}.json');src=Path(receipt['hostSource']);dest=d/f'raw-{version}.png'
assert not dest.exists();shutil.copy2(src,dest);im=Image.open(dest);assert im.size==(1254,1254)
args=p.read(d/f'parameters-{version}.json')
rec={'file':str(dest),'sha256':p.sha(dest),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'opaque':im.convert('RGBA').getchannel('A').getextrema()==(255,255),'tool':'image_gen.imagegen','route':'builtin','hostSource':str(src),'hostBytesMatch':p.sha(src)==p.sha(dest),'actualModel':None,'actualQuality':None,'submittedParameters':args,'references':[p.reference(f,'actual submitted reference') for f in args.get('referenced_image_paths',[])],'preparation':str(d/'preparation.json'),'receipt':str(d/f'receipt-{version}.json'),'resizedAfterGeneration':False,'finalArtUpscaled':False,'formalAccepted':False}
p.put_json(Path(str(dest)+'.generation.json'),rec)
status=p.read(ROOT/'local-continuation-20261011.json');status['newPixelsGeneratedThisRound']=True;status['status']='builtin-resumed-real-output-saved-repair-in-progress';status['updatedAtUTC']=p.now();status.setdefault('outputsThisRound',[]).append({'file':str(dest),'sha256':rec['sha256'],'pixels':[1254,1254],'receipt':rec['receipt']});status.setdefault('firstPostRestorationActualOutput',{'file':str(dest),'sha256':rec['sha256'],'hostSource':str(src),'pixels':[1254,1254],'submittedParameters':str(d/f'parameters-{version}.json')});status['blockers']=['Known structure repairs still pending; unavailable outer neighbors remain pending.'];status['gitPolicy']='No Git operations by this chat. Central migration thread 01a11b5e-158a-77d0-8c02-e8e503b7abe4 owns commit/push; no owned Git scripts exist.'
tmp=ROOT/'continuation-20261011/local-status-writing.json';p.put_json(tmp,status);os.replace(tmp,ROOT/'local-continuation-20261011.json')
progress=p.read(ROOT/'progress.json');progress['status']=status['status'];progress['firstPostRestorationActualOutput']=status['firstPostRestorationActualOutput'];progress['nextStep']='Repair r03_c05 / r04_c05 shared southern structure boundary using recorded builtin outputs';p.replace_json(ROOT/'progress.json',progress)
print(json.dumps({'file':str(dest),'sha256':rec['sha256'],'pixels':[1254,1254],'hostBytesMatch':True}))

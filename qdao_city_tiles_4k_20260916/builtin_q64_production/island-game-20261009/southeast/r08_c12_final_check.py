from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,os,sys
from datetime import datetime,timezone
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
REV=sys.argv[1] if len(sys.argv)>1 else 'v11'
A=R/f'tiles/r08_c12.candidate-{REV}.png'; B=R/'qa/r08_c12-r09c12-counterpart-v11.png'; O=R/'tiles/r09_c12.candidate-v02.png'
im=Image.open(A).convert('RGB'); rec=read(str(A)+'.generation.json')
replay=Image.new('RGB',(4096,4096));cover=np.zeros((4096,4096),dtype=np.uint8); sources=[]
for i,s in enumerate(rec['contributions']+rec['repairOverlays']):
 p=Path(s['file']);native=Image.open(p);b=s['destinationBox'];crop=s['sourceCrop'];piece=native.crop(crop)
 assert piece.size==(b[2]-b[0],b[3]-b[1]);replay.paste(piece,b[:2])
 if i<16:cover[b[1]:b[3],b[0]:b[2]]+=1
 sources.append(dict(s,shaMatch=sha(p)==s['sha256'],nativeSize=list(native.size)))
r={'auditedAt':datetime.now(timezone.utc).isoformat(),'candidate':str(A),'candidateSha256':sha(A),'baseCoreCount':16,'repairOverlayCount':len(rec['repairOverlays']),'allSourceHashesMatch':all(s['shaMatch'] for s in sources),'allNative1254':all(s['nativeSize']==[1254,1254] for s in sources),'baseCoverageMin':int(cover.min()),'baseCoverageMax':int(cover.max()),'replayPixelExact':bool(np.array_equal(np.array(replay),np.array(im))),'sources':sources,'resizing':False,'blending':False,'formalAccepted':False}
br=read(str(B)+'.generation.json'); bp=Image.open(O).convert('RGB')
for s in br['contributions']:bp.paste(Image.open(s['file']).crop(s['sourceCrop']),s['destinationBox'][:2])
r['counterpart']={'file':str(B),'sha256':sha(B),'base':str(O),'baseSha256':sha(O),'replayPixelExact':bool(np.array_equal(np.array(bp),np.array(Image.open(B).convert('RGB')))),'contributions':br['contributions'],'status':'proposal_only_not_applied_to_r09'}
write(R/f'qa/r08_c12.replay-{REV}.json',r)
for rr in range(1,4):
 for cc in range(1,4): im.crop((cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256)).save(R/'qa'/f'r08_c12.junction_{rr}{cc}-{REV}.png')
for typ,bb in [('proposed',B),('current',O)]:
 c=Image.new('RGB',(4096,512));c.paste(im.crop((0,3840,4096,4096)),(0,0));c.paste(Image.open(bb).crop((0,0,4096,256)),(0,256))
 for col in range(4):c.crop((col*1024,0,(col+1)*1024,512)).save(R/'qa'/f'r08_c12-{REV}-to-r09-{typ}-col{col+1}.png')
im.crop((3866,1536,4096,3072)).save(R/f'qa/r08_c12.{REV}-right-paving-perimeter.png')
records=sorted((R/'native').glob('r08_c12*.png.generation.json'));audit=[]
for p in records:
 q=read(p); f=Path(q['file']); prompt=Path(q['prompt']); receipt=R/q['evidence']['toolReceipt']; refs=[]
 for t in q['references']:
  ref=Path(t['file']);refs.append({'file':str(ref),'exists':ref.exists(),'shaMatch':sha(ref)==t['sha256'] if ref.exists() else False})
 audit.append({'record':str(p),'file':str(f),'shaMatch':sha(f)==q['sha256'],'nativeSize':list(Image.open(f).size),'promptExists':prompt.exists(),'promptNonempty':bool(prompt.read_text(encoding='utf-8').strip()),'promptShaMatch':sha(prompt)==q['promptSha256'],'receiptExists':receipt.exists(),'references':refs,'actualModelNull':q.get('actualModel') is None,'actualQualityNull':q.get('actualQuality') is None,'submittedParameters':q.get('submittedParameters'),'configSnapshotIsTargetOnly':True,'sourceHostHashMatch':sha(q['sourceOutputPath'])==q['sourceOutputSha256'] if Path(q['sourceOutputPath']).exists() else None})
write(R/f'qa/r08_c12.source-audit-{REV}.json',{'auditedAt':r['auditedAt'],'count':len(audit),'snapshot':[str(p) for p in records],'records':audit,'historicalMissingStyleNote':'Old PNG reference retained unchanged in original pre-resume records; current JPG authorized replacement is used by all new resume generations. Model and quality remain undisclosed.'})
print(json.dumps({k:v for k,v in r.items() if k not in ('sources','counterpart')},ensure_ascii=False));print(json.dumps({'nativeCount':len(audit),'counterpartReplayExact':r['counterpart']['replayPixelExact'],'newRecordsAllChecks':all(a['shaMatch'] and a['promptShaMatch'] and a['receiptExists'] for a in audit)},ensure_ascii=False))


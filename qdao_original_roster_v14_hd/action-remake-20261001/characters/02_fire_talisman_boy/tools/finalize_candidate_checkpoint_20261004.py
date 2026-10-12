from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stem='run-E-09-20261004-grounding-v2-02'
native=R/'work'/'root-ground-fix'/f'{stem}-native.png'
rp=R/'records'/f'{stem}.json';rec=json.loads(rp.read_text(encoding='utf-8-sig'));im=Image.open(native)
rec.update(status='generated_central_support_candidate_final_allocation_pending',native={'sourceFile':str(native),'sha256':sha(native),'width':im.width,'height':im.height,'mode':im.mode},actualModel=None,actualQuality=None)
rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
cp=R/'reviews'/'grounding-v2-root-candidates.json';c=json.loads(cp.read_text(encoding='utf-8'))
for f in c['frames']:
 if f['direction']=='E' and f['frame']==9:
  f.update(nativePath=str(native.relative_to(R)).replace('\\','/'),nativeSha256=sha(native),record=str(rp.relative_to(R)).replace('\\','/'))
c['generatedAttemptsWithReceipt']=6
cp.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,560),(246,242,230));draw=ImageDraw.Draw(sheet)
for i,x in enumerate(c['frames']):
 for row,p in enumerate([R/'frames'/'run'/x['direction']/f"{x['frame']:02}.png",R/x['nativePath']]):
  im=Image.open(p).convert('RGBA').resize((248,248),Image.Resampling.LANCZOS);sheet.paste(im,(i*256,row*280+28),im);draw.text((i*256+12,row*280+8),f"{x['direction']} {x['frame']:02} / "+('current' if row==0 else 'candidate'),fill=(30,65,55))
sheet.save(R/'previews'/'grounding-new-keyposes-20261004.png')
unknown=Path('C:/Users/luyua/.codex/generated_images/01a0fcf5-e5d7-7461-80df-79c90391ec08/exec-615ada4f-2d3f-4e90-9c9e-c7d11bb03d31.png')
u=R/'work'/'root-ground-fix'/'interrupted-SE-unassigned-20261004-native.png';shutil.copy2(unknown,u)
interrupted=[]
for f in [1,2,16]:
 p=R/'records'/f'run-SE-{f:02}-20261004-grounding-v2-01.json'
 rec=json.loads(p.read_text(encoding='utf-8'));rec['status']='call_interrupted_receipt_not_captured';rec['interruptionEvidence']='exec cell 135 not found after new user steering; no returned receipt available; do not assign untracked native by guess'
 p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');interrupted.append(str(p.relative_to(R)).replace('\\','/'))
(R/'reviews'/'grounding-interrupted-call-20261004.json').write_text(json.dumps({'callRecords':interrupted,'unassignedNative':str(u.relative_to(R)).replace('\\','/'),'nativeSha256':sha(u),'evidence':'Observed new host PNG after interrupted calls; exact slot and raw result unconfirmed. Not imported.','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'STATUS.md';s=p.read_text(encoding='utf-8');s+='\n最新细化：中间接地4帧、旁边各2帧；已询问旁边是沿行进方向身体前后或画面左右，空间分配尚待明确。中间承重候选继续制作，尚未正式替换。东/东南已有6次带回执候选生成，当前5个选用候选槽位见 reviews/grounding-v2-root-candidates.json。\n';p.write_text(s,encoding='utf-8')
print({'selectedKeyCandidates':5,'capturedGenerations':6,'formalReplaced':False,'spatialAllocation':'clarification_pending'})

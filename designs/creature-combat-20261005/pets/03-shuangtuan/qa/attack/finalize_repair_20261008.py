from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, shutil, numpy as np
from datetime import datetime, timezone

b=Path(r'D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r): p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
config=read(Path(r'D:/work/image/config/image-generation.json'))
reviewed_at=datetime.now(timezone.utc).isoformat()
metrics=[]
for n in ['10','11','12']:
    native=b/f'source/attack/repair-20261008/W-{n}-native-b.png'
    cand=b/f'source/attack/repair-20261008/W-{n}-candidate-b.png'
    target=b/f'runtime/attack/W/{n}.png'
    req=read(b/f'records/attack/W/repair-20261008/{n}.repair-b.request.json')
    receipt=read(b/f'records/attack/W/repair-20261008/{n}.repair-b.receipt.json')
    im=Image.open(native);out=Image.open(cand)
    assert out.size==(1024,1024) and out.mode=='RGBA' and out.getchannel('A').getextrema()==(0,255)
    native_sha=sha(native)
    refs=[]
    roles=['edit target from first repair, RH-only further adjustment','W09 planted RH stance reference','W01 terminal stance reference','original E/W identity reference board','approved primary painted style reference']
    for path,role in zip(req['actualArguments']['referenced_image_paths'],roles):
        p=Path(path);ref={'path':path,'purpose':role,'sha256':sha(p)}
        if p.name==f'W-{n}-candidate.png':ref['generationRecord']=f'records/attack/W/repair-20261008/{n}.repair.generation.json'
        if p.name=='identity-EW-reference.png':ref['derivationRecord']='records/attack/W/repair-20261008/identity-EW-reference.json'
        refs.append(ref)
    r={'file':target.relative_to(b).as_posix(),'sha256':sha(cand),'generatedAt':receipt['completedAt'],'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':req['actualArguments']['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露 model / quality；无可核实元数据。','prompt':f'prompts/attack/W-{n}-repair-20261008-b.txt','references':refs,'evidence':[f'records/attack/W/{n}.request.json',f'records/attack/W/{n}.receipt.json'],'native':{'file':native.relative_to(b).as_posix(),'sha256':native_sha,'width':im.width,'height':im.height,'format':'PNG','mode':im.mode},'derivedFrom':{'file':native.relative_to(b).as_posix(),'sha256':native_sha,'operation':'uniform-square-resize','scale':1024/im.width,'translation':[0,0],'mirrored':False,'perFrameAlignment':False},'editHistory':[f'records/attack/W/repair-20261008/{n}.previous.generation.json',f'records/attack/W/repair-20261008/{n}.repair.generation.json'],'visualQA':{'reviewed':True,'reviewedAt':reviewed_at,'status':'static-adjacent-accepted-dynamic-pending','notes':'实际查看最终1024帧及W09/W01；RH支撑由09连续收回，原80px单帧内缩已消除。LF下降/落地/警戒阶段、另一后足、后脑背向与单尾/饰品保留。仅相邻静态通过；连播由主任务另验。'},'event':None,'durationMs':30,'pivot':[0.5,0.08]}
    shutil.copy2(cand,target)
    assert sha(target)==r['sha256']
    shutil.copy2(b/f'records/attack/W/repair-20261008/{n}.repair-b.request.json',b/f'records/attack/W/{n}.request.json')
    shutil.copy2(b/f'records/attack/W/repair-20261008/{n}.repair-b.receipt.json',b/f'records/attack/W/{n}.receipt.json')
    write(b/f'records/attack/W/{n}.generation.json',r)
    write(b/f'records/attack/W/repair-20261008/{n}.repair-b.generation.json',r)

# Read-only pixel measurements; no alignment or anatomical manipulation.
for n in ['01','08','09','10','11','12']:
    p=b/f'runtime/attack/W/{n}.png';a=np.array(Image.open(p))[:,:,3]
    data={'frame':n,'file':p.relative_to(b).as_posix(),'sha256':sha(p)}
    for part,(x0,x1) in {'RH':(600,860),'LH':(360,570)}.items():
        ys,xs=np.where(a[890:990,x0:x1]>=128);mask=ys>=ys.max()-5
        data[part]={'soleBandCenter':[float(xs[mask].mean()+x0),float(ys[mask].mean()+890)],'method':'alpha>=128 visible contour lowest 6 rows within fixed ROI; not skeletal joint/contact point'}
    metrics.append(data)
write(b/'qa/attack/repair-20261008-metrics.json',{'reviewedAt':reviewed_at,'frames':metrics})

# Current final-assets-only comparison preview; never used as runtime sprite.
sheet=Image.new('RGB',(1536,1040),(45,53,52));d=ImageDraw.Draw(sheet)
for i,n in enumerate(['08','09','10','11','12','01']):
    im=Image.open(b/f'runtime/attack/W/{n}.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
    x=(i%3)*512;y=(i//3)*520;sheet.paste(im,(x,y+8),im);d.text((x+12,y+12),'attack W '+n,fill=(255,255,255))
sheet.save(b/'qa/attack/repair-20261008-current-sheet.png')
print(json.dumps({'updated':['runtime/attack/W/10.png','runtime/attack/W/11.png','runtime/attack/W/12.png'],'metrics':metrics},ensure_ascii=False,indent=2))

from pathlib import Path
import av,json,hashlib
from PIL import Image,ImageDraw
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
V=Path(r'C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=R/'work'/'video-axis';out.mkdir(exist_ok=True)
starts=[0.25,5.6,11.1,14.7]
sheets=[Image.new('RGB',(1600,440),'#e9e4da') for _ in range(4)]
counts=[0]*4;samples=[]
for fr in av.open(str(V)).decode(video=0):
    t=float(fr.time)
    for j,start in enumerate(starts):
        if t>=start and counts[j]<16:
            i=counts[j];counts[j]+=1
            im=fr.to_image().crop((520,170,760,410)).resize((200,200))
            # Preview crop only; original video and formal game PNG remain untouched.
            sheets[j].paste(im,((i%8)*200,(i//8)*220))
            ImageDraw.Draw(sheets[j]).text(((i%8)*200+4,(i//8)*220+200),f'{t:.3f}s',fill='black')
            samples.append({'clip':j,'index':i,'videoTime':t})
    if sum(counts)==64:break
for j,im in enumerate(sheets):im.save(out/f'reference-continuous-{j}.jpg',quality=93)
(R/'reviews/video-reference-sampling-20261004.json').write_text(json.dumps({'source':str(V),'sourceSha256':hashlib.sha256(V.read_bytes()).hexdigest(),'timeUtc':datetime.now(timezone.utc).isoformat(),'fps':24,'samples':samples,'crop':[520,170,760,410],'limits':'low-resolution video character and UI occlusion; broad movement direction only, not proof of toe joint alignment','operation':'read video, consecutive source frames at24fps, crop for review only'},ensure_ascii=False,indent=2),encoding='utf-8')
review=json.loads((R/'reviews/final-review.json').read_text(encoding='utf-8'))
review['knownUnresolvedArtFailures']=['Reopened for video-axis feedback; SE11-14 and selected NE/NW swing-foot axes are being corrected. Other directions under fresh review.']
review['videoAxisRevision']={'status':'in_progress','startedAtUtc':datetime.now(timezone.utc).isoformat(),'reference':'reviews/video-reference-sampling-20261004.json'}
(R/'reviews/final-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'STATUS.md';s=p.read_text(encoding='utf-8')
p.write_text('# 02 火符少年当前进度\n\n2026-10-04：收到视频方向反馈后重新开启跑步脚轴复核。正在修SE11–14与NE/NW选定外扭帧，逐方向复验相邻动作；旧离线完成结论仅对应上一轮。196张库存仍齐全，当前视频方向修订未完成。16×75ms=1200ms，两帧一个接地位置段保持。客户端未接入。\n\n上一轮交付记录保留在MERGE_HANDOFF.md，最终会更新为本轮结果。过程图清理此前被自动审批拦截，本轮不绕过重试。\n',encoding='utf-8')
print({'samples':len(samples),'sheets':len(sheets)})

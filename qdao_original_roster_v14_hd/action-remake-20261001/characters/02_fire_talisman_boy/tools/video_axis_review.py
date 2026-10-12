import json,hashlib,argparse
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];W=R/'work/video-axis-ne-nw';W.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--reviewed',action='store_true');a=p.parse_args()
changed={'NE':[7,14,15],'NW':[1,2,3,4,5,6,7,8,16]}
reasons={
'NE':{**{f:'右脚支撑在膝下或沿行进面后移；左腿自然屈膝，后跟与小腿方向连续，无新增侧翻。' for f in [1,2,3,4,5,6,16]},**{f:'左足中段承重、右腿折回，鞋底可见来自自然后视透视，未见踝处突然横折。' for f in [8,9,10,11]},**{f:'左腿后支撑沿同一运动面伸展，鞋跟端面跟随小腿；右抬脚维持正常屈膝。' for f in [12,13]}},
'NW':{**{f:'右足支撑链连续，近左腿折回且鞋底长轴跟随小腿，未见横转恢复脚的缺陷。' for f in [1,3,5,7]},**{f:'左足着地缓冲、右腿自然后屈，保留远近腿透视和膝踝连接。' for f in [9,10]},**{f:'左支撑脚在髋膝下方持续承重，右脚回收轮廓顺腿，无C形外滚。' for f in [11,12,13,14]},15:'左足后端支撑，远右膝屈曲与鞋底视角连续，无16帧原有的恢复鞋外扭。'}
}
rows=[];previews=[]
for d,ip in [('NE','inventory-run-ne-cast.json'),('NW','inventory-run-nw-finish.json')]:
    iv=json.loads((R/ip).read_text(encoding='utf-8'));ims=[]
    for e in sorted(iv['frames'],key=lambda e:e['frame']):
        f=e['frame'];fp=R/e['path'];im=Image.open(fp).convert('RGBA');assert im.size==(1024,1024);assert sha(fp)==e['sha256'];assert im.getchannel('A').getextrema()==(0,255)
        sc=json.loads(fp.with_suffix('.png.generation.json').read_text(encoding='utf-8'));assert sc['sha256']==sha(fp)
        replaced=f in changed[d];rec=json.loads((R/e['native_evidence']).read_text(encoding='utf-8-sig'))
        reason=rec['visualQA']['notes'] if replaced else reasons[d][f]
        row={'path':e['path'],'sha256':sha(fp),'direction':d,'frame':f,'decision':'replaced' if replaced else 'retained','reason':reason,'generationRecord':e['native_evidence'],'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'size':[1024,1024],'mode':'RGBA','frameDurationMs':75}
        if replaced:row['previousSHA256']=rec['replaces']['sha256']
        rows.append(row);ims.append(im)
        e['visual_status']='video_axis_static_review_pass_dynamic_pending' if a.reviewed else 'video_axis_final_contact_review_pending';e['sequence_review']='reviews/video-axis-NE-NW-20261004.json'
    assert len(ims)==16
    contact=Image.new('RGB',(1280,1408),(39,51,64));draw=ImageDraw.Draw(contact)
    for i,im in enumerate(ims):
        x=i%4*320;y=i//4*352;sm=im.resize((320,320),Image.Resampling.LANCZOS);contact.paste(sm,(x,y),sm);draw.text((x+8,y+326),f'{d} {i+1:02d} '+('REVISED' if i+1 in changed[d] else 'KEPT'),fill='white')
    contact.save(W/f'{d}-contact.jpg',quality=95)
    small=[im.resize((384,384),Image.Resampling.LANCZOS) for im in ims]
    for name,ms in [('normal',75),('slow',300)]:
        ap=W/f'{d}-{name}.apng';small[0].save(ap,save_all=True,append_images=small[1:],duration=ms,loop=0,disposal=0,blend=0)
        anim=Image.open(ap);duration=0
        for i in range(anim.n_frames):anim.seek(i);duration+=anim.info['duration']
        assert anim.n_frames==16 and duration==16*ms
        previews.append({'path':ap.relative_to(R).as_posix(),'sha256':sha(ap),'frames':16,'durationMs':duration})
    iv['qa_summary']={'completeSequencePassed':False,'staticAxisReview':'passed' if a.reviewed else 'pending','dynamicStatus':'root_unified_review_pending','clientStatus':'not_integrated','review':'reviews/video-axis-NE-NW-20261004.json'}
    (R/ip).write_text(json.dumps(iv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
refs=['../../reference-motion-review-20261004/video-contact.jpg','../../reference-motion-review-20261004/character-detail.jpg','C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7cc4bf22-e4cf-4c35-8ac6-a37fd85f4037.png']+[f'work/video-axis/reference-continuous-{i}.jpg' for i in range(4)]
report={'character':'02_fire_talisman_boy','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'static_axis_review_pass_pending_root_dynamic' if a.reviewed else 'final_contact_review_pending','frames':rows,'revisedCount':8,'retainedCount':24,'referenceReview':{'actuallyViewed':refs,'limitations':'视频低清且HUD遮挡，仅对照整体运动平面；膝踝鞋掌依正式1024图实际逐图判断，不声称视频提供精确关节测量。'},'timing':{'framesPerDirection':16,'frameDurationMs':75,'cycleMs':1200,'twoFramePositionSegmentMs':150,'supportMappingPreserved':True},'previews':previews,'knownUnresolvedArtFailures':[] if a.reviewed else None,'dynamicReview':'由root统一浏览器正常/慢放/逐帧复核，本报告不复用旧动态通过结论。','clientStatus':'not_integrated','modelQuality':'目标GPT Image2.5 Sunburst/max；内置实际model/quality没有选择器且未披露返回确认，均为null。'}
report['revisedCount']=sum(len(v) for v in changed.values());report['retainedCount']=len(rows)-report['revisedCount']
(R/'reviews/video-axis-NE-NW-20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html='''<!doctype html><meta charset="utf-8"><title>02 NE/NW 视频脚轴复核</title><style>body{background:#243440;color:#fff;font:16px system-ui;padding:20px}main{display:flex;gap:24px}img{width:384px;height:384px;background:#e5e1d3}button,select,input{margin:6px;padding:6px}section{text-align:center}</style><h1>02 NE / NW · 视频脚轴修订</h1><p>每帧75ms，整圈1200ms；慢放4800ms。正式1024原图，无逐帧贴地。</p><button id="play">暂停</button><select id="speed"><option value="75">正常1200ms</option><option value="300">慢放4800ms</option></select><input id="frame" type="range" min="1" max="16" value="1"><span id="label"></span><main><section>NE<br><img id="NE"></section><section>NW<br><img id="NW"></section></main><script>let f=0,run=true,start=performance.now(),ms=75;const imgs={};for(const d of ['NE','NW'])imgs[d]=Array.from({length:16},(_,i)=>{let x=new Image();x.src='../../frames/run/'+d+'/'+String(i+1).padStart(2,'0')+'.png?v=videoaxis';return x});function show(){for(const d of ['NE','NW'])document.getElementById(d).src=imgs[d][f].src;frame.value=f+1;label.textContent='第'+(f+1)+'帧'}play.onclick=()=>{run=!run;play.textContent=run?'暂停':'播放';start=performance.now()-f*ms};speed.onchange=()=>{ms=Number(speed.value);start=performance.now()-f*ms};frame.oninput=()=>{run=false;play.textContent='播放';f=Number(frame.value)-1;show()};function tick(t){if(run){let n=Math.floor((t-start)/ms)%16;if(n!==f){f=n;show()}}requestAnimationFrame(tick)}show();requestAnimationFrame(tick)</script>'''
(W/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'frames':len(rows),'revised':report['revisedCount'],'retained':report['retainedCount'],'status':report['status']}))

import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];W=R/'work/full-limb-cast-ne-nw';W.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review='reviews/full-limb-cast-NE-NW-20261004.json'
groups=[('cast','E','inventory-cast.json'),('cast','W','inventory-cast.json'),('run','NE','inventory-run-ne-cast.json'),('run','NW','inventory-run-nw-finish.json')]
hands_cast={
'E':{1:'右肘收在胸前，右腕托五符；左手握铃在身后低位，袖口与手腕相接。',2:'五符在胸前展开且边缘可数，右腕不反折；左铃仍在身后随肘抬高。',3:'右符臂胸前蓄力，左铃在身后，保持原左右持物并接入E04腰侧过渡。',4:'右五符抬到头侧、肘部弯曲；左拳在腰侧握单铃，两条臂链完整。',5:'右符继续抬高形成蓄力峰值，左铃贴胸，双手均有清楚袖口/腕连接。',6:'右五符向前送出，左铃臂后摆，肩肘腕随释放旋转没有多余手。',7:'右手向前释放五符，左手后铃沿左肩链相连，握柄未脱手。',8:'右前伸五符与左后摆单铃保持，前臂不与袍摆混成第三肢。',9:'五符前送达到释放段，左后铃手握柄清楚，右腕与前臂同向。',10:'右符手在释放末段开始回收，左臂后摆幅度保持合理。',11:'两臂回收，右符和左铃各自连接所属袖口，未左右互换。',12:'右五符回到胸前，左单铃垂向身后，屈肘回收自然。',13:'五张重叠符卡可数；右腕承托、左手握单铃，肩肘连接完整。',14:'收招五符置胸前，左铃放低，双臂不交叉穿躯干。',15:'右五符胸前、左铃身后低垂，手指与握持点连续。',16:'近待机收招，右符扇和左铜铃握持与首帧一致。'},
'W':{1:'近侧左手握单铃，远侧右手托五符，最左重叠符仍可辨。',2:'左铃开始抬高，右五符维持胸前，袖口与腕部相连。',3:'左铃收到胸侧，右五符贴近前胸，手肘收拢且未穿插。',4:'右符扇抬高蓄力，左铃随屈肘上提，两腕分别握原道具。',5:'右五符向前伸展、左铃臂向后打开，释放预备的双肩连接清楚。',6:'五符为五张（含最左低角重叠一张），前右臂与后左铃臂连贯，无缺符。',7:'前方右手持五符、后方左拳握铃，肘腕同向不反折。',8:'右臂继续前送，左铃臂后摆，未额外生出袖内手指。',9:'五符完全展开，左铃在后侧，两臂沿各自肩部接回躯干。',10:'释放末段，右前腕和五符连接、左后腕和铃柄连接均正确。',11:'收招开始，右扇回收而左铃下降，两臂保持各自道具。',12:'右五符胸前回收，左铃回到身侧，屈肘形状自然。',13:'前胸五符未缺张，近侧左拳仍握单铃，袖口腕部无断裂。',14:'五符含重叠边角完整，左铃垂于身侧，手指握柄稳定。',15:'右五符胸前、左铃低垂回到待机阶段，两腕连续。',16:'五符和单铃与首帧同侧，收招闭环无持物互换。'}
}
cast_legs={1:'双足平放，髋膝在各自支撑脚上方，鞋头顺前进方向。',2:'轻屈膝预备，双脚未横叉，膝踝与鞋头顺同一运动平面。',3:'预备下沉，两膝自然屈曲，前后支撑脚鞋头仍顺向。',4:'蓄力双足承重，膝盖未机械锁死，踝和鞋掌无向侧面拧折。',5:'蓄力开始展开前后步，髋—膝—踝仍各自顺向，未横向劈叉。',6:'释放前后弓步，前脚承重后脚支撑；两鞋长轴与前进方向一致。',7:'弓步膝弯保留，前膝落在前脚轨道内，后腿沿前后轴展开。',8:'释放大步维持，前后足在同向运动平面，鞋掌未在踝处横撇。',9:'重心偏前且膝弯自然，后腿伸展为前后支撑而非侧向劈叉。',10:'释放末段前后支撑连续，双踝与各自鞋头方向一致。',11:'支撑逐渐收窄，两鞋继续顺向，前膝回收未反关节。',12:'收招双膝回收，脚掌落点与髋膝方向一致，未突然横转鞋头。',13:'收招较窄站位，双踝位于各自膝下，两脚顺向。',14:'近待机轻屈膝，鞋掌前后向清楚，未横叉。',15:'重心回中，两脚平放同向，膝踝保持自然屈曲。',16:'收招站稳，两鞋头同向，支撑链与首帧连贯。'}
nelegs={1:'右足中央支撑，髋膝踝沿东北前后面，左腿后屈且鞋底顺小腿。',2:'右足稍后承重，右鞋头与小腿同向，左足离地回收不侧翻。',3:'继续右足稍后支撑，膝踝轨迹同向，左鞋纵轴顺恢复小腿。',4:'右足后支撑，右膝自然弯曲；左脚后屈未横向扭踝。',5:'右支撑腿随重心后移，鞋头保持东北轴，抬腿不横叉。',6:'右足后蹬开始，膝踝鞋轴延续；左恢复腿屈膝并露鞋底。',7:'右足后蹬，左恢复鞋已沿小腿收正，保留屈膝和后视透视。',8:'左足中央接地，左踝在膝下、鞋头顺向；右腿后屈离地。',9:'左足中央承重，左髋膝踝连续，右后屈鞋掌不横撇。',10:'左足稍后支撑，右恢复足继续顺腿折回，双腿无横叉。',11:'左支撑膝踝同轨，右腿屈曲恢复；袖口转动不影响支撑链。',12:'左足后支撑沿东北前后面伸展，鞋跟端面随小腿，右腿正常弯曲。',13:'左后支撑进一步伸展，鞋轴未在踝处外扭，右足回收连续。',14:'左足后蹬鞋掌顺小腿，右腿保持弯曲；露底来自后蹬而非横翻。',15:'左脚后蹬末段与右腿恢复均沿长轴，已保留前轮修正。',16:'右足接回中央支撑，左足后屈，右鞋与膝踝朝向一致且闭环首帧。'}
nwlegs={1:'右足中央支撑，膝踝与鞋跟长轴沿西北；左恢复足纵轴顺小腿。',2:'右足中央承重同段第二帧，左腿屈膝恢复，无鞋掌外滚。',3:'右脚稍后支撑，髋膝踝沿西北前后面，左足后屈不横转。',4:'右脚稍后承重保持，左恢复鞋底窄纵向，膝踝未折成侧向。',5:'右足后支撑沿前进面后伸，左腿正常折回而未横叉。',6:'右足后支撑第二帧，支撑鞋轴随小腿，左恢复鞋不侧翻。',7:'右足后蹬，后腿膝踝鞋轴连贯，左腿屈膝恢复保持笔直运动面。',8:'右后蹬末段，左脚回收转向接地且纵轴仍沿小腿，保留收臂过渡。',9:'左足中央接地缓冲，髋膝踝鞋头顺西北，右膝后屈露鞋底。',10:'左足中央支撑第二帧，膝踝不横折，右恢复脚沿腿纵向。',11:'左足稍后支撑，右足回收与近侧腿有透视重叠但不横叉。',12:'左脚继续稍后承重，鞋头沿西北，右足后屈未形成C形外滚。',13:'左足后支撑到身后，远近腿轮廓重叠符合透视，鞋掌各顺腿轴。',14:'左后支撑第二帧，只有两腿，右恢复鞋轴顺膝踝无第三肢。',15:'左足后蹬，鞋头与踝部同向，右腿后屈恢复正常。',16:'左足后蹬末段，右恢复鞋已收正随小腿，左支撑鞋仍沿西北轴。'}
rows=[];previews=[];inventories={}
for action,d,ip in groups:
    iv=inventories.setdefault(ip,json.loads((R/ip).read_text(encoding='utf-8')))
    entries=sorted([e for e in iv['frames'] if e['action']==action and e['direction']==d],key=lambda e:e['frame'])
    assert len(entries)==16
    ims=[];hashes=[]
    for e in entries:
        f=e['frame'];fp=R/e['path'];h=sha(fp);im=Image.open(fp).convert('RGBA');assert im.size==(1024,1024);assert im.getchannel('A').getextrema()==(0,255);assert e['sha256']==h
        ims.append(im);hashes.append(h)
        changed=action=='cast' and d=='E' and f==4 and '20261005' in e.get('source_record','')
        hand=hands_cast[d][f] if action=='cast' else ('右手五符扇、左手单铜铃，双侧肩袖—肘—腕连接可追踪，握持未互换。' if d=='NE' or f<8 else '右手仍持五符扇（部分远侧边角受头/躯干遮挡），左手握单铜铃；前后摆臂各自连回肩肘腕。')
        leg=cast_legs[f] if action=='cast' else (nelegs if d=='NE' else nwlegs)[f]
        reason=hand+leg
        if changed: reason='修复原E03→04两臂跨位过快：E04左铃回到腰侧中间位，右五符保持头侧蓄力。'+reason
        row={'action':action,'direction':d,'frame':f,'path':fp.relative_to(R).as_posix(),'sha256':h,'decision':'replaced' if changed else 'retained','reason':reason,'source_record':e.get('source_record'),'visualStatus':'current_original_full_canvas_and_limb_review_pass'}
        rows.append(row);e['full_limb_review']=review;e['full_limb_reviewed_at']=datetime.now(timezone.utc).isoformat()
    assert len(set(hashes))==16
    can=Image.new('RGB',(1600,1728),(36,52,64));draw=ImageDraw.Draw(can)
    for i,im in enumerate(ims):
        x=i%4*400;y=i//4*432;pic=im.resize((400,400),Image.Resampling.LANCZOS);can.paste(pic,(x,y),pic);draw.text((x+10,y+406),f'{action} {d} {i+1:02}',fill='white')
    cp=W/f'{action}-{d}-contact.jpg';can.save(cp,quality=97)
    ms=45 if action=='cast' else 60
    for speed,duration in [('normal',ms),('slow',ms*4)]:
        ap=W/f'{action}-{d}-{speed}.png';ims[0].save(ap,save_all=True,append_images=ims[1:],duration=duration,loop=0,disposal=0,blend=0)
        ck=Image.open(ap);assert ck.n_frames==16
        durations=[]
        for i in range(16):ck.seek(i);durations.append(ck.info['duration'])
        assert sum(durations)==16*duration
        previews.append({'action':action,'direction':d,'speed':speed,'path':ap.relative_to(R).as_posix(),'frameCount':16,'frameMs':duration,'durationMs':sum(durations),'sha256':sha(ap),'dynamicHumanReview':'pending_root_browser_review'})
    previews.append({'action':action,'direction':d,'path':cp.relative_to(R).as_posix(),'type':'full_canvas_contact','size':[1600,1728],'transform':'uniform whole1024canvas to400; no boundingbox normalization or pose warp','sha256':sha(cp)})
for ip,iv in inventories.items():(R/ip).write_text(json.dumps(iv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
replaced=[r for r in rows if r['decision']=='replaced']
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewDate':'2026-10-05','scope':'cast E/W + run NE/NW, 64 current formal PNGs','status':'static_limb_review_complete_dynamic_pending_root','frames':rows,'replacedCount':len(replaced),'retainedCount':64-len(replaced),'knownUnresolvedArtFailures':[] if replaced else ['cast/E03→04 两臂跨位过快待过渡修复'],'visualNotes':['重新实际查看64张正式原图，非复用旧通过结论。','重点查看支撑髋—膝—踝—鞋头同一前进面；保留正常屈膝、重心移位、前后弓步与后蹬，不机械锁膝。','数清五符扇重叠边角；铜铃为解剖左手单一握持，五符为解剖右手。','cast E03→04经相邻全尺寸复核确认缺少中间收臂位，单独修复E04左铃臂；E03原图、E05蓄力峰值及E06释放幅度保留。','本轮运行方向32张保留前轮脚轴修正，独立PNG非复制帧；未操作浏览器，动态由root统一复核。'],'previewArtifacts':previews,'timing':{'cast':{'frames':16,'frameMs':45,'durationMs':720},'run':{'frames':16,'frameMs':60,'durationMs':960}},'clientStatus':'not_integrated','generationModelEvidence':{'targetModel':'gpt-image-2.5-sunburst','targetQuality':'max','actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'note':'只经宿主管理内置imagegen；无型号/质量选择器与实际返回确认。旧记录不改写。'}}
(R/review).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cards=''.join(f'<section><h2>{a} {d}</h2><img src="{a}-{d}-normal.png"><p><a href="{a}-{d}-contact.jpg">16帧完整画布联系表</a> · <a href="{a}-{d}-slow.png">4倍慢放</a></p></section>' for a,d,_ in groups)
(W/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>02 手脚全查</title><style>body{background:#243440;color:#fff;font:16px system-ui;padding:20px}main{display:grid;grid-template-columns:1fr 1fr;gap:24px}img{width:448px;height:448px;background:#e7e3d7}a{color:#8fdfff}</style><h1>02 施法E/W、跑步NE/NW · 手脚全查</h1><p>完整1024画布等比显示。施法16×45=720ms，跑步16×60=960ms；不重新贴地或扭曲。</p><main>'+cards+'</main>',encoding='utf-8')
print(json.dumps({'frames':len(rows),'replaced':len(replaced),'retained':64-len(replaced),'report':review,'knownUnresolvedArtFailures':report['knownUnresolvedArtFailures']},ensure_ascii=False))

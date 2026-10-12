"""Snapshot actual selected native candidates and measured review observations.
Does not modify sprite pixels or infer contact from alpha minima.
"""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
versions=[1,1,4,5,3,1,1,3,1,1,4,7,2,1,2,1]
phases=['右初触','右承重缓冲','右压缩','右晚支撑/左通过','右前掌蹬离','离地','左前伸腾空','左落地准备','左初触','左承重缓冲','左支撑/右通过','左晚支撑','左前掌蹬离','右前摆腾空','下降','右落地准备']
observed=[('air','contact','前右靴近全掌，低于近侧候选平面约11原生px；与E02足部承重有区别，仍需连贯性复核。'),('air','weight','前右全掌近水平、膝收回，后脚离地。近侧候选平面来自该鞋底约1191–1196/1254。'),('air','weight','右膝屈曲更明显；远腿尚未明确前穿，头冠较E02上移。'),('air','push_off','右脚后移支撑、左腿前收；右脚跟稍抬，前掌接触候选。'),('air','push_off','后右靴跟抬高、前掌承重；近肩至前剑袖连接已修，头胸位置相对E04向左变化。'),('air','air','两脚离地，近右腿后收、远左前伸，短腾空；剑尖接近右边界。'),('air','air','远左腿前伸、脚跟接近地面但仍有间隙；近右腿折后。'),('air','air','左靴位于身体前下方，离地约46px；较E07有轻微反向升高及抬头，仍需修连续性。'),('contact','air','远左鞋底约1192，与远侧候选平面1189差3px；初触与E10缓冲差异偏小。'),('weight','air','左靴全掌支撑，近右腿后收，右剑前摆链条清楚。'),('weight','air','远左平底约1177，较远侧平面高约12px；标为支撑姿态候选，接触仍需校准。'),('unknown','air','以当前修稿实图重新复核，不能把提示词的最后前掌接触当成事实。'),('push_off','air','远左后跟抬高，前掌约1183，距远侧候选平面约6px；接触候选而非引擎事件。'),('air','air','右前摆鞋底约1129，距近侧地面66px；腾空偏高。'),('air','air','右前鞋底约1136，继E14后下降；仍偏高但不再先落地又离地。'),('air','air','右前鞋底约1159，约36px离地；至E01落地顺序合理，未整图下移。')]
dur=[75]*16
phases[7]='左脚跟初触（按实图修正）'
phases[8]='左脚早期承重'
observed[2]=('air','weight','03-v4右脚全掌承重、膝屈曲；近右剑手保持腹前，远左符手由前伸收至腰前，为02→04后摆加入中间位置。整画布对照确认两条手臂连续，未平移贴地。')
observed[3]=('air','push_off','04-v5近右剑手低髋前摆、近肩单袖肘手连接清楚；远左符手收近后腰，较04-v2减少后伸，与03-v4→05-v3连贯。后右前掌支撑、左腿前穿；修改为原生局部重绘，未整图贴地。')
observed[7]=('contact','air','08-v3远左脚跟初触候选：后跟约x885–920/y1188–1193，远侧诊断面1188.792；前掌仍抬起。07→08→09局部下降/接触顺序通过。')
observed[8]=('weight','air','左靴转全掌早期承重，鞋底约1192；08实图已经初触，09不再记首次接触。')
observed[10]=('weight','air','11-v4远左支撑、近右腿前摆；近肩单袖连剑手，剑改为近竖直，握点仍偏低。鞋底主要轮廓相对v3仅约1–3px变化，正常尺寸衔接以最新复核为准。')
observed[11]=('push_off','air','12-v7右拳收至腹前、屈肘连接近肩，剑朝左上；远左后跟抬高、前掌较低，近右前脚抬趾。已补前摆至后摆的中间姿态，接触及全圈复核见当前审阅。')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frames=[]
for i,v in enumerate(versions,1):
    p=R/f'drafts/run/E/{i:02}-v{v}.png'
    if not p.exists():
        raise FileNotFoundError(f'Explicitly selected frame is missing: {p}')
    im=Image.open(p);record=p.with_name(p.name+'.generation.json'); rec=json.loads(record.read_text(encoding='utf-8-sig'))
    l,r,detail=observed[i-1]
    frames.append({'frame':i,'path':p.relative_to(R).as_posix(),'sourcePath':p.relative_to(R).as_posix(),'sha256':sha(p),'nativeSize':list(im.size),'generationRecord':record.relative_to(R).as_posix(),'status':'selected_for_preview','plannedPhase':phases[i-1],'actualContact':{'left':l,'right':r,'confidence':'medium; physical_contact_unverified','evidence':detail},'notes':'实图人工相位候选；接触姿态不等于客户端碰撞/无滑步验收。','durationMs':dur[i-1],'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality')})
root={'point':[512,975.872],'farFootGroundY':970.752,'status':'provisional','definition':'固定虚拟世界根点，1024整画布坐标，近侧95.3%/远侧94.8%为实图鞋底推定的两条诊断轨道。近侧参考E02，远侧参考E09/E10；只供人工复核，不据alpha最低点修改任何帧。Unity候选pivot=[0.5,0.047]，尚非客户端合同。原942.08为旧提示词目标，未沿用为接地通过证据。'}
data={'schemaVersion':1,'characterId':R.name,'direction':'E','createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'nativeCanvasSize':[1254,1254],'root':root,'timing':{'status':'normal_preview_user_selected_client_unconfirmed','uniformCycleMs':1200,'frameDurationsMs':dur,'comparisonsMs':[],'reason':'用户最新指定16帧均匀75ms，整圈1200ms；正常1倍不再使用旧快速档或相位权重。实际接触仍按当前图观察，E01至E08为525ms，E08至下圈E01为675ms。','formallyAdopted':False,'offlineDefaultApplied':True},'frames':frames,'artStatus':'needs_sequence_correction','clientIntegrated':False,'clientRuntimeVerified':False,'formalExportCount':0,'events':{'kind':'manual_visual_hypotheses_not_runtime_events','rightContact':{'frame':1,'offsetMs':0,'confidence':'medium'},'leftContact':{'frame':8,'offsetMs':525,'confidence':'medium'},'rightToeOff':{'betweenFrames':[5,6],'offsetMs':375,'confidence':'medium'},'leftToeOff':{'betweenFrames':[13,14],'offsetMs':975,'confidence':'pending_E12_E13_contact_review'}}}
write(R/'review/run-E-selection.json',data)
write(R/'anchor.json',{'canvas':[1024,1024],'root_anchor':root['point'],'virtual_ground_y':root['point'][1],'far_foot_ground_y':root['farFootGroundY'],'status':'provisional','definition':root['definition'],'registrationApplied':False,'transform':'none; previews fit the entire square canvas uniformly'})
write(R/'review/technical-native.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'selectedCount':len([x for x in frames if x]),'checks':[{'frame':f['frame'],'path':f['path'],'sha256MatchesRecord':f['sha256']==json.loads((R/f['generationRecord']).read_text(encoding='utf-8-sig'))['sha256'],'size':f['nativeSize'],'mode':Image.open(R/f['path']).mode,'alphaExtrema':list(Image.open(R/f['path']).getchannel('A').getextrema())} for f in frames if f],'artAcceptance':False,'formal1024ExportCount':0})
print(json.dumps({'selected':len([x for x in frames if x]),'cycleMs':sum(dur),'frames':[f['path'] if f else None for f in frames]},ensure_ascii=False))

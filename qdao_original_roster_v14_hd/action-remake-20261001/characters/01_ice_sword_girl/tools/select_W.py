from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
vs=[2,2,1,2,1,2,2,2,2,2,1,1,1,2,2,1]
actual=[
('weight','air','前近左靴接近全掌，远右靴后折离地。近左肩接符袖，远右剑手从后腰露出。'),
('weight','air','近左平底支撑，较01膝收回；二版符手从前伸收至胸腰前，剑手由后腰向前回收。'),
('weight','air','近左屈膝支撑姿态；实图鞋底约1160，较候选1182高约22原生像素，整体承重高度仍需播放复核。'),
('push_off','air','二版支撑近左腿后移，后跟抬起、前掌低位；远右腿向前屈膝通过，替换了首版前脚未后移姿态。'),
('push_off','air','后侧支撑靴前掌低位，另一靴前摆离地，脚尖沿西向；接触为视觉候选。'),
('air','air','双脚短暂离地；二版近左符手回到胸前中间位，远右剑手开始后收，接05→07。'),
('air','contact','前方远右靴已低位接触；按实图记作初触候选，不沿用原计划的落地准备。近左符袖连接已修。'),
('air','weight','前右靴平掌承重，鞋底比候选平面低约20原生像素；头冠较相邻帧偏高，已保留真实高度，不作整图贴地。'),
('air','weight','远右靴平掌承重、膝弯曲，近左后靴回收。局部肩链修复后近左符、远右剑明确。'),
('air','push_off','远右靴已移至后方，前掌低位、跟抬，近左腿前收。按实际阶段记录，不冒称仍为压缩。'),
('air','push_off','后右前掌支撑候选，近左腿前摆，剑后收、符前摆。'),
('air','push_off','后右跟抬高，近左靴向前伸，脚掌轴向仍朝西；衣袖小幅摆动。'),
('air','push_off','后右前掌最后低位，前左靴抬趾，未用最低alpha对齐。'),
('air','air','二版减小前踢：近左膝回收、前靴最低约1140，远右靴折后；双脚离地。'),
('air','air','二版前左靴收至膝下，平底约1160，继续下降；未将整体下移。'),
('contact','air','近左全掌已到约1182，按实图为接触候选，接回01继续承重；不再标成悬空准备。')
]
frames=[]
for i,(v,(left,right,note)) in enumerate(zip(vs,actual),1):
 p=R/f'drafts/run/W/{i:02}-v{v}.png';record=p.with_name(p.name+'.generation.json')
 frames.append({'frame':i,'path':p.relative_to(R).as_posix(),'sourcePath':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(Image.open(p).size),'generationRecord':record.relative_to(R).as_posix(),'durationMs':75,'actualContact':{'left':left,'right':right,'confidence':'manual_visual_candidate_not_engine_contact','evidence':note},'notes':note,'staticInspected':True,'dynamicArtAccepted':False,'actualModel':None,'actualQuality':None})
s={'schemaVersion':1,'characterId':R.name,'action':'run','direction':'W','createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'root':{'point':[512,1182/1254*1024],'status':'provisional_visual_reference_only','registrationApplied':False},'timing':{'uniformCycleMs':1200,'frameDurationsMs':[75]*16,'phaseWeights':False},'artStatus':'static_inspected_sequence_review_pending','staticInspectionScope':'all16 native outputs plus full-canvas128/256 contact sheets; repaired arm connections, late stance and descending legs','dynamicArtAccepted':False,'clientIntegrated':False,'clientRuntimeVerified':False,'frames':frames}
(R/'review/run-W-selection.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Selected W16 with per-frame actual observations')

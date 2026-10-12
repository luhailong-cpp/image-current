from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
b=Path(__file__).resolve().parents[1]
p=b/'audit/cast-selection.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['frames']=[f for f in d['frames'] if f['direction']=='E']
mapping={i:f'cast-W-{i:02d}-v1' for i in range(1,17)}
mapping.update({3:'cast-W-04-v1',4:'cast-W-03-v1',5:'cast-W-05-v2',7:'cast-W-08-v1',8:'cast-W-07-v1',10:'cast-W-10-v3'})
notes={1:'左空手腰前掌心向上起手，右远手持扇。',2:'低位结诀，扇稍外展。',3:'原 W04 比原 W03 扇位低，依实际聚势重选为03，来源名不改。',4:'原 W03 抬扇更高，依实际聚势重选为04，来源名不改。',5:'v1有朝镜头转脸及站位变宽，v2用原W03定点编辑，仅双臂聚势，双靴与相机保持。',6:'扇升至头侧，左诀近脸下。',7:'原 W08 为肩侧蓄势，较原W07手更靠后，重选为07。',8:'原 W07 高扇、左诀前推，重选为08，衔接释放。',9:'左近手诀前送，右远手扇导引。',10:'只用v3；已修复前景空左臂、后景右手持扇关系。',11:'左诀缩回半臂，右扇贴近胸。',12:'左手诀收胸前，双脚保持。',13:'同W12靴位相机，左诀到胸下松开。',14:'左手松掌降腹前，右远手扇守势。',15:'左手降腰侧、肘略屈，衣袖下降。',16:'左手自然垂落，肘进一步伸直，袖摆收落，独立区别于15。'}
for i,key in mapping.items():
 src=b/'sources/new'/f'{key}.png'
 d['frames'].append({'action':'cast','direction':'W','frame':i,'source':src.relative_to(b).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'accepted':True,'nativeSingleFrame':True,'generationRecord':f'provenance/generation/{key}.json','review':{'reviewer':'continue_cast','reviewedAt':datetime.now(timezone.utc).isoformat(),'notes':[notes[i],'已实际逐图目检，静态候选；完整动态与透明边缘仍待汇总复核。']},'event':{9:'cast_release_begin',10:'cast_release_peak'}.get(i)})
d['status']='E_W_static_candidates_complete_dynamic_pending'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
r={'character':d['character'],'action':'cast','status':'32_static_candidates_complete_dynamic_pending','frameMs':45,'reviewedAt':datetime.now(timezone.utc).isoformat(),'selection':'audit/cast-selection.json','reselection':{'W03':'cast-W-04-v1','W04':'cast-W-03-v1','W07':'cast-W-08-v1','W08':'cast-W-07-v1'},'rejected':{'cast-W-05-v1':'脸转向及站位宽度跳变；由v2替换','cast-W-10-v1':'左右手归属错误','cast-W-10-v2':'左右手归属错误','cast-E-13-v1':'脸转向及站位跳变；由v2替换'},'observations':['W两手归属全组复核：近左空手结诀，远右持扇；全部独立绘制，非E镜像。','W收势13-16按W12锁下身制作，实际手诀松开、降腹、降腰、垂侧分开可辨。','E沿用既有选择与原审核，未在本轮改写为动态通过。','W相邻衣摆与扇角仍须正常/慢速预览检查；静态齐帧不是完整动画通过。']}
(b/'audit/cast-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('cast selected',len(d['frames']))


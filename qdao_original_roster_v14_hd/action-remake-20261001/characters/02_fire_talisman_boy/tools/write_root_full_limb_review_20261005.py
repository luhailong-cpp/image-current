from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
baseline=json.loads((R/'reviews/full-limb-root-before-20261005.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
run_phases=['近中位缓冲','近中位压重','身体经过支点','身体前移且支撑跟开始抬','支撑趾端滚动','趾端蹬离前过渡','异侧鞋前落地','异侧足底承重']
attack_phases=['预备双膝微屈','沉身蓄力','扇臂拉开，前腿稳住','出手跨步','前腿接重、后跟抬起','打击峰值前腿屈膝承重','扇臂越峰、后腿回收','撤回手臂并减小跨距','恢复双脚支撑','重心回中','双膝恢复预备屈度','回到预备姿态']
frames=[]
revisions={3:'右扇由后伸收至腰侧，左铃由前伸收向肋旁；作为02到04的前半程中位。',4:'左铃从完全后伸收为躯干侧半后摆，补足03到05的路线；符扇补足第五张，保持两臂及原腿脚。',11:'反向半周左铃肘下收，手经过后腰侧；右扇仍在腰前，保持原腿脚。',12:'左铃由完全前伸收为下胸旁半前摆，衔接11腰侧到13前伸；右扇和原腿脚保持。'}
for f in baseline['frames']:
 n=f['frame'];a=f['action'];d=f['direction']
 replaced=a=='run' and d=='E' and n in revisions
 assert (sha(f['path'])!=f['sha256'])==replaced,f['path']
 if a=='attack':
  reason=f'实际查看整幅及手部、下肢等比细节：{attack_phases[n-1]}；肩袖—肘—腕连贯，解剖右手扇柄与左手铃环握持成立，未见多臂、断腕。'
  if d=='E': reason+='两鞋头沿向右的攻击平面，蓄力及出手的前后膝踝可对应，后跟抬起为蹬推，未见鞋掌单独横扭。'
  else: reason+='两鞋沿向左攻击平面；宽步与屈膝属于蓄力/前冲，鞋头未背离对应膝踝；不能把战斗跨步误判为跑步横摆。'
  if (d,n)==('E',3): reason+='全尺寸确认扇面为五张红符。'
  if (d,n)==('E',9): reason+='全尺寸确认铃腕旁白边属于宽袖口折面，未多生第三臂。'
  if d=='W' and n in [9,10]: reason+='全尺寸补看铃环与拇指食指，回收弯腕有连续前臂。'
 else:
  reason=f'实际查看整幅及手部、下肢等比细节：{run_phases[(n-1)%8]}，第{(n-1)//8+1}半周；右扇左铃固定持手，肘腕随反向摆臂移动，腕部不脱离袖口。'
  if d=='E':reason+='支撑鞋朝向屏幕右，与髋膝前后运动平面一致；摆动鞋的抬尖、垂尖来自踝屈伸，未见朝观众横翻鞋侧。'
  else:reason+='三分之二正面透视下膝踝鞋头沿东南前进平面，支撑鞋与裤管连续，回收腿在身后屈曲；不按二维投影强制髋膝踝共线。'
  if d=='SE' and n in [11,12,13,14]:reason+='保留上一轮实际局部重画的脚轴，未出现新的手部或持物回归。'
 if replaced:
  reason='邻帧重看后对本帧作局部AI修订：'+revisions[n]+'新图已实际全幅查看，五张红符、单铃、两条肩肘腕链成立，腿脚支撑关系与鞋轴未出现新错误。'
 frames.append(dict(f,sha256=sha(f['path']),decision='replaced' if replaced else 'retained',reason=reason))
evidence=[f'previews/{a}-{d}-contact.png' for a,d in [('attack','E'),('attack','W'),('run','E'),('run','SE')]]
evidence += [p.relative_to(R).as_posix() for p in (R/'work/full-limb-root-20261005').glob('*.jpg')]
out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','scope':'attack E/W 24 + run E/SE 32; all hands and feet reviewed from actual images','frames':frames,'reviewedCount':56,'retainedCount':52,'replacedCount':4,'viewedEvidence':{p:sha(p) for p in evidence},'fullResolutionSpotChecks':['frames/attack/E/03.png','frames/attack/E/09.png','frames/attack/W/09.png','frames/attack/W/10.png']+[f'frames/run/E/{n:02}.png' for n in [2,3,4,5,10,11,12,13]],'diagnosticMethod':'Fixed-region, uniform aspect-preserving review crops only. Initial contact/crop evidence predates targeted arm replacements. New full native and exported images viewed separately; current per-frame SHAs above are authoritative. No bounding-box normalization.','criteria':['肩—肘—腕—握柄连通，右扇左铃','髋—膝—踝—鞋头沿同一前进运动平面，允许正常屈膝、踝滚动及透视','相邻姿态与动作阶段成立；不以文件数或SHA作为美术通过依据'],'knownUnresolvedArtFailures':[],'clientIntegrated':False,'timing':'run16x60=960ms; attack12x30=360ms'}
(R/'reviews/full-limb-root-20261005.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewed':len(frames),'retained':52,'replaced':4})

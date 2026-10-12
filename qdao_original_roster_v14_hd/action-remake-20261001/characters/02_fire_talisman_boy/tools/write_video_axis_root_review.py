from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
frames=[]
for d in ['E','SE']:
 for n in range(1,17):
  p=f'frames/run/{d}/{n:02}.png'
  changed=d=='SE' and n in [11,12,13,14]
  if d=='E':
   if n in [1,2,9,10]:reason='侧视收腿期：跟腱—踝—鞋保持向东屈伸平面，脚尖随屈膝下垂，未见横向外扭。'
   elif n in [3,4,5,6,11,12,13,14]:reason='侧视前摆/后蹬期：前鞋鞋尖向东、后鞋踝位中立；鞋底角变化属于屈伸，未出现朝向侧翻跳变。'
   else:reason='侧视接触/后屈期：支撑脚向东，抬脚屈向后方；膝踝鞋轴连续，保持原图。'
  elif changed:
   reason='重画抬起的解剖右小腿/踝/鞋：纠正鞋尖向画面左下外撇，使前掌沿东南运动平面朝前下方，支撑左脚及上身持物保持；已对照09–16相邻完整画布复核。'
  elif n in [7,8,9,10]:reason='支撑左脚向东南，右腿向后屈，鞋尖随踝收向下方，未把正常屈膝和透视当侧扭；与新11顺接。'
  elif n in [15,16,1,2]:reason='右脚支撑/左脚前摆：两条腿各循东南平面，保留足背/底面随前摆变化，未见额外外展朝向跳变。'
  else:reason='左脚前摆至右脚后蹬：膝踝连接自然、鞋尖前向与身体一致，保留已有接地位置段。'
  frames.append({'action':'run','direction':d,'frame':n,'path':p,'sha256':sha(p),'decision':'replaced' if changed else 'retained','reason':reason})
doc={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','directions':['E','SE'],'referenceEvidence':'reviews/video-reference-sampling-20261004.json','reviewedImages':['previews/run-E-contact.png','previews/run-SE-contact.png','previews/run-SE-video-axis-detail.png'],'detailViewed':['E02','E06','E10','E14','SE09','SE10','SE11','SE12','SE13','SE14'],'scope':'实际查看全序列联系表、关键原始1024PNG、每个新1254PNG和09–16新帧联系表；视频64连续抽样仅约束整体动作方向。客户端未接入。','timing':{'frameMs':75,'cycleMs':1200,'support':'同一脚四位置各两帧连续8帧；保持原相位'},'frames':frames,'knownUnresolvedArtFailures':[]}
(R/'reviews/video-axis-E-SE-20261004.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewed':len(frames),'replaced':sum(f['decision']=='replaced' for f in frames)})


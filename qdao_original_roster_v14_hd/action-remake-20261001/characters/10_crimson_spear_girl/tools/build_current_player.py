from pathlib import Path
import json,copy,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
is_final=(R/'delivery-current.json').exists()
data=json.loads((R/('delivery-current.json' if is_final else 'candidate-inventory.json')).read_text(encoding='utf-8'))
data['orders']={} if is_final else json.loads((R/'run-playback-proposals.json').read_text(encoding='utf-8-sig')).get('groups',{})
data.update(runFrameMs=60,runCycleMs=960,phaseWeightsApplied=False)
runreg=json.loads((R/'candidate/registration.json').read_text(encoding='utf-8-sig'))
battlereg=json.loads((R/'candidate/battle-registration.json').read_text(encoding='utf-8-sig'))
for group,frames in data['groups'].items():
 for f in frames:
  if is_final:
   f['candidateUrl']=f['url']+'?v='+f['sha256'][:12]
   continue
  p=R/'candidate'/group/f"{f['frame']:02}.png"
  meta=Path(str(p)+'.generation.json')
  action,direction=group.split('/')
  reg=runreg['directions'].get(direction) if action=='run' else battlereg['groups'].get(group)
  cm=json.loads(meta.read_text(encoding='utf-8')) if meta.exists() else {}
  fresh=p.exists() and any(x.get('sha256')==f['sha256'] for x in cm.get('derivedFrom',[])) and cm.get('operation',{}).get('translation')==reg['translation'] if reg else False
  if reg and not fresh:
   source=R/f['url'][3:]
   im=Image.open(source);im.load()
   if im.size!=(1254,1254) or im.mode!='RGBA':raise ValueError('Unexpected native '+str(source))
   actual=hashlib.sha256(source.read_bytes()).hexdigest()
   if actual!=f['sha256']:raise ValueError('Source changed during preview build '+str(source))
   canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),tuple(reg['translation']))
   p.parent.mkdir(parents=True,exist_ok=True);canvas.save(p)
   cm={'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':1024,'height':1024,'mode':'RGBA','status':'candidate-export-not-visually-approved','derivedFrom':[{'file':source.relative_to(R).as_posix(),'sha256':actual,'generationRecord':str(source.relative_to(R))+'.generation.json'}],'operation':{'type':'uniform-whole-canvas-resample-and-group-fixed-translation','scale':860/1254,'translation':reg['translation'],'rootTarget':[512,942],'basis':reg['basis'],'perFrameLowestFootAlignment':False,'perFrameBBoxScaling':False},'visualAcceptance':False,'dynamicAcceptance':False}
   meta.write_text(json.dumps(cm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   fresh=True
  if not fresh:raise ValueError('Cannot mix unregistered native into registered sequence: '+group)
  f['candidateUrl']='../'+p.relative_to(R).as_posix()+'?v='+cm['sha256'][:12]
template=(R/'tools/uniform-player.html').read_text(encoding='utf-8')
if is_final:
 status='全动作手脚复查中。' if (R/'full-limb-review-20261004/SCOPE.md').exists() and not (R/'full-limb-review-20261004/completion.json').exists() else '本轮全动作手脚复查已完成。'
 template=template.replace('正在参照已确认的弓足少女逐向修正，图片仍在复查。','跑步16×60ms；每个连续支撑位置两张独立姿态，沿运动方向逐点递进。'+status+'客户端尚未接入。')
for name,only in [('index.html',False),('timing-grounding.html',True)]:
 (R/'preview'/name).write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__RUN_ONLY__',str(only).lower()),encoding='utf-8')
(R/'preview/timing-review-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
timing={'run':{'frameMs':60,'cycleMs':960,'frameCount':16,'phaseWeightsApplied':False,'timingStatus':'user_requested_offline_default','incompleteSequencePolicy':'block complete playback; preserve16 time slots for stepping','extraLoopPauseMs':0},'hit':{'frameMs':40,'cycleMs':240},'attack':{'frameMs':30,'cycleMs':360,'contactFrame':6},'cast':{'frameMs':45,'cycleMs':720,'releaseFrame':9},'clientIntegrated':False,'clientRuntimeTested':False}
(R/'animation-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'runCycleMs':960,'runFrameMs':60,'oldSpeedOptions':False,'incompleteRunGroups':[k for k,v in data['groups'].items() if k.startswith('run/') and len(v)!=16]}))

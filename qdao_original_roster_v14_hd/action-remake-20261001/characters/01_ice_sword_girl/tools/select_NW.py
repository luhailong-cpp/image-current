from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
spec=json.loads((R/'review/NW-selection-input.json').read_text(encoding='utf-8'))
frames=[]
for i,(name,note) in enumerate(zip(spec['sourceList'],spec['notes']),1):
 p=R/f'drafts/run/NW/{name}.png'; im=Image.open(p)
 foot='left' if i<=8 else 'right'
 frames.append({'frame':i,'path':p.relative_to(R).as_posix(),'sourcePath':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'generationRecord':p.relative_to(R).as_posix()+'.generation.json','durationMs':75,'actualContact':{'left':'weight' if foot=='left' else 'air','right':'weight' if foot=='right' else 'air','confidence':'manual_visual_observation_not_engine_contact','evidence':note},'spatialPosition':['forward_landing','body_approaches_support','body_passes_support','rear_forefoot_push_off'][((i-1)%8)//2],'notes':note,'staticInspected':True,'dynamicArtAccepted':False,'actualModel':None,'actualQuality':None})
s={'schemaVersion':1,'characterId':R.name,'action':'run','direction':'NW','createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'timing':{'uniformCycleMs':1200,'frameDurationsMs':[75]*16,'phaseWeights':False},'artStatus':'paired_support_selected_pending_sequence_review','eightConsecutiveSupportVerified':False,'positionPairsVerified':False,'dynamicArtAccepted':False,'remainingIssues':['连续播放检查8→9/16→1换脚与上半身漂移','四组支撑位置逐步后移幅度需联合视查'],'clientIntegrated':False,'clientRuntimeVerified':False,'frames':frames}
(R/'review/run-NW-selection.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NW selected16')


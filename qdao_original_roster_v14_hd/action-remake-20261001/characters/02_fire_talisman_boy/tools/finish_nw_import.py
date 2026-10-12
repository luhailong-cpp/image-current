import json,shutil,hashlib,argparse,datetime
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('--direction');p.add_argument('--frame',type=int);a=p.parse_args()
req=json.loads((R/'records'/f'{a.key}.request.json').read_text(encoding='utf-8-sig'))
_,d,f=req['slot'].split('/');d=a.direction or d;f=a.frame or int(f)
src=R/'work/grounding-v2/north'/d/f'{a.key}.png'
rec=json.loads(src.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
dst=R/f'frames/run/{d}/{int(f):02}.png';old=json.loads(dst.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
rec['replaces']={'sha256':sha(dst),'generationRecord':old.get('generationRecord')}
rec['status']='exported_candidate_pending_sequence_review';rec['registeredAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
native=rec['native'];native['file']=Path(native['file']).relative_to(R).as_posix()
rec['export']={'file':str(dst.relative_to(R)).replace('\\','/'),'sha256':sha(src),'size':[1024,1024],'mode':'RGBA','operation':'uniform full-canvas downsample of native; no mirror, crop, warp or per-frame grounding','derivedFrom':native}
rec['file']=rec['export']['file'];rec['prompt']=f'prompts/{a.key}.txt'
recpath=R/'records'/f'{a.key}.json';recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(src,dst)
side={'file':rec['export']['file'],'sha256':sha(dst),'generationRecord':recpath.relative_to(R).as_posix(),'derivedFrom':native,'operation':rec['export']['operation'],'actualModel':None,'actualQuality':None}
dst.with_suffix('.png.generation.json').write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding='utf-8')
ip=R/'inventory-run-nw-finish.json';iv=json.loads(ip.read_text(encoding='utf-8-sig')) if ip.exists() else {'character':'02_fire_talisman_boy','action':'run','direction':'NW','target_frames':16,'frame_duration_ms':75,'duration_ms':1200,'frames':[]}
iv['frames']=[x for x in iv['frames'] if not(x['direction']==d and x['frame']==int(f))]
iv['frames'].append({'action':'run','direction':d,'frame':int(f),'path':side['file'],'sha256':sha(dst),'native_size':[native['width'],native['height']],'native_evidence':side['generationRecord'],'visual_status':'same_foot_eight_frame_grounding_sequence_review_pending'})
iv['frames'].sort(key=lambda x:(x['direction'],x['frame']));ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'slot':f'run/{d}/{int(f):02}','sha256':sha(dst)}))

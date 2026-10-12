import json,shutil,hashlib,argparse,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('note');a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads((R/'records'/f'{a.key}.request.json').read_text(encoding='utf-8'))
action,d,f=req['slot'].split('/');f=int(f)
assert action=='cast' and d in ['E','W']
src=R/'work/grounding-v2/north'/d/f'{a.key}.png'
rec=json.loads(src.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
dst=R/f'frames/{action}/{d}/{f:02}.png'
ip=R/'inventory-cast.json';iv=json.loads(ip.read_text(encoding='utf-8'))
e=next(x for x in iv['frames'] if x['direction']==d and x['frame']==f)
assert e['sha256']==sha(dst)
rec['replaces']={'sha256':sha(dst),'generationRecord':e.get('source_record')}
rec['visualQA']={'status':'single_frame_full_limb_pass_pending_sequence','notes':a.note}
native=rec['native'];native['file']=Path(native['file']).relative_to(R).as_posix()
rec['export']={'file':dst.relative_to(R).as_posix(),'sha256':sha(src),'size':[1024,1024],'mode':'RGBA','operation':'uniform full-canvas downsample; no mirror/crop/warp/grounding shift','derivedFrom':native}
rec['file']=rec['export']['file'];rec['prompt']=f'prompts/{a.key}.txt';rec['status']='full_limb_revision_imported'
rp=R/'records'/f'{a.key}.json';rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(src,dst)
side={'file':rec['file'],'sha256':sha(dst),'generationRecord':rp.relative_to(R).as_posix(),'derivedFrom':native,'operation':rec['export']['operation'],'actualModel':None,'actualQuality':None}
dst.with_suffix('.png.generation.json').write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding='utf-8')
e.update({'sha256':sha(dst),'native_size':[native['width'],native['height']],'native_evidence':rp.relative_to(R).as_posix(),'source_record':rp.relative_to(R).as_posix(),'visual_status':'full_limb_single_frame_pass_pending_sequence','sequence_review':'reviews/full-limb-cast-NE-NW-20261004.json'})
iv['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'slot':req['slot'],'sha256':sha(dst)}))

import json,shutil,hashlib,argparse,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('note');a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads((R/'records'/f'{a.key}.request.json').read_text(encoding='utf-8'))
_,d,f=req['slot'].split('/');f=int(f)
src=R/'work/grounding-v2/north'/d/f'{a.key}.png';rec=json.loads(src.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
dst=R/f'frames/run/{d}/{f:02}.png';old=json.loads(dst.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
rec['replaces']={'sha256':sha(dst),'generationRecord':old.get('generationRecord')};rec['visualQA']={'status':'single_frame_axis_pass_pending_sequence','notes':a.note}
native=rec['native'];native['file']=Path(native['file']).relative_to(R).as_posix()
rec['export']={'file':dst.relative_to(R).as_posix(),'sha256':sha(src),'size':[1024,1024],'mode':'RGBA','operation':'uniform full-canvas downsample; no mirror/crop/warp/grounding shift','derivedFrom':native}
rec['file']=rec['export']['file'];rec['prompt']=f'prompts/{a.key}.txt';rec['status']='axis_revision_imported'
rp=R/'records'/f'{a.key}.json';rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');shutil.copy2(src,dst)
side={'file':rec['file'],'sha256':sha(dst),'generationRecord':rp.relative_to(R).as_posix(),'derivedFrom':native,'operation':rec['export']['operation'],'actualModel':None,'actualQuality':None}
dst.with_suffix('.png.generation.json').write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding='utf-8')
ip=R/('inventory-run-ne-cast.json' if d=='NE' else 'inventory-run-nw-finish.json');iv=json.loads(ip.read_text(encoding='utf-8'))
e=next(x for x in iv['frames'] if x['direction']==d and x['frame']==f);e.update({'sha256':sha(dst),'native_size':[native['width'],native['height']],'native_evidence':rp.relative_to(R).as_posix(),'source_record':rp.relative_to(R).as_posix(),'visual_status':'video_axis_single_frame_pass_pending_sequence','sequence_review':'reviews/video-axis-NE-NW-20261004.json'})
iv['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();iv['qa_summary']={'completeSequencePassed':False,'dynamicStatus':'new_video_axis_feedback_pending_sequence_review','review':'reviews/video-axis-NE-NW-20261004.json','clientStatus':'not_integrated'}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'slot':req['slot'],'sha256':sha(dst)}))

from pathlib import Path
import json, hashlib, argparse
from datetime import datetime, timezone
b=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('keys',nargs='+');a=p.parse_args()
dst=b/'audit/run-NS-selection.json'
data=json.loads(dst.read_text(encoding='utf-8-sig')) if dst.exists() else {'character':'15_water_dragon_scholar_boy','frameMs':30,'status':'static_candidates_partial_dynamic_pending','frames':[]}
for key in a.keys:
 _,direction,num,version=key.split('-')
 frame=int(num);src=b/'sources/new'/f'{key}.png'
 record=b/'provenance/generation'/f'{key}.json'
 if not src.exists() or not record.exists():raise ValueError('source or record missing '+key)
 data['frames']=[f for f in data['frames'] if not (f['direction']==direction and f['frame']==frame)]
 data['frames'].append({'action':'run','direction':direction,'frame':frame,'source':src.relative_to(b).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'accepted':True,'nativeSingleFrame':True,'generationRecord':record.relative_to(b).as_posix(),'review':{'reviewer':'continue_cast','reviewedAt':datetime.now(timezone.utc).isoformat(),'notes':['实际图已目检：方向、右扇左空手与双腿可辨。阶段姿态与实际落地/腾空由逐帧联合复核；单图选择不等于动态通过。','固定画布根锚点，不按脚底或包围盒单独平移缩放。']},'event':{1:'left_touchdown',4:'left_toe_off',6:'first_flight_apex',9:'right_touchdown',12:'right_toe_off',14:'second_flight_apex'}.get(frame)})
data['frames'].sort(key=lambda f:(f['direction'],f['frame']))
data['status']='static_candidates_complete_dynamic_pending' if len(data['frames'])==32 else 'static_candidates_partial_dynamic_pending'
dst.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Selected NS:',len(data['frames']))


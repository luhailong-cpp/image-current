import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
old=json.loads((R/'inventory-run-north.json').read_text(encoding='utf-8-sig'))
ip=R/'inventory-run-nw-finish.json'
if ip.exists():raise RuntimeError('NW inventory already initialized')
frames=[e for e in old['frames'] if e['direction']=='NW' and e['frame'] in (9,10,11)]
assert len(frames)==3
iv={'character':'02_fire_talisman_boy','action':'run','direction':'NW','target_frames':16,'frame_duration_ms':75,'duration_ms':1200,'frames':frames,'ownership':'NW exclusively delegated by root; supersedes older NW rows in north inventory after all slots exported','client_status':'not_integrated'}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NW retained 09/10/11 initialized')

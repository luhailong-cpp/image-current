from pathlib import Path
import json,hashlib
from inventory_sources import current_slots
ROOT=Path(__file__).resolve().parents[1]
frames=[dict(f, inventory_source=name) for name,f in current_slots(ROOT)]
slots=[(x["action"],x["direction"],x["frame"]) for x in frames]
if len(slots)!=len(set(slots)):raise ValueError("duplicate frame slots")
review_path=ROOT/'reviews/final-review.json'
review=json.loads(review_path.read_text(encoding='utf-8-sig')) if review_path.exists() else {}
reviewed={x['path']:x['sha256'] for x in review.get('frames',[])}
for f in frames:
    current=hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()
    if reviewed.get(f['path'])==current:
        f['visual_status']='offline_directional_review_complete_client_pending'
        f['final_review']='reviews/final-review.json'
    elif f['action']=='run':
        f['visual_status']='two_frame_position_grounding_revision_pending'
        f.pop('final_review',None)
complete=len(frames)==196 and all(reviewed.get(f['path'])==hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() for f in frames) and not review.get('knownUnresolvedArtFailures',['pending'])
manifest={"character":"02_fire_talisman_boy","root_anchor":[512,920],"anchor_status":"target coordinates; full sequence visual verification pending","target_frames":196,"timing":{"run":{"frameMs":60,"cycleMs":960,"uniform":True,"clientConfirmed":False},"hit":{"frameMs":40,"cycleMs":240},"attack":{"frameMs":30,"cycleMs":360},"cast":{"frameMs":45,"cycleMs":720}},"frames":sorted(frames,key=lambda x:(x["action"],x["direction"],x["frame"]))}
(ROOT/"inventory.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
manifest['offline_materials_complete']=complete
manifest['client_integrated']=False
manifest['anchor_status']='unified design reference; client ground and movement calibration pending'
(ROOT/'inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'exported_frames':len(frames),'target':196,'offline_materials_complete':complete,'client_integrated':False}))


from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def save(p,o):(R/p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
feedback={'text':'应该是要着中间地四帧，旁边地各两帧','recordedAt':datetime.now(timezone.utc).isoformat(),'status':'awaiting_clarification_of_per_foot_or_whole_cycle_scope','interpretationConstraint':'Center and adjacent positions are spatial, not heel/full-sole/toe phases. Must show distinct actual poses, no duplicates or label-only compliance.','timing':'16x75ms=1200ms','question':'Per foot forward2-center4-rear2, alternating two feet across16, or8 contact frames total for entire cycle?'}
save('audit/spatial-contact-requirement.json',feedback)
review=load('review.json')
for slot,row in review.items():
 if slot.startswith('run/'):
  row['visualStatus']='pending_spatial_2_4_2_contact_review'
  row['latestUserRequirement']='audit/spatial-contact-requirement.json'
save('review.json',review)
final=load('audit/final-visual-review.json')
final['status']='reopened_spatial_2_4_2_contact_requirement'
final['latestUserRequirement']=feedback
save('audit/final-visual-review.json',final)
for slot in ['run-N-06-root-v7','run-N-10-root-v7','run-E-03-contact-v1','run-E-11-contact-v1','run-N-06-root-v8']:
 p='run/staging/'+slot+'.png.generation.json'
 m=load(p);m['review']={'status':'rejected','reason':'Wrong non-target pose/composition or head/hand position; see audit/root-N-v7-rejection.json, root-v8-recovery.json, contact-E-rejected-v1.json'}
 save(p,m)
p='run/staging/run-N-10-root-v8.png.generation.json'
m=load(p)
m['evidence']['mappingVerification']='inferred_from_timestamp_visual_content_and_remaining_host_image_after_reset'
m['evidence']['exactOutputHintRecovered']=False
m['evidence']['returnedFields']=[]
m['review']={'status':'superseded_by_v9','reason':'Unwanted crystal haze removed in v9'}
save(p,m)
frames=[16,1,2,3,8,9,10,11]
sheet=Image.new('RGB',(4*300,2*340),(224,230,227));draw=ImageDraw.Draw(sheet)
for k,n in enumerate(frames):
 im=Image.open(R/'run/E'/f'{n:02d}.png').convert('RGBA')
 # Evidence crop only; never used as a game frame.
 detail=im.crop((140,630,840,1024));detail.thumbnail((300,300))
 x=(k%4)*300;y=(k//4)*340
 sheet.paste(detail,(x,y),detail);draw.text((x+8,y+306),f'E {n:02d} current actual stance',fill=(25,45,35))
sheet.save(R/'run/staging/contact-E-current-detail.jpg',quality=94)
print(json.dumps({'runStatus':'pending_spatial_2_4_2_contact_review','requirement':feedback['text']},ensure_ascii=False))

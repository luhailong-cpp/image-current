from pathlib import Path
import json
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
base=json.loads((R/'provenance/hit/E/01.request.json').read_text())
stages={3:'Maximum recoil: torso leans backward about 10 degrees, head tilts back modestly, knees flex further without moving the feet. Both elbows bend to protect the body and stabilize their held objects. Hair and sleeve ribbons lag forward. No falling.',4:'Rebound midstage: torso recovers to only 6 degrees backward lean, head and shoulders begin returning toward upright, knees still softly bent. Hands stabilize their unchanged objects. Three jade chimes show slight inertial swing; no glowing magic.',5:'Almost recovered: torso near upright with only 2 degrees lean, knees begin extending, left mallet and right chime return toward the original ready positions. Hair and tassel residual sway becoming small. Feet unchanged.',6:'Final recovery: upright in-place ready posture, natural knees and relaxed attentive expression; anatomical right hand chimes and left hand mallet return to their ready positions. Subtle small residual ribbon sway, no effects. Distinct settling pose. Crucially keep the preceding frame body facing, proportions and two foot contact locations.'}
for d in ['E','W']:
 for n in range(3,7):
  stem=R/f'provenance/hit/{d}/{n:02d}'
  if stem.with_suffix('.request.json').exists():continue
  view='Southeast three-quarter FRONT facing lower-right, right chime on screen-left, left mallet screen-right.' if d=='E' else 'Northwest TRUE three-quarter BACK facing upper-left. Back of head, hair knot, back robe, heels visible. Left mallet on screen-left, right chime on screen-right. No frontal chest/full face.'
  p=base['prompt'];start=p.index('Frame hit/E/01');end=p.index('Clean bright')
  p=p[:start]+f'Frame hit/{d}/{n:02d}, 40ms. '+view+' '+stages[n]+' Anatomical hands never change. Both foot contact positions EXACTLY preserved from previous frame. No stepping, no full body rotation.\n'+p[end:]
  p+='\nInput image 4 is the preceding frame: preserve its camera, size, anatomical side, foot positions and costume. Advance only the small next pose step described.'
  args={'prompt':p,'referenced_image_paths':base['referenced_image_paths']+[str(R/f'provenance/hit/{d}/_inprogress/{n-1:02d}.png')],'transparent_background':True,'model':None,'quality':None,'submittedAt':None}
  stem.with_suffix('.prompt.txt').write_text(p,encoding='utf-8')
  stem.with_suffix('.request.json').write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding='utf-8')
print('Missing hit requests prepared')

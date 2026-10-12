"""Prepare missing root frames as edits of authoritative idle, with same-view contact anchor."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[3]
for direction in ['SE','S']:
 for frame in range(1,16):
  if (ROOT/f'runtime/run/{direction}/{frame:02d}.png').exists():continue
  stem=f'run_{direction}_{frame:02d}_v2'
  old=(ROOT/'prompts'/f'run_{direction}_{frame:02d}_v1.txt').read_text(encoding='utf-8')
  phase=old.split('Pose: ')[1].split('\nKeep character')[0]
  camera=old.split('Camera: ')[1].split('\nPose:')[0]
  refs=[{'path':str(REPO/f'qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/{direction}.png'),'role':'EDIT TARGET, exact fixed camera scale, proportions'}, {'path':str(REPO/'q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png'),'role':'identity detail only'}, {'path':str(REPO/'designs/jubaozhai-ui/02-characters.png'),'role':'approved paint finish'}, {'path':str(ROOT/f'work/run_{direction}_00_v2.png'),'role':'same-view run right-contact anchor; change limb pose, preserve scale'}]
  prompt=f'''Edit image1 into ONE {direction} RUN animation sprite, frame{frame:02d}/16. Image1 is the exact canvas/camera/proportion edit target; image2 only identity detail; image3 only paint finish; image4 same-view running contact anchor. KEEP HEAD SIZE AND CANVAS LOCATION of image1 and image4, do not enlarge character or zoom/crop. Make a distinct real anatomical pose.\nCamera: {camera}\nPose: {phase}\nKeep exact short stocky chibi proportions. The head including ponytail spans y14%-48% of canvas, top clear margin, belt near x50% y66%. Fixed virtual ground y92%, support feet on this plane, airborne feet above it. Only small vertical bob dictated by pose. RIGHT anatomical hand always gold pointed short thunder scepter, LEFT hand always rigid rectangular gold taiji plaque. Opposite arm to leading leg swings FORWARD through shoulder and elbow; other arm goes BACK, not two arms in static display. Trace each thigh from correct hip, no crossed knees, no two limbs merged. Right limbs viewer-left and left limbs viewer-right in frontal view; preserve mild SE perspective if specified. TWO hands, TWO legs, TWO boots only. Distinct thumbs and grip, no extra fist at waist. White shin wraps, black/gold boots, navy lightning baggy pants, gold/ivory embroidered robe/navy lining. Brown layered hair and little high ponytail, gold ribbons/turquoise beads. Same rich clean rounded painted identity and outfit as refs. Moderate cloth/ribbon lag. Preserve genuine transparent alpha, no floor, shadow, effects, motion trails, text, grid, extra characters. Native square at least1024. ONLY change pose, preserve all camera/scale invariants.\n'''
  (ROOT/'prompts'/f'{stem}.txt').write_text(prompt,encoding='utf-8')
  (ROOT/'records'/f'{stem}_references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8')
print('Edit specifications saved.')

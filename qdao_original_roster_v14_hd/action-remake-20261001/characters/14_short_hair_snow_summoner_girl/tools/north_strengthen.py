from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
for d in ['N','NE','NW']:
 for i in range(2,17):
  slot=f'run-{d}-{i:02d}-v1'
  p=root/'provenance'/f'{slot}.request.json'
  rec=json.loads(p.read_text())
  support='LEFT' if i<=5 else ('RIGHT' if 9<=i<=13 else None)
  if support:
   add=f"\nGround-contact constraint: this is a ONE-LEG SUPPORT pose. {support} boot visibly contacts the virtual floor at 92% canvas height; supporting knee compresses, while the OTHER boot is lifted at least 8% canvas height above that floor. At push-off only the supporting toe stays on floor. No broad airborne split during support. Near/far projection must not reverse anatomical leg. RIGHT shoulder and elbow must change as specified, not just fingers/crystal orientation."
  else:
   gap='6 to 10%' if i in [7,15] else '3 to 5%'
   add=f"\nFlight constraint: BOTH boots are airborne, their lowest points above virtual floor y92% by {gap} canvas height. Preserve body scale and raise hips with true bent-knee running flight, no star-jump. RIGHT shoulder/elbow location changes according to phase, not just wrist rotation."
  rec['submittedParameters']['prompt']+=add
  p.write_text(json.dumps(rec,indent=2),encoding='utf-8')
  (root/'prompts'/f'{slot}.txt').write_text(rec['submittedParameters']['prompt'],encoding='utf-8')
print('Updated 45 unsubmitted prompts')

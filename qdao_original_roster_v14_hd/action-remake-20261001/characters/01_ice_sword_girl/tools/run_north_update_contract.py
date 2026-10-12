from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
for d,first in [('N','right'),('NE','left')]:
 p=R/'review'/f'run-{d}-selection.json'
 j=json.loads(p.read_text(encoding='utf-8'))
 j['artStatus']='new_contact_4_positions_x2_frames_revision_in_progress'
 j['contactStructureRequirement']={'status':'not_yet_verified','source':'latest user clarification','firstSupportFoot':first,'firstSupportFrames':list(range(1,9)),'secondSupportFoot':'left' if first=='right' else 'right','secondSupportFrames':list(range(9,17)),'positions':['front_landing','body_approaches_support','body_passes_support','rear_push_off'],'framesPerPosition':2,'frameMs':75,'positionMs':150,'stanceMs':600,'cycleMs':1200,'positionMeaning':'actual support foot relative to body/pelvis; not labels for heel/fullsole/toe','requireIndependentPoses':True,'allowWholeImageTranslation':False}
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N and NE candidate selections flagged for latest contact revision')


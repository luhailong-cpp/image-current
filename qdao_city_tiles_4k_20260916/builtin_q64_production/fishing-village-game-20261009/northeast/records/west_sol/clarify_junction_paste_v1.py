from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
name='r06_c11_junction_r2_c2-v1'
rec=w.read(w.R/f'{name}.derivation-trial.json')
items=[]
for e in rec['patches']:
 p=Path(e['path']+'.derived.json');d=w.read(p);items.append(dict(patch=e['patch'],sourceSidecar=w.ref(p),field='targetPasteAt',originalRecordedValue=d['targetPasteAt'],actualPasteAt=d['targetPasteAt'][:2],targetContributionBox=d['targetContributionBox'],reason='Pillow paste expands mutable two-coordinate list into four-coordinate bounds; actual integer paste origin is first two values, proven by pixel comparison. Original metadata and dependent hash evidence remain preserved.'))
w.write(w.R/'r06_c11-junction-r2c2-v1.paste-metadata-clarification.json',dict(schemaVersion=1,items=items,imagesUnchanged=True))
print(len(w.own_selection('r06_c11')))


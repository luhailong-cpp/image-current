from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
rows=[]
for d,n,note in [('E',3,'Original high recovery knee, far stance leg and waist-level right palm preserved. Support boot sole raised by local ankle/knee edit; toe points E. Full native and current leg contact sheet plus480px browser observed.'),('E',11,'Original forward knee lift, near stance leg and hip-level right hand preserved. Support ankle extended locally with flat shoe direction E. Full native and current leg contact sheet plus480px browser observed.'),('N',10,'Right wrist/palm lowered to intermediate swing; no extra limb or crystal haze. New head width matches master scale; support right boot upper/heel and left rear sole distinct.480px browser frame10 observed; complete new spatial contact cycle not accepted.')]:
 p=R/'run'/d/f'{n:02d}.png'
 rows.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'localAnatomy':'accepted','observation':note})
record={'status':'local_repairs_reviewed_pending_full_spatial_contact_rebuild','reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root','frames':rows,'normal240Evidence':'E normal1200ms selected rendered frame01, no video/FPS measurement','latestRequirement':'audit/spatial-contact-requirement.json','clientValidated':False}
(R/'audit/root-local-repair-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))

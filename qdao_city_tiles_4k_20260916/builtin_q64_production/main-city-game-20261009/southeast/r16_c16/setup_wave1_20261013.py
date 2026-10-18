from pathlib import Path
import json
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
p=T/'local-content.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update({
'p01_01':'Existing plain warm grey stone outer parapet/tower wall extends downward from TOP native. Broad flat wall face fills x100..850; far-left is a slim lighter edge and a small diagonal coping fragment in top-left ONLY, matching guide. Near x900..1000 a deep vertical contact shadow marks the original recessed corner, with another darker stone wall face to its right. Keep the exact continuous vertical corner location, stone grout trajectories and large slab scale from TOP native. This is a giant cropped wall detail, not a whole building. No new coping below, door, window, ledge, pillar, staircase, vegetation, lantern, plaque or object; no extra horizontal molding or hard line at the 115-pixel anchor boundary.',
'p01_02':'Existing lower tower-wall corner. Leftmost roughly x0..550 is the darker return face and inset contact shadow, tapering diagonally toward x550 lower down. Right x550..1254 is the existing warm pale tower wall: broad existing pale horizontal bevel/molding at y400..550 and another at y1030..1150 visible in guide, with quiet grey-beige wall between. Continue TOP and LEFT native corner and slab-grid direction precisely. These are existing building base string courses, not a new stair/rail/object. Do not fit a full building or add a post, window, door, lantern, plaque, coins, vegetation or ornament.',
'p02_01':'Continue exact same plain large warm-grey stone outer parapet wall from TOP, filling x100..850, narrow pale side edge at far-left. Existing deep vertical corner/recessed shadow around x900..1000 continues from TOP through most of this crop. Near bottom y1050..1254 the original diagonal stone boundary/coping begins at x600 and rises toward x980,y1000 before receding to right, exactly as guide; do not prematurely introduce it higher. No new post, door, window, decoration, ledge, tree, pot, stairs or furniture. Keep calm large slabs and connected grout in current perspective.'
})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
R=T.parent/'r15_c16/review/south-local-0cd62b74724ba75d'
e=json.loads((R/'evidence.json').read_text())
e.update({'reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_south_core_geometry_passed_for_continuation','findings':'Four native384-deep south strips viewed. Stone slab boundaries and diagonal base bevel are continuous with no additional ornament, orphan structural stub or new object. Full internal/north/west QA remains delegated and pending.','externalJoinPassed':False,'formalAccepted':False})
with (R/'root-local-qa.json').open('x',encoding='utf-8') as f:json.dump(e,f,ensure_ascii=False,indent=2)

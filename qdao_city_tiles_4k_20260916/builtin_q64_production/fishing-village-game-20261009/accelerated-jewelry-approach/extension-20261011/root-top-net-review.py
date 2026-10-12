from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];q=b/'extension-20261011/geometry/north-seams'
items=[('r05_c10-north-c4-wide-native.png','Native net top rope and mesh continue across north boundary without major break.'),('r05_c11-north-c1-wide-native.png','Actionable: new wooden post extends upward into the original net across north boundary; the north original has mesh at these pixels. Repair new p11 only, keeping old north candidate fixed.'),('new-core-seams/r05-cross-tile-r1-native.png','Actionable: abrupt horizontal rectangular conditioning strip 115 pixels below new tile top. Remove hard reference-band cutoff while repairing p11 upper net.')]
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scale':'native 1:1','formalAccepted':False,'ownerNotified':'qa_first_tile','crops':[{'file':str(q/f),'sha256':hashlib.sha256((q/f).read_bytes()).hexdigest(),'finding':note} for f,note in items],'requiredAction':'Localized built-in repair of r05_c11 p11 upper portion; review net continuity and local west/north seams after repair.'}
(b/'extension-20261011/root-top-net-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

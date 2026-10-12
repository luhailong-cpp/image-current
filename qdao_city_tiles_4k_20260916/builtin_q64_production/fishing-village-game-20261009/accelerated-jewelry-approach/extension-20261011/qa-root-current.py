from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];q=b/'extension-20261011/geometry/north-seams'
checked={
'r05_c10-north-c1-wide-native.png':'Wood support and timber facade edges continuous; minor paint variation only.',
'r05_c10-north-c2-wide-native.png':'Shield rim, rack support and wood edge continuous through north boundary.',
'r05_c10-north-c3-wide-native.png':'Shield side and stone slab joints continuous through north boundary.',
'r05_c11-north-c2-wide-native.png':'Repaired blue net and timber join continue at boundary; separate hard white-cloth band on right is an interior p12/p13 defect already assigned to owner.',
'r05_c11-north-c4-wide-native.png':'Blue roof ridges and golden fascia continuous at north boundary.',
'new-core-seams/r05_c10-h-p12-p22-native.png':'Gold rope wrap and wooden post physically continuous; stone surface joins continue.',
'new-core-seams/r05_c10-v-p12-p13-native.png':'Post, net and shield silhouettes connect; soft sand texture under shield on p12 side reported to owner for final clarity review.',
'new-core-seams/r05_c10-v-p21-p22-native.png':'Stone slab outlines continuous; no core-aligned abrupt band observed.',
'new-core-seams/r05_c10-h-p11-p21-native.png':'Stone outlines continue without disconnected crack or slab edge.',
'new-core-seams/r05_c11-h-p14-p24-native.png':'Blue tile grooves, golden support and timber geometry continuous.',
'new-core-seams/r05_c11-v-p12-p13-native.png':'Actionable: vertical halo-edge cutoff of post/collar against white fabric. Assigned to r05_c11 owner for local repair; not accepted.'}
records=[{'file':str(q/f),'sha256':hashlib.sha256((q/f).read_bytes()).hexdigest(),'finding':note,'scale':'native 1:1'} for f,note in checked.items()]
out=b/'extension-20261011/root-incremental-qa.json'
out.write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'Only listed original-scale crops; not complete extension acceptance','formalAccepted':False,'crops':records,'pendingRepairs':['r05_c11 p12/p13 hard vertical splice'],'pendingQualityReview':['r05_c10 p12 soft sand beneath shield']},indent=2)+'\n',encoding='utf-8')
print(len(records))

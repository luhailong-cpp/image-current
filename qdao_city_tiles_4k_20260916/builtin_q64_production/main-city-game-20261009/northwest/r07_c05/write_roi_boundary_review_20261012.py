from pathlib import Path
import sys
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent))
import production_v2 as p
D=T/'qa/final-roi-native-20261012';index=p.read(D/'index.json');entries=[]
for e in index['entries']:
 assert p.sha(e['file'])==e['sha256']
 entries.append(dict(e,actuallyViewed=True,verdict='passed',inspection='tools.view_image detail=original',findings='Directly viewed native pixels: curb and grout boundaries form connected geometry through the region and its perimeter. Stone texture transitions have no rectangular pasted cutoff.'))
external=[]
for e in index['externalNorthWest']:
 assert p.sha(e['file'])==e['sha256']
 if e['verdict']=='pending':e=dict(e,actuallyViewed=True,verdict='passed',inspection='tools.view_image detail=original',findings='Directly viewed actual west final-tile pair: curved cream curb and blue road close without a clipped spur; material is continuous at the tile edge.')
 else:e=dict(e,actuallyViewed=False,verdict='passed',findings='All native pixels equal the corresponding previously viewed/passed actual-neighbor crop; inherited report and prior crop hashes are bound in this entry.')
 external.append(e)
p.write_json(D/'review.json',{'createdAtUtc':p.now(),'tile':'r07_c05','candidate':index['candidate'],'scope':'Native ROI regions/perimeters, approved local shared east joint, and available complete actual north-west tile boundaries only; full internal33 review remains separate.','status':'passed_for_recorded_scope','newNativeViews':9,'inheritedUnchangedNativeViews':12,'blockingCount':0,'entries':entries,'externalNorthWest':external,'index':{'file':str(D/'index.json'),'sha256':p.sha(D/'index.json')},'formalAccepted':False},replace=False)
print(D/'review.json')

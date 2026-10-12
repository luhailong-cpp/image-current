from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
selected=read(ROOT/'selection-r09_c12.json')['patchVersions']
rejects={'r09_c12_p12_v01':'Repeated neighboring crop and invented ornaments','r09_c12_p12_v02':'Added fascia and ornaments outside layout','r09_c12_p12_v03':'Visible roof tile and tonal mismatch at seam','r09_c12_p12_v04':'Persistent seam mismatch after repair; experimental minimum seam rejected','r09_c12_p12_v05':'Repair did not fix joint/brightness mismatch','r09_c12_p13_v01':'Invented large decorative scroll and floral badges','r09_c12_p43_v01':'Invented jade gongs, mounts and carvings','r09_c12_p44_v01':'Invented jade gongs absent from coordinate layout','r10_c12_p11_v01':'Invented carved stone posts; removed by v02'}
for rc,v in selected.items():
 f=ROOT/'native'/f'r09_c12_p{rc}_{v}.png.generation.json';d=read(f);d['status']='selected_current_native_for_candidate_and_neighbor_guides';d['formalAccepted']=False;write(f,d)
for name,reason in rejects.items():
 f=ROOT/'native'/f'{name}.png.generation.json';d=read(f);d['status']='rejected_superseded_native';d['rejectionReason']=reason;d['formalAccepted']=False;write(f,d)
write(ROOT/'qa'/'native-dispositions-root.json',{'updatedAt':now(),'selectedFirstTile':selected,'rejected':rejects,'formalAcceptedCount':0,'imageCleanupPending':True,'noHistoricalModelEvidenceChanged':True})
refs=read(ROOT/'references.json');plan=read(ROOT/'coordinate-plan.json')
for rel,tid in [('guides/r09_c12.tile-layout-only.png','r09_c12'),('qa/r10_c12.layout-preview.png','r10_c12')]:
 f=ROOT/rel
 if not f.exists():continue
 side=Path(str(f)+'.generation.json')
 if side.exists():continue
 tile=next(t for t in plan['tiles'] if t['id']==tid)
 write(side,{'file':str(f),'sha256':sha(f),'recordCreatedAt':now(),'dimensions':list(Image.open(f).size),'operation':'mechanical nearest-neighbor coordinate crop enlargement; layout review only, never final pixels','source':refs[0],'sourceCrop':[v*1254/57344 for v in tile['coreGlobalBox']],'usableAsFinalArt':False})
old=ROOT/'tiles'/'r09_c12.candidate.png.generation.json';d=read(old);d['status']='superseded_assembly_keep_text_record';d['replacedBy']='tiles/r09_c12.candidate-v02.png';d['replacementReason']='Move native source ownership at bottom-row p42/p43 by -115px to preserve complete cross-tile tube silhouette.';write(old,d)
print('9 rejection records and selected native statuses recorded; derived layout previews traced.')


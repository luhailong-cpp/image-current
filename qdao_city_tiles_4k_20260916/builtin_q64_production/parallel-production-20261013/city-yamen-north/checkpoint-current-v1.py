from pathlib import Path
import importlib.util,json
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
per={}
for tile in sorted(m.TILES):
    files=list((B/tile/'native').glob('*.png'))
    picked=m.selected(tile)
    per[tile]={'nativeVersions':len(files),'nativePatchPositions':len({f.name.split('-v')[0] for f in files}),'selectedCount':len(picked),'selected':picked}
data={'schemaVersion':2,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'status':'active_generation_resumed_after_user_authorized_resume','supersedes':'recovery-checkpoint-v001.json','oldNetworkDenial':'Historical; current builtin calls have succeeded. No permission/credential changes or paid route used.','perTile':per,'expectedCoreCount':64,'selectedCoreCount':sum(x['selectedCount'] for x in per.values()),'completeSourceTiles':sum(x['selectedCount']==16 for x in per.values()),'formalAcceptedCount':0,'helper':'batch_pipeline_v4.py','route':'builtin_image_gen','actualImageModel':None,'modelEvidence':'Tool returns image_url/output_hint only; actual model not returned','paidAPIUsed':False,'gitMutation':False,'activeAssignments':{'root':'r02_c04, excluding s03_04 which is delegated','audit_northwest':'r02_c04/s03_04 only, generation/QA without selection writes','production_helper':'r01_c04 remaining3 and QA; proposed next r01_c05 after east confirmation','east_column_native':'r02_c05 remaining cores/repairs'},'pending':{'r02_c04':'16 positions have native candidates; 9 selected. s01_03 deferred after two unsuccessful local repairs; s03_01 duplicate tip and seams pending; s03_04 actively rebuilt at corrected large scale; s04 row4 unselected south/east phase issues. Limited top230 references remain limited only.','r01_c04':'13 selected at snapshot; last row being completed. Whole tile QA pending.','r02_c05':'8 selected at snapshot; stable tree frontier progressing. Three s03 roof positions deferred with explicit defects.','r01_c05':'Not begun as of snapshot; forthcoming helper scope avoids east overlap.'},'hostOutputAudit':'Not repeated while concurrent generation in progress; each returned root output has been registered before next call.','latestRootSelected':'r02_c04/native/s01_01-v001.png'}
out=m.next_path(B,'recovery-checkpoint')
m.write_new(out,data)
print(json.dumps({'saved':str(out),'selectedCoreCount':data['selectedCoreCount'],'perTile':{k:{a:v[a] for a in ['nativeVersions','nativePatchPositions','selectedCount']} for k,v in per.items()},'formalAcceptedCount':0}))


from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys
OUT=Path(__file__).resolve().parent
Z=OUT.parents[2]
sys.path.insert(0,str(Z))
import production_v2 as p
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ref(path): return {'file':str(path),'sha256':sha(path)}
checkpoint_path=OUT/'local-checkpoint-and-counts.json'
checkpoint=read(checkpoint_path)
excluded=set(checkpoint['excludedCoordinates'])
rows=[]; errors=[]
for r in range(1,9):
    for c in range(1,9):
        tile=f'r{r:02}_c{c:02}'
        if tile in excluded: continue
        directory=Z/tile; selection=read(directory/'selection.json') if (directory/'selection.json').exists() else {}
        selected=[]
        for sr in range(1,5):
            for sc in range(1,5):
                pid=f's{sr:02}_{sc:02}'; source=p.selected_path(directory,pid,selection)
                if not source.is_file(): continue
                try:
                    p.validate_native(source,directory,pid)
                    selected.append({'id':pid,**ref(source)})
                except Exception as exc: errors.append({'tile':tile,'id':pid,'error':str(exc)})
        rows.append({'tile':tile,'selectedUsableNativeCount':len(selected),'selectedSources':selected})
prior=read(Z/'progress.json')
counts={'effectiveOwnedTileCount':len(rows),'expectedNativeCoreCount':len(rows)*16,
 'selectedUsableNativeCount':sum(x['selectedUsableNativeCount'] for x in rows),
 'tilesWithAll16NativePatches':sum(x['selectedUsableNativeCount']==16 for x in rows),
 'tilesStillMissingNativePatches':sum(x['selectedUsableNativeCount']!=16 for x in rows),
 'internallyPassedDeliveredTiles':prior['internalQAPassedCount'],'formalAcceptedCount':prior['formalAcceptedCount']}
counts['missingNativePatchCount']=counts['expectedNativeCoreCount']-counts['selectedUsableNativeCount']
counts['fullSourceTilesPendingInternalRepairOrReview']=counts['tilesWithAll16NativePatches']-counts['internallyPassedDeliveredTiles']
assert counts['selectedUsableNativeCount']>=196
assert counts['fullSourceTilesPendingInternalRepairOrReview']>=0
assert not errors,errors
checkpoint['createdAtUtc']=datetime.now(timezone.utc).isoformat()
checkpoint['currentScopeCounts']=counts
checkpoint['currentSelectedSourceCensus']=rows
checkpoint['selectedSourceValidationErrors']=errors
checkpoint['censusMethod']='Current selected logical ids s01_01..s04_04 only; image dimensions, opacity, hashes, prompt/request/receipt checked via production_v2.validate_native. No previous candidate or historical ZIP scan.'
checkpoint_path.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':counts,'checkpoint':ref(checkpoint_path),'nonemptyTiles':[{'tile':r['tile'],'selected':r['selectedUsableNativeCount']} for r in rows if r['selectedUsableNativeCount']]},indent=2))

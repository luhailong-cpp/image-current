from pathlib import Path
import json,sys,datetime
zone=Path(__file__).resolve().parent.parent
tile=zone/sys.argv[1]
assert tile.parent==zone and tile.name[4:] in ['c15','c16'] and tile.name!='r07_c15'
patch,version=sys.argv[2:4]
native=tile/'native'/f'{version}.png'
assert native.exists()
selpath=tile/'selected-native.json'
selection=json.loads(selpath.read_text(encoding='utf-8-sig')) if selpath.exists() else {}
selection[patch]=native.name
selpath.write_text(json.dumps(selection,indent=2),encoding='utf-8')
p=tile/'tile-progress.json'
progress=json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}
valid=[k for k,v in selection.items() if (tile/'native'/v).exists()]
record=json.loads(Path(str(native)+'.generation.json').read_text(encoding='utf-8-sig'))
progress.update(owner='/root/east_resume',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='native-production-resumed-current-AGENTS',selectedCoreCount=len(valid),remainingCoreCount=16-len(valid),generatedNativeCount=len(list((tile/'native').glob('*.png'))),lastCompletedPatch=patch,lastCompletedNative=str(native),lastCompletedSha256=record['sha256'],missingSelectedIds=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in valid],inflightRequests=[],inflightGeneration=None,unsavedSuccessfulOutputs=[],newGenerationAllowed=True,actualModel=None,actualQuality=None,requestedFutureImageModel='free/included2.5 preferred; existing builtin2.0 allowed; actual model undisclosed',modelRouteVerified=False,paidApiAllowed=False,nextStep='Continue missing native cores then review remaining seams; existing P2 issues remain unpassed until repaired.')
p.write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'tile':tile.name,'selected':len(valid),'last':patch,'sha256':record['sha256']}))

from pathlib import Path
import json,sys,datetime
T=Path(__file__).resolve().parent
records=list((T/'native').glob('*.png.generation.json'))
selection=json.loads((T/'selection.json').read_text(encoding='utf-8-sig')) if (T/'selection.json').exists() else {}
selected={f's{r:02d}_{c:02d}':selection.get(f's{r:02d}_{c:02d}',str(T/'native'/f's{r:02d}_{c:02d}.png')) for r in range(1,5) for c in range(1,5)}
available={k:v for k,v in selected.items() if Path(v).is_file()}
state={'tile':'r06_c04','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generatedNativeCount':len(records),'selectedNativeCount':len(available),'missingNativePatches':[p for p in selected if p not in available],'complete4kCandidateCount':int(any((T/'candidate').glob('*-candidate-*.png'))),'internalQA':'pending','formalAcceptedCount':0,'nextStep':sys.argv[1],'nativeSize':[1254,1254],'corePixels':1024,'haloPixels':115,'actualModel':None,'actualQuality':None,'capacity5000Validated':False}
(T/'production-status.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(state,ensure_ascii=False))


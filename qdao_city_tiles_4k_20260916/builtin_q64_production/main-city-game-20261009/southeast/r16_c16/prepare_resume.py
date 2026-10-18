from pathlib import Path
import importlib.util,json,sys
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('production_workflow',T.parent/'production_workflow.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
if not w.CONFIG.exists():
 origin=T.parent/'r14_c15/records/p04_02_v20261012T132701_018eddce.preparation.json'
 prior=w.read(origin);carried=T/'records/config-carried-snapshot-20261013.json'
 if not carried.exists():
  w.atomic_json(carried,prior['configSnapshot'],exclusive=True)
  w.atomic_json(T/'records/config-carried-origin-20261013.json',{'recordedAt':w.now(),'missingHistoricalPath':str(w.CONFIG),'sourcePreparation':str(origin),'sourcePreparationSha256':w.sha(origin),'preservedSnapshot':str(carried),'preservedSnapshotSha256':w.sha(carried),'status':'historical_preferences_only_not_current_backend_claim','actualModel':None,'actualQuality':None},exclusive=True)
 w.CONFIG=carried
print(json.dumps(w.prepare(T.name,sys.argv[1]),ensure_ascii=False,indent=2))

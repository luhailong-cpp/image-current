import sys,os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
f=ROOT/'continuation-round-20261011.json'
state=p.read(f) if f.exists() else {'resumedAt':p.now(),'scope':list(p.OWNED),'networkRoute':'builtin image_gen.imagegen only','currentCoordinate':'r03_c05/south boundary to r04_c05','candidateCount':4,'coveredAssignedCores':64,'internalFullyPassedTileCount':0,'formalAcceptedCount':0,'firstNewOutputThisRound':None,'errors':[],'gitOperationsThisRound':0,'noExpansionOutsideAssignment':True,'nextStep':'Repair window-lattice discontinuity in south-segment04; merge actual successful outputs and inspect native boundaries.'}
state['updatedAt']=p.now();state['successfulSavedOutputsFromPreviousResume']=[{'file':str(x),'sha256':p.sha(x)} for x in sorted((ROOT/'continuation-20261011').glob('south-segment*/raw-v1.png'))]
state['status']='saved_outputs_recovered_repair_ready'
tmp=ROOT/'continuation-20261011/round-state-writing.json';p.put_json(tmp,state);os.replace(tmp,f);print(json.dumps(state,ensure_ascii=False))

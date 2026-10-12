import sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
raw=ROOT/'continuation-20261011/south-segment04/raw-v2.png';rec=p.read(str(raw)+'.generation.json');state=p.read(ROOT/'continuation-round-20261011.json');state['firstNewOutputThisRound']={'file':str(raw),'sha256':p.sha(raw),'pixels':[1254,1254],'hostSource':rec['hostSource'],'parameters':str(raw.parent/'parameters-v2.json'),'record':str(raw)+'.generation.json'};state['status']='builtin_new_image_saved_native_merge_in_progress';state['updatedAt']=p.now();state['currentCoordinate']='r03_c05/r04_c05 four-segment southern seam';state['nextStep']='Compose four saved native repairs with recorded source maps, preserving geometry; inspect all join crops.'
tmp=ROOT/'continuation-20261011/round-state-writing.json';p.put_json(tmp,state);os.replace(tmp,ROOT/'continuation-round-20261011.json')
print(state['firstNewOutputThisRound'])

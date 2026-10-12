import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json
Z=Path(__file__).resolve().parents[1];ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
n=[Z/'native'/('r09_c06_repair_b_complete_'+part+'_v3.png') for part in ['upper','lower']]
m={'schemaVersion':1,'outputPrefix':'repair-r09_c06-bcomplete-v3','baseContext':ref(Z/'qa/full-tile-r09_c06-context-native.png'),'nativeSources':[ref(p) for p in n],'nativeGenerationRecords':[ref(Path(str(p)+'.generation.json')) for p in n],'stride':1024,'tileContextBox':[1360,500,2614,2778],'objectPolygon':[[535,60],[552,68],[580,80],[615,85],[650,87],[685,80],[715,68],[740,55],[740,2168],[638,2210],[535,2168]],'sideSeamBands':{'left':[523,543],'right':[733,753]},'qaCrops':{'top':[450,0,820,560],'upperband':[450,400,820,960],'overlap':[450,920,820,1390],'lowerband':[450,1280,820,1840],'foot':[450,1780,820,2278]},'notes':['Only original 1254x1254 AI pixels in source composite; no resampling.','One complete object selection from curved cap underside through foot shadow. No separate per-patch outer masks.','Outside B full object the original stable base remains unchanged; parent will combine this full-object mask with other accepted subregions.']}
p=Z/'qa/repair-r09_c06-bcomplete-v3.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(ref(p))

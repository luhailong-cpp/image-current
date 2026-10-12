import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
i=int(sys.argv[1]);HERE=ROOT/'continuation-20261011';cur=HERE/f'south-segment{i:02d}';prev=HERE/f'south-segment{i-1:02d}'
cp=p.read(cur/'preparation.json');pp=p.read(prev/'preparation.json');offset=cp['contextNorthTileBox'][0]-pp['contextNorthTileBox'][0];width=1254-offset
im=Image.open(cur/'context-native.png').convert('RGB');anchor=Image.open(prev/'raw-v1.png').convert('RGB');im.paste(anchor.crop((offset,700,1254,912)),(0,700))
info=p.save_png(cur/'edit-guide-with-left-anchor.png',im)
p.put_json(cur/'edit-guide-manifest.json',{'guide':info,'base':str(cur/'context-native.png'),'baseSHA256':p.sha(cur/'context-native.png'),'leftSource':str(prev/'raw-v1.png'),'leftSourceSHA256':p.sha(prev/'raw-v1.png'),'sameCoordinateCopy':[0,700,width,912],'resampled':False,'nativeScale':1,'referenceOnly':True})

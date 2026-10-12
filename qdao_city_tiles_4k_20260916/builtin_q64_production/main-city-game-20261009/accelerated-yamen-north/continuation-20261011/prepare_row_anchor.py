import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent
a=Image.open(HERE/'roof-row02/context-native.png').convert('RGB');b=Image.open(HERE/'roof-row01/raw-v1.png').convert('RGB')
a.paste(b.crop((1147,455,1254,785)),(0,455));p.save_png(HERE/'roof-row02/edit-guide-with-left-anchor.png',a)
p.put_json(HERE/'roof-row02/guide-record.json',{'original':str(HERE/'roof-row02/context-native.png'),'leftAnchorRaw':str(HERE/'roof-row01/raw-v1.png'),'leftAnchorSHA256':p.sha(HERE/'roof-row01/raw-v1.png'),'nativeCopiedBox':[1147,455,1254,785],'destinationTopLeft':[0,455],'role':'reference edit guide only, no final art claim','resized':False})


import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;OUT=HERE/'checkpoint-v2';OUT.mkdir(exist_ok=True)
sources={'r03_c04':ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png','r03_c05':ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png','r04_c04':ROOT/'r04_c04/candidate/r04_c04-pipeline-fixed-native-contexts-71cabb17b21f.png','r04_c05':ROOT/'r04_c05/candidate/r04_c05-pipeline-fixed-native-contexts-0e9a0c64dd52.png'}
im=Image.new('RGB',(320,320))
for tile,src in sources.items():
 a=Image.open(src);box=(3936 if tile.endswith('04') else 0,3936 if tile.startswith('r03') else 0,4096 if tile.endswith('04') else 160,4096 if tile.startswith('r03') else 160);im.paste(a.crop(box),(0 if tile.endswith('04') else 160,0 if tile.startswith('r03') else 160))
p.save_png(OUT/'fourway-native.png',im)
p.put_json(OUT/'sources.json',{tile:{'file':str(src),'sha256':p.sha(src),'assembly':str(src.with_suffix('.assembly.json'))} for tile,src in sources.items()})
print(OUT)


from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'
a=Image.open(QA/'multi-boundary-v02-r09_c04-candidate-4096.png')
b=Image.open(QA/'c04-bamboo-join-v02-r09_c04-candidate-4096.png')
boxes={'target':[250,330,1050,740],'right-seam':[1040,350,1350,650],
       'top-bright-stalk':[860,-80,1050,400],'bottom-vessel':[350,1100,1050,1330]}
for name,box in boxes.items():
    local=[box[j]+[2400,500][j%2] for j in range(4)]
    first,second=a.crop(local),b.crop(local)
    pair=Image.new('RGB',(first.width*2,first.height))
    pair.paste(first,(0,0));pair.paste(second,(first.width,0))
    pair.save(QA/('c04-bamboo-v02-'+name+'-base-left-candidate-right-100pct.png'))
b.crop((2400,500,3654,1754)).save(QA/'c04-bamboo-v02-candidate-patch-100pct.png')

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'
stems=['r10_c03_s01_01_v02','r10_c03_s01_02_v01','r10_c03_s01_03_v01']
above_path=ROOT/'output'/'r09_c03-native-candidate-v05.png'
above=Image.open(above_path)
row=Image.new('RGB',(3072,600))
evidence=[]
for i,stem in enumerate(stems):
    source_path=ROOT/'native'/(stem+'.png')
    source=Image.open(source_path)
    pair=Image.new('RGB',(1024,600))
    pair.paste(above.crop((i*1024,3796,(i+1)*1024,4096)),(0,0))
    pair.paste(source.crop((115,115,1139,415)),(0,300))
    target=QA/('r10-independent-'+stem+'-actual-v05-seam-native100.png')
    pair.save(target)
    row.paste(pair,(i*1024,0))
    evidence.append({'path':target.as_posix(),'dimensions':[1024,600],
      'globalBox':[8192+i*1024,36564,9216+i*1024,37164],'seamGlobalY':36864,'seamImageY':300,
      'sources':[above_path.as_posix(),source_path.as_posix()],
      'sourceCrops':[[i*1024,3796,(i+1)*1024,4096],[115,115,1139,415]],'resampling':False})
boxes={'package-leaf-rope':[0,210,670,410],
       'flowers-and-right-rectangle':[1724,210,2224,470],
       'post-foot-and-wall':[1240,210,1740,520]}
for name,box in boxes.items():
    target=QA/('r10-independent-'+name+'-native100.png')
    row.crop(box).save(target)
    evidence.append({'path':target.as_posix(),'globalBox':[8192+box[0],36564+box[1],8192+box[2],36564+box[3]],'seamGlobalY':36864,'seamImageY':300-box[1],'resampling':False})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'selectedSnapshot':stems+[None],
    'aboveActualFinal':above_path.as_posix(),'aboveSha256':hashlib.sha256(above_path.read_bytes()).hexdigest(),
    'artifacts':evidence,'limitations':['Only 3 selected row-one cores inspected; unselected fourth core excluded.']}
(QA/'r10-independent-evidence.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))

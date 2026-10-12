import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=ROOT/'continuation-20261011';OUT=HERE/'bottom-return01';OUT.mkdir(exist_ok=True)
im=Image.new('RGB',(4096,8192));im.paste(Image.open(HERE/'merged-south-v1/r03_c05/integrated-candidate-native.png'),(0,0));im.paste(Image.open(HERE/'merged-south-v1/r04_c05/integrated-candidate-native.png'),(0,4096))
box=[0,3697,1254,4951];info=p.save_png(OUT/'context-native.png',im.crop(box));p.put_json(OUT/'preparation.json',{'contextPairBox':box,'contextWorldBox':[16384,11889,17638,13143],**info,'nativeScale':1,'resampled':False,'defectBoxInContext':[100,575,400,685]})

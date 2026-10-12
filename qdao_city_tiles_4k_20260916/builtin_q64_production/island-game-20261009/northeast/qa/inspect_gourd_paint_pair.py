import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
outdir=ZONE/'qa/gourd-paint-pair-20261011';outdir.mkdir(exist_ok=True)
can=Image.new('RGB',(8192,4096));sources=[]
for tid,at in [('r03_c12',[0,0]),('r03_c13',[4096,0])]:
 p=ZONE/'tiles'/f'{tid}.png';can.paste(Image.open(p).convert('RGB'),tuple(at));sources.append({'file':p.as_posix(),'sha256':sha(p),'canvasPaste':at})
repairs=[]
for ident,at in [('r03_c12_cross_02_04_gourd_paint_repair',[3264,1536]),('r03_c13_cross_02_01_gourd_paint_repair',[4288,1536])]:
 p=ZONE/'native'/f'{ident}.png';im=Image.open(p);assert im.size==(1254,1254);can.paste(im.crop((115,115,1139,1139)),tuple(at));repairs.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'coreCrop':[115,115,1139,1139],'canvasPaste':at})
can.crop((3072,1280,5504,2816)).save(outdir/'context-native.png')
boxes={'top-left':[3264,1408,4288,1664],'top-right':[4288,1408,5312,1664],'bottom-left':[3264,2432,4288,2688],'bottom-right':[4288,2432,5312,2688],'left':[3136,1536,3392,2560],'right':[5184,1536,5440,2560],'repair-join':[4160,1536,4416,2560],'tile-boundary':[3968,1536,4224,2560],'horizontal-left':[3264,1920,4288,2176],'horizontal-right':[4288,1920,5312,2176]}
for name,box in boxes.items():can.crop(tuple(box)).save(outdir/f'{name}-100pct.png')
write(outdir/'review.json',{'status':'candidate_pending_visual_inspection','sources':sources,'repairs':repairs,'cropBoxes':boxes,'actualModel':None,'actualQuality':None,'formalAccepted':False})
print(outdir.as_posix())

from pathlib import Path
from PIL import Image
import json,hashlib,sys
Z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
ID='r04_c12_cross_01_03_jar_repair'
mode=sys.argv[1]
if mode=='prepare':
 box=[2445,13,3699,1267];out=Image.new('RGB',(1254,1254));sources=[]
 for ident,at in [('r04_c12_p01_03',[2048,0]),('r04_c12_p01_04_v2',[3072,0]),('r04_c12_p02_03',[2048,1024]),('r04_c12_p02_04_v3',[3072,1024])]:
  p=Z/'native'/f'{ident}.png';r=read(p.with_suffix('.png.generation.json'));assert sha(p)==r['sha256'];im=Image.open(p);assert im.size==(1254,1254)
  x,y=at;inter=[max(x,box[0]),max(y,box[1]),min(x+1024,box[2]),min(y+1024,box[3])];crop=[inter[0]-x+115,inter[1]-y+115,inter[2]-x+115,inter[3]-y+115];paste=[inter[0]-box[0],inter[1]-box[1]];out.paste(im.crop(crop),paste)
  sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':crop,'targetPaste':paste,'generationRecord':p.with_suffix('.png.generation.json').as_posix()})
 dest=Z/'guides'/f'{ID}.png';assert not dest.exists();out.save(dest)
 d={'operation':'exact native core mosaic crop for complete broken jar foot and all4接入边; no resampling or feathering','file':dest.as_posix(),'sha256':sha(dest),'size':[1254,1254],'tileLocalBox':box,'nativeWorldBox':[47501,12301,48755,13555],'coreWorldBox':[47616,12416,48640,13440],'coreCrop':[115,115,1139,1139],'sources':sources,'finalArt':False,'preservedRightBorder':'repair core stops tileLocalx3584, does not touch right230pxnative anchor near tile eastern edge'}
 write(dest.with_suffix('.png.derivation.json'),d)
 refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: exact native mosaic includes complete broken central jar foot and all4 perimeter anchors','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},*read(Z/'reference-audit-resumed-20261010.json')['references']]
 write(Z/'prompts'/f'{ID}.inputs.json',refs);print(json.dumps(d))
elif mode=='inspect':
 src=Z/'native'/f'{ID}.png';im=Image.open(src);assert im.size==(1254,1254);base=Image.open(Z/'guides'/f'{ID}.png').convert('RGB');base.paste(im.crop((115,115,1139,1139)),(115,115));base.save(Z/'qa'/f'{ID}.overlay-composite-100pct.png')
 crops={'top':(0,0,1254,230),'bottom':(0,1024,1254,1254),'left':(0,0,230,1254),'right':(1024,0,1254,1254),'center':(200,200,1054,954)};evidence=[]
 for key,box in crops.items():
  p=Z/'qa'/f'{ID}.{key}-100pct.png';base.crop(box).save(p);evidence.append(p.as_posix())
 d={'operation':'exact native1024 repair core overlay; no resampling or feathering','source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[2560,128],'worldPaste':[47616,12416],'review':'pending','reviewerEvidence':evidence,'preservedRightBorder':True,'selectionNotModified':True}
 write(Z/'qa'/f'{ID}.overlay.json',d);print(json.dumps(d))


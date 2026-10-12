"""Exact native external crop QA and full hard-core pixel proof for this tile only."""
from pathlib import Path
import sys,json,importlib.util
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
N=Z/'r05_c07/candidate/r05_c07-candidate-localcut-e280bcf6d4f6.png'
W=Z/'r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.png'
NW=Z/'r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png'
assert p.sha(N)=='75374335df252505edbb301d18c17bca9434b8ac74852bdafa698eaba41f10ec'
assert p.sha(W)=='105ed0953773073a1b336660887ab78e4f8ef145ec74285ac0f1bc3ae0a77595'
candidate=Path(sys.argv[1]);m=p.read(candidate.with_suffix('.assembly.json'));output=m['output'];a=np.array(Image.open(candidate).convert('RGB'));sel=p.read(T/'selection.json');proof=[]
for patch in p.coordinates('r06_c07')['patches']:
 pid=patch['id'];source=p.selected_path(T,pid,sel);ref=p.validate_native(source,T,pid);r=int(pid[1:3])-1;c=int(pid[4:6])-1
 sample=np.array(Image.open(source).convert('RGB'))[115:1139,115:1139];part=a[r*1024:(r+1)*1024,c*1024:(c+1)*1024]
 assert np.array_equal(sample,part)
 proof.append(dict(id=pid,source=ref,sourceCropLTRB=[115,115,1139,1139],pasteXY=[c*1024,r*1024],verifiedPixels=1024*1024,allRGBExact=True,sourceResampled=False))
proof_path=T/'qa'/(candidate.stem+'.native-pixel-proof.json');p.write_json(proof_path,dict(candidate=output,method='exact hard1024 cores',sourceCount=16,verifiedPixels=4096*4096,allRGBExact=True,allOpaque=True,colorChanges=False,blending=False,warp=False,resize=False,sources=proof))
dir=T/'qa'/(candidate.stem+'.actual-final-neighbors');dir.mkdir(exist_ok=False)
ims={'north':Image.open(N).convert('RGB'),'west':Image.open(W).convert('RGB'),'target':Image.open(candidate).convert('RGB'),'northwest':Image.open(NW).convert('RGB')};crops=[]
def crop(name,size,parts,rotate=False):
 image=Image.new('RGB',size)
 for role,box,xy in parts:image.paste(ims[role].crop(box),xy)
 if rotate:image=image.transpose(Image.Transpose.ROTATE_90)
 path=dir/(name+'.png');p.save_png(path,image);crops.append(dict(file=str(path),sha256=p.sha(path),nativePixelScale=1,sourceResampled=False,parts=parts,rotationCCW90=rotate,actuallyViewed=False,visualVerdict='pending'))
for s in range(4):
 x=s*1024;crop(f'north-segment{s+1:02d}',(1024,320),[('north',[x,3936,x+1024,4096],[0,0]),('target',[x,0,x+1024,160],[0,160])])
 y=s*1024;crop(f'west-segment{s+1:02d}',(320,1024),[('west',[3936,y,4096,y+1024],[0,0]),('target',[0,y,160,y+1024],[160,0])],True)
for v in (1024,2048,3072):
 crop(f'north-junction-x{v}',(320,320),[('north',[v-160,3936,v+160,4096],[0,0]),('target',[v-160,0,v+160,160],[0,160])])
 crop(f'west-junction-y{v}',(320,320),[('west',[3936,v-160,4096,v+160],[0,0]),('target',[0,v-160,160,v+160],[160,0])])
crop('northwest-corner-extra',(320,320),[('northwest',[3936,3936,4096,4096],[0,0]),('north',[0,3936,160,4096],[160,0]),('west',[3936,0,4096,160],[0,160]),('target',[0,0,160,160],[160,160])])
p.write_json(dir/'manifest.json',dict(candidate=output,actualNorth=dict(file=str(N),sha256=p.sha(N)),actualWest=dict(file=str(W),sha256=p.sha(W)),actualNorthwest=dict(file=str(NW),sha256=p.sha(NW)),requiredCrops=14,extraCorner=1,crops=crops,actuallyViewed=False,formalAccepted=False))
print(json.dumps(dict(proof=str(proof_path),verifiedPixels=4096*4096,externalManifest=str(dir/'manifest.json'),externalCrops=len(crops))))

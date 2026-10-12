"""Final evidence and canonical p23 alias; no original source changes."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import hashlib,json,shutil,datetime
Z=Path(__file__).resolve().parent.parent
P='r06_c12_p22-p23-bridge'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
 p=Path(p)
 if p.exists():raise ValueError('Refusing overwrite '+str(p))
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return {'path':str(p),'sha256':sha(p),'role':role}
def im(p):return Image.open(p).convert('RGB')
old=Z/'native'/f'{P}-p23-candidate.png'
alias=Z/'native/r06_c12_p23-p22-bridge-p23-candidate.png'
if alias.exists():raise ValueError('Alias already exists')
shutil.copy2(old,alias)
orig=read(str(old)+'.derived.json')
save(str(alias)+'.derived.json',{'file':str(alias),'sha256':sha(alias),'patchId':'r06_c12_p23',
 'pixels':[1254,1254],'nativeGlobalBox':orig['nativeGlobalBox'],
 'derivedFrom':[{**ref(old,'p23 mechanically derived bridge candidate'),'derivedRecord':str(old)+'.derived.json'}],
 'operation':'byte-for-byte canonical-name alias only; no resampling, painting or new image_gen call',
 'status':'candidate_pending_full_tile_QA','formalAccepted':False})
def pair(a,b):
 out=Image.new('RGB',(2278,1254))
 out.paste(im(a).crop((0,0,1139,1254)),(0,0))
 out.paste(im(b).crop((115,0,1254,1254)),(1139,0))
 return out
a=Z/'native/r06_c12_p22-v2.png';b=Z/'native/r06_c12_p23-v1.png'
belowpaths=[Z/'native/r06_c12_p32-v1.png',Z/'native/r06_c12_p33-v1.png']
original=pair(a,b);below=pair(*belowpaths)
out=Image.new('RGB',(1254,256))
out.paste(original.crop((512,1011,1766,1139)),(0,0))
out.paste(below.crop((512,115,1766,243)),(0,128))
baseline=Z/'qa'/f'{P}-bottom-original-baseline.png';out.save(baseline)
save(str(baseline)+'.derived.json',{'file':str(baseline),'sha256':sha(baseline),'pixels':[1254,256],
 'derivedFrom':[ref(p,'original native, before bridge') for p in [a,b]+belowpaths],
 'operation':'1:1 hard crop/paste before bridge, no resize/blend','seamLocalY':128,
 'topOriginalBoxes':[[512,1011,1139,1139],[115,1011,742,1139]],
 'bottomOriginalBoxes':[[512,115,1139,243],[115,115,742,243]],'purpose':'prove provenance of bottom QA color discontinuity'})
current=im(Z/'qa'/f'{P}-bottom-outer.png')
same=ImageChops.difference(current.crop((0,128,1254,256)),out.crop((0,128,1254,256))).getbbox() is None
if not same:raise ValueError('Unexpected difference in untouched lower neighbor band')
source_seam=below.crop((1011,0,1267,512))
source_seam_path=Z/'qa'/f'{P}-p32-p33-original-seam.png';source_seam.save(source_seam_path)
save(str(source_seam_path)+'.derived.json',{'file':str(source_seam_path),'sha256':sha(source_seam_path),'pixels':[256,512],
 'derivedFrom':[ref(p,'unchanged row3 source') for p in belowpaths],
 'operation':'1:1 crop/paste of p32 right and p33 left native pixels only','seamLocalX':128,
 'purpose':'original p32/p33 boundary independent of new bridge'})
c22=Z/'native'/f'{P}-p22-candidate.png';c23=alias
candidate=pair(c22,c23)
above_paths=[Z/'native/r06_c12_p12-bridge-candidate.png',Z/'native/r06_c12_p13-p14-bridge-p13-candidate.png']
above=pair(*above_paths)
out2=Image.new('RGB',(1254,256))
out2.paste(above.crop((512,1011,1766,1139)),(0,0))
out2.paste(candidate.crop((512,115,1766,243)),(0,128))
newtop=Z/'qa'/f'{P}-top-current-selected.png';out2.save(newtop)
save(str(newtop)+'.derived.json',{'file':str(newtop),'sha256':sha(newtop),'pixels':[1254,256],
 'derivedFrom':[ref(p,'current row1 neighbor') for p in above_paths]+[ref(p,'new bridge-derived row2 candidate') for p in [c22,c23]],
 'operation':'native 1:1 crop and hard paste at row1-row2 core border; no resize/blend',
 'seamLocalY':128,'purpose':'QA against latest selected p13/p14 bridge candidate'})
save(Z/'records'/f'{P}-bottom-provenance.json',{
 'bottomNeighborBandUnchangedPixelForPixel':same,'comparisonLocalBox':[0,128,1254,256],
 'sourceBoundaryAtQaX':627,'sourceBoundaryBetween':['r06_c12_p32-v1','r06_c12_p33-v1'],
 'baseline':ref(baseline,'before p22/p23 bridge'),'current':ref(Z/'qa'/f'{P}-bottom-outer.png','after p22/p23 bridge'),
 'sourceOnlySeam':ref(source_seam_path,'p32/p33 source pixels only'),
 'conclusion':'The vertical timber tone/grain discontinuity at x627 in the lower half belongs to unchanged p32/p33. New bridge removed the row2 core defect but cannot certify the existing row3 seam.',
 'additionalReview':'Compare top half vs unchanged lower half for new horizontal join drift too; source provenance is not visual acceptance.'})
print(json.dumps({'p22':str(c22),'p23':str(c23),'bottomOriginalPixelsUnchanged':same,
 'newTopQa':str(newtop),'baselineQa':str(baseline),'sourceOnlyQa':str(source_seam_path)},ensure_ascii=False))


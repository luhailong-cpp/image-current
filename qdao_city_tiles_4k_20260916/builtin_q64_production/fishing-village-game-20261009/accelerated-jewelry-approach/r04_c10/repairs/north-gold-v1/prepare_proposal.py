from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json,hashlib
d=Path(__file__).parent
before=Image.open(d/'context-before-native.png').convert('RGB')
native=Image.open(d/'repair-native.png').convert('RGB')
assert before.size==native.size==(1254,1254)
# Native-sized proposal mask. Polygon is restricted to blurry gold and its immediate blur halo.
poly=[(-30,545),(13,553),(44,579),(79,591),(95,584),(100,558),(112,542),(132,530),(152,526),(178,528),(204,539),(225,556),(243,584),(253,612),(257,649),(253,666),(234,687),(132,702),(-30,702)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(4))
# Restrict lower transition to sharp gold; fade to unchanged south source by y690.
pix=mask.load()
for y in range(652,1254):
 fade=max(0,min(1,(690-y)/38))
 for x in range(0,280):pix[x,y]=round(pix[x,y]*fade)
# no pixels beyond declared ROI
roi=(0,510,280,690)
guard=Image.new('L',mask.size);guard.paste(mask.crop(roi),roi[:2]);mask=guard
mask.save(d/'contribution-mask-1254.png')
rgba=native.convert('RGBA');rgba.putalpha(mask);rgba.crop(roi).save(d/'contribution-roi-rgba.png')
mask.crop(roi).save(d/'contribution-roi-alpha.png')
after=Image.composite(native,before,mask);after.save(d/'context-after-proposal-native.png')
qbox=(0,500,400,760)
before.crop(qbox).save(d/'qa-before-native.png');after.crop(qbox).save(d/'qa-after-native.png')
pair=Image.new('RGB',(800,260));pair.paste(before.crop(qbox),(0,0));pair.paste(after.crop(qbox),(400,0));pair.save(d/'qa-before-after-native.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=mask.getbbox()
record={'status':'repair_ready_for_root_integration_only','notAppliedToCandidates':True,'contextGlobalBox':[36864,11661,38118,12915],'nativeDimensions':[1254,1254],'nativeFile':str(d/'repair-native.png'),'nativeSha256':sha(d/'repair-native.png'),'actualModel':None,'actualQuality':None,'tool':'image_gen__imagegen','roiContextBox':list(roi),'roiDimensions':[280,180],'roiGlobalBox':[36864,12171,37144,12351],'rgbaFile':str(d/'contribution-roi-rgba.png'),'rgbaSha256':sha(d/'contribution-roi-rgba.png'),'maskFile':str(d/'contribution-roi-alpha.png'),'maskSha256':sha(d/'contribution-roi-alpha.png'),'maskMode':'L 0..255, straight alpha; 255 replacement, 0 unchanged; source pixels never resized','maskActualNonzeroContextBox':list(a),'polygonContextPoints':poly,'featherGaussianSigma':4,'southTransitionFadeContextY':[652,690],'compositingEquation':'result=(repair*alpha + current_candidate*(255-alpha))/255; round to byte. Current candidate is the final root version, not the saved before version.','tileContributions':[{'tile':'r03_c10','destinationLocalBox':[0,3979,280,4096],'sourceRoiCrop':[0,0,280,117]},{'tile':'r04_c10','destinationLocalBox':[0,0,280,63],'sourceRoiCrop':[0,117,280,180]}],'reference':{'file':str(d/'context-before-native.png'),'sha256':sha(d/'context-before-native.png'),'role':'exact native edit target and sharp gold continuation reference'},'beforeAfterQaFile':str(d/'qa-before-after-native.png'),'formalAccepted':False}
(d/'proposal.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'nativeDimensions':list(native.size),'ROI':record['roiGlobalBox'],'alphaBBox':list(a),'proposal':str(d/'proposal.json')}))


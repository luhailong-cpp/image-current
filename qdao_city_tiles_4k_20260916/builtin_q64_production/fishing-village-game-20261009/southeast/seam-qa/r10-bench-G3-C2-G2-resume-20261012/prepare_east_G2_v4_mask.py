from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent
text=(D/'check_native_rect_generation_v2.py').read_text()
text=text.replace("before=Image.open(job['beforeGuide']).convert('RGB');after=before.copy();after.paste(im.crop(BOX),BOX[:2])\nmask=np.zeros((1254,1254),bool);mask[BOX[1]:BOX[3],BOX[0]:BOX[2]]=True", "before=Image.open(job['beforeGuide']).convert('RGB')\nmask=np.asarray(Image.open(job['adoptMaskFile']).convert('L'))==255\nafter=Image.fromarray(np.where(mask[:,:,None],np.asarray(im.convert('RGB')),np.asarray(before)).astype(np.uint8),'RGB')")
text=text.replace("art.paste(im.crop(crop),dest[:2]);aa=np.asarray(art)\n    pmask=np.zeros((1254,1254),bool);pmask[dest[1]:dest[3],dest[0]:dest[2]]=True","pmask=np.zeros((1254,1254),bool);pmask[dest[1]:dest[3],dest[0]:dest[2]]=mask[crop[1]:crop[3],crop[0]:crop[2]]\n    aa=old.copy();aa[dest[1]:dest[3],dest[0]:dest[2]]=np.where(mask[crop[1]:crop[3],crop[0]:crop[2],None],np.asarray(im.convert('RGB'))[crop[1]:crop[3],crop[0]:crop[2]],old[dest[1]:dest[3],dest[0]:dest[2]])\n    art=Image.fromarray(aa,'RGB')")
text=text.replace("'baseCandidateManifest':job.get('baseCandidateManifest'),","'adoptMaskFile':job['adoptMaskFile'],'adoptMaskSha256':sha(job['adoptMaskFile']),'baseCandidateManifest':job.get('baseCandidateManifest'),")
out=D/'check_native_mask_generation_v1.py';assert not out.exists();out.write_text(text)
before=Image.open(D/'eastdeck-G2-conditioned-v3-bounded-preview-native1254.png').convert('RGB')
orig=Image.open(D/'eastdeck-G2-conditioned-v1-guide-native1254.png').convert('RGB')
# Remove bottom adoption from the preceding raw crop at natural board interior.
before.paste(orig.crop((440,1100,850,1150)),(440,1100))
beforePath=D/'eastdeck-G2-conditioned-v4-before-native1254.png';before.save(beforePath)
boxes=[(780,360,915,415),(780,470,915,530),(780,602,915,670),(780,771,915,845),(780,970,915,1045)]
mask=Image.new('L',(1254,1254),0);dr=ImageDraw.Draw(mask)
guide=Image.new('RGBA',(1254,1254),(255,255,255,0))
for b in boxes:
 nb=(b[0]-64,b[1]-32,b[2]+64,b[3]+32);guide.paste(before.crop(nb).convert('RGBA'),nb[:2]);dr.rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=255)
guide.paste((255,255,255,0),(0,0,1254,1254),mask)
guidePath=D/'eastdeck-G2-conditioned-v4-five-gap-guide-native1254.png';guide.save(guidePath)
maskPath=D/'eastdeck-G2-conditioned-v4-adopt-mask-native1254.png';mask.save(maskPath)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'eastdeck-G2-conditioned-v4-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native five gap neighborhoods with holes','before':str(beforePath),'beforeSha256':sha(beforePath),'sourceBefore':str(D/'eastdeck-G2-conditioned-v3-bounded-preview-native1254.png'),'original':str(D/'eastdeck-G2-conditioned-v1-guide-native1254.png'),'revertedPreviousBox':[440,1100,850,1150],'mask':str(maskPath),'maskSha256':sha(maskPath),'guide':str(guidePath),'guideSha256':sha(guidePath),'holeGuideBoxes':boxes,'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(json.dumps({'maskBox':mask.getbbox(),'maskPixels':sum(mask.histogram()[255:]),'guide':str(guidePath)}))


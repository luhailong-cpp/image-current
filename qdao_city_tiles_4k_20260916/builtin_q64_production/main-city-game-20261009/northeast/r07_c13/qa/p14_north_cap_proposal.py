"""Exact native-pixel north cap proposal only. No candidate mutation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
HERE=Path(__file__).resolve().parent;TILE=HERE.parent;ZONE=TILE.parent
out=HERE/'p14-north-cap';out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=TILE/'native/p14.png';context=TILE/'layout-only/p14-mixed-context.png';src=Image.open(source).convert('RGB');orig=Image.open(context).convert('RGB')
for name,im in [('source',src),('before',orig)]:im.crop([230,50,500,250]).save(out/f'{name}-cap-1to1.png')
mask=Image.new('L',(1254,1254));draw=ImageDraw.Draw(mask)
# Trace the complete rounded upper cap. The actual north-half paste clips only
# at the existing tile boundary, not through either side of the object contour.
polygon=[(294,139),(301,122),(311,111),(323,103),(337,98),(351,96),(367,98),(382,103),(396,112),(407,125),(416,141),(427,165),(430,186),(419,210),(393,230),(358,240),(324,220),(302,191),(291,163)]
draw.polygon(polygon,fill=255)
# This proposal owns only pixels north of the new tile, y0..114.
mask.paste(0,(0,115,1254,1254));maskpath=out/'north-cap-binary-mask.png';mask.save(maskpath)
assert {i for i,count in enumerate(mask.histogram()) if count}<={0,255}
before=src.copy();before.paste(orig.crop([0,0,1254,115]),(0,0));after=before.copy();after.paste(src,(0,0),mask)
for name,im in [('before-shared',before),('after-shared',after)]:im.crop([230,50,500,250]).save(out/f'{name}-cap-1to1.png')
outside=ImageChops.difference(before,after);outside.paste((0,0,0),(0,0),mask);assert outside.getbbox() is None
north=ZONE/'r06_c13/candidates/r06_c13.candidate.png';assert sha(north)=='2920e92f3c34f6ae2e73a5a9e52fe862adef3230487c2df2f98f48a7de5b0b2e'
crop=[280,88,450,115];mx=mask.crop(crop);assert mx.getbbox()[0]>0 and mx.getbbox()[2]<170 and mx.getbbox()[1]>0
proposal={'id':'r07-p14-north-gold-cap','status':'local-integer-integration-proposal-awaiting-parent','source':str(source),'sourceSha256':sha(source),'sourceNativePixels':[1254,1254],'sourceGenerationRecord':str(source)+'.generation.json','sourceContextWorldBox':[52109,24461,53363,25715],'mask':str(maskpath),'maskSha256':sha(maskpath),'maskMode':'L','maskValues':[0,255],'maskFullContextNonzeroBox':mask.getbbox(),'polygonInContextPixels':polygon,'method':'Exact source RGB pixels under binary traced object mask; north half only; no source image filter, scaling, warp, blur or feathering','northCandidateBefore':str(north),'northCandidateBeforeSha256':sha(north),'integerTileOperations':[{'tile':'r06_c13','sourceCrop':crop,'maskCrop':crop,'destinationTileXY':[3237,4069],'worldBox':[52389,24549,52559,24576]}],'unchanged':{'p14Native':True,'candidateFilesWritten':False,'outsideMaskPixelIdentical':True},'edgeProof':{'maskZeroAtRectangleTop':True,'maskZeroAtRectangleLeft':True,'maskZeroAtRectangleRight':True,'bottomEdge':'existing north/south tile border; source p14 core starts at y115, so exact same generated cap continues below','noImageResampling':True,'noImageBlur':True,'binaryMaskNoFeather':True},'reviewEvidence':{'before':str(out/'before-shared-cap-1to1.png'),'after':str(out/'after-shared-cap-1to1.png'),'reviewScale':'1:1 native pixels'},'actualModel':None,'actualQuality':None,'formalAcceptedCount':0}
(out/'integration-proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(proposal,ensure_ascii=False))

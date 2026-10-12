import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
ident='r03_c12_cross_02_04_gourd_paint_repair'
canvas=Image.new('RGB',(8192,4096));sources=[]
for tid,at in [('r03_c12',[0,0]),('r03_c13',[4096,0])]:
 p=ZONE/'tiles'/f'{tid}.png';canvas.paste(Image.open(p).convert('RGB'),tuple(at));sources.append({'file':p.as_posix(),'sha256':sha(p),'canvasPaste':at})
gp=ZONE/'guides'/f'{ident}.png';assert not gp.exists();canvas.crop((3149,1421,4403,2675)).save(gp)
d={'operation':'exact1254 crop from two native4096 tiles; no scale or feather','sources':sources,'sourceCropInCanvas':[3149,1421,4403,2675],'nativeWorldBox':[48205,9613,49459,10867],'coreWorldBox':[48320,9728,49344,10752],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[3264,1536],'finalArt':False}
write(gp.with_suffix('.png.derivation.json'),d)
write(ZONE/'prompts'/f'{ident}.inputs.json',[{'file':gp.as_posix(),'sha256':sha(gp),'role':'only edit target; exact current native art authority for minimal glaze color repair','derivationRecord':gp.with_suffix('.png.derivation.json').as_posix()}])
(ZONE/'prompts'/f'{ident}.prompt.txt').write_text('Edit this image very minimally. Remove only the artificial rectangular color seams across the gold gourd and its green circular ornament: the horizontal seam at y627 and the vertical seam at x947. Smooth the abrupt tonal steps using the original adjacent gold and green shades. Preserve every contour and detail of the gold curl, circular frame, gourd silhouette, pedestal, stone paving and foliage. Keep the outer115-pixel halo and all four central1024 attachment edges unchanged, except let the repaired horizontal shading continue naturally toward the right edge where another adjacent native repair will join. Do not globally recolor, brighten, darken, repaint texture, move shapes, change framing or dimensions. Output the same1254x1254 image. Only the artificial rectangular paste boundaries should disappear.\n',encoding='utf-8')
cp=ZONE/'qa'/f'{ident}.before-context-native.png';canvas.crop((3072,1280,5504,2816)).save(cp)
write(ZONE/'qa'/f'{ident}.preparation.json',{'id':ident,'status':'prepared_not_generated','preparedAtUtc':now(),'sources':sources,'nativeWorldBox':d['nativeWorldBox'],'coreWorldBox':d['coreWorldBox'],'jointRepair':{'nextCoreWorldBox':[49344,9728,50368,10752],'coreOverlap':0,'nativeOverlap':230,'requireExactLeftNativeOverlapAnchor':True},'plannedTilePartitions':[{'tileId':'r03_c12','sourceCoreCrop':[115,115,947,1139],'tilePaste':[3264,1536]},{'tileId':'r03_c13','sourceCoreCrop':[947,115,1139,1139],'tilePaste':[0,1536]}],'mandatoryReview':['all outer edges of combined2048x1024 repair','x49152 true4K boundary','x49344 adjacent repair boundary','gold curl geometry and green inset circular frame','full horizontal band and gold gourd context'],'actualModel':None,'actualQuality':None})
print(gp.as_posix())

from r06_c13_extension import *
from PIL import Image,ImageDraw
p='root-adjacent44-v1';gp=Z/'guides'/f'{p}.four-edge-guide.png'
a=Image.open(gp).convert('RGB');s=Image.open(Z/'native/r07_c12_northrepair43-v1.png').convert('RGB')
# GUIDE ONLY: translated native thin-curb sample replaces the known incorrect thick curb, before AI rendering.
part=s.crop((800,428,1108,723))
mask=Image.new('L',part.size,0)
ImageDraw.Draw(mask).polygon([(0,0),(308,0),(308,85),(0,270)],fill=255)
a.paste(part,(230,175),mask)
a.save(gp)
meta=json.loads(Path(str(gp)+'.derived.json').read_text(encoding='utf-8'))
meta['guideOnlyThinCurbReplacement']={'source':ref(Z/'native/r07_c12_northrepair43-v1.png','thin curb sample for GUIDE ONLY'),'cropBox':[800,428,1108,723],'pasteAt':[230,175],'polygonMaskLocal':[[0,0],[308,0],[308,85],[0,270]],'translationOnly':True,'finalPixels':False,'reason':'remove wrong lowered thick curb conditioning; thin native-left line continues behind post; mask excludes source finial'}
meta['topAnchorException']={'box':[230,175,538,230],'reason':'inner halo only, thin curb must enter behind post; actual top core seam y115 is preserved'}
write(str(gp)+'.derived.json',meta)
planp=Z/'records'/f'{p}.plan.json';plan=json.loads(planp.read_text(encoding='utf-8'))
plan['references'][3]=ref(gp,'repair guide; four native anchors with disclosed thin-curb inner-halo correction only')
plan['guideCorrection']=meta['guideOnlyThinCurbReplacement'];plan['topAnchorException']=meta['topAnchorException']
write(planp,plan)

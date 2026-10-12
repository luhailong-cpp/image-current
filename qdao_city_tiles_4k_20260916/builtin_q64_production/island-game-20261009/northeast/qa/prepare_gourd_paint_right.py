import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
ident='r03_c13_cross_02_01_gourd_paint_repair';left='r03_c12_cross_02_04_gourd_paint_repair'
src=ZONE/'tiles/r03_c13.png';out=Image.open(src).convert('RGB').crop((77,1421,1331,2675));lp=ZONE/'native'/f'{left}.png';lim=Image.open(lp).convert('RGB');assert lim.size==(1254,1254)
out.paste(lim.crop((1024,0,1254,1254)),(0,0))
gp=ZONE/'guides'/f'{ident}.png';assert not gp.exists();out.save(gp)
d={'operation':'exact1254 native tile crop with exact230px left native repair overlap; no scale or feather','sources':[{'file':src.as_posix(),'sha256':sha(src),'sourceCrop':[77,1421,1331,2675]},{'file':lp.as_posix(),'sha256':sha(lp),'sourceCrop':[1024,0,1254,1254],'targetPaste':[0,0],'role':'left native repair overlap color and geometry authority'}],'nativeWorldBox':[49229,9613,50483,10867],'coreWorldBox':[49344,9728,50368,10752],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[192,1536],'finalArt':False}
write(gp.with_suffix('.png.derivation.json'),d)
write(ZONE/'prompts'/f'{ident}.inputs.json',[{'file':gp.as_posix(),'sha256':sha(gp),'role':'only edit target; left230 pixels are exact native repair anchor and must remain stable','derivationRecord':gp.with_suffix('.png.derivation.json').as_posix()}])
(ZONE/'prompts'/f'{ident}.prompt.txt').write_text('Edit this image very minimally. Remove only the artificial horizontal color seam across the gold gourd belly at y627, and smoothly continue the existing repaired gold shading in the left230 pixels across the rest of the gourd. The left230 pixels are the exact neighboring repair anchor: preserve their color and geometry. Use original adjacent gold shades to remove the tonal step without brightening or darkening the whole image. Keep all stonework, silhouette, texture scale, pedestal shapes, highlights, framing and dimensions unchanged. Preserve the outer115-pixel halo and central1024 crop attachment edges, especially y115, y1139 and x1139. Output the same1254x1254 image. The only visible change should be removal of the artificial paste boundaries in the gold surface.\n',encoding='utf-8')
print(gp.as_posix())

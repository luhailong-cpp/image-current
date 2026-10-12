from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent;Z=T.parent
src=T/'native/s04_01_resume01.png'
west=Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png'
north=T/'native/s03_01_resume01.png'
im=Image.open(src).convert('RGB')
w=Image.open(west).convert('RGB');n=Image.open(north).convert('RGB')
im.paste(w.crop((3981,2957,4096,4096)),(0,0))
im.paste(n.crop((115,1024,1254,1139)),(115,0))
f=T/'layout-only/s04_01_curbfix01.exact-boundary-guide.png';im.save(f)
p.write_json(f.with_suffix('.png.derivation.json'),{'gameArt':False,'role':'layout-only edit guide with exact accepted western candidate and selected northern core boundary','base':{'file':str(src),'sha256':p.sha(src)},'west':{'file':str(west),'sha256':p.sha(west),'sourceCropLTRB':[3981,2957,4096,4096],'pasteXY':[0,0]},'north':{'file':str(north),'sha256':p.sha(north),'sourceCropLTRB':[115,1024,1254,1139],'pasteXY':[115,0]},'sourceResampled':False,'file':str(f),'sha256':p.sha(f)},replace=False)
print(f)


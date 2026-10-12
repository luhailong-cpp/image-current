from pathlib import Path
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parent;T=D.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=[282,384,1536,1638];out=Image.new('RGB',(1254,1254));sources=[]
for r in [1,2]:
 for c in [1,2]:
  s=json.loads((T/'records'/f'p{r}{c}.selection.json').read_text(encoding='utf-8-sig'));p=Path(s['file']);bb=[(c-1)*1024,(r-1)*1024,c*1024,r*1024];inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
  crop=[inter[0]-bb[0]+115,inter[1]-bb[1]+115,inter[2]-bb[0]+115,inter[3]-bb[1]+115];at=[inter[0]-box[0],inter[1]-box[1]];out.paste(Image.open(p).convert('RGB').crop(crop),at);sources.append({'file':str(p),'sha256':sha(p),'nativeCrop':crop,'pasteAt':at})
out.save(D/'target-native.png');rgba=out.convert('RGBA');rgba.paste((0,0,0,0),(607,146,647,664));rgba.save(D/'target-inpaint-native.png')
(D/'target-derivation.json').write_text(json.dumps({'tile':'r05_c11','tileTargetBox':box,'nativeDimensions':[1254,1254],'sources':sources,'operation':'Unresampled native selected-core crops pasted into exact tile box; second image alpha knockout only, no painted pixels','targetSha256':sha(D/'target-native.png'),'inpaintSha256':sha(D/'target-inpaint-native.png'),'transparentHoleNativeBox':[607,146,647,664],'transparentHoleTileBox':[889,530,929,1048]},indent=2)+'\n')
print(str(D/'target-inpaint-native.png'))

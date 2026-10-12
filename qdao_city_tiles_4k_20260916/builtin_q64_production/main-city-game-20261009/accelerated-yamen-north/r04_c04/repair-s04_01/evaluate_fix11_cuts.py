from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix11_centered'
G=np.array(Image.open(D/'generated-centered.png').convert('RGB'));S=np.array(Image.open(ROOT.parent/'northwest/r05_c04/native/s01_01.png').convert('RGB'))
cuts=[512,536,560,584,608,626];canvas=Image.new('RGB',(1320,640),(230,230,230));dr=ImageDraw.Draw(canvas)
profiles=[]
for i,y in enumerate(cuts):
 a=G.copy();a[y:742]=S[y-512:230];a[742:]=S[230:742]
 crop=Image.fromarray(a).crop((600,460,1040,760));canvas.paste(crop,((i%3)*440,(i//3)*320+20));dr.text(((i%3)*440+4,(i//3)*320+3),f'context y{y}, north native y{y+512}',fill=(0,0,0))
 profiles.append({'contextY':y,'northNativeY':y+512,'meanAbsDiffRail':float(np.mean(np.abs(G[y,650:1005].astype(float)-S[y-512,650:1005].astype(float))))})
canvas.save(D/'constant-cut-comparison-native.png');(D/'constant-cut-evaluation.json').write_text(json.dumps(profiles,indent=2),encoding='utf-8')
print(json.dumps(profiles))

from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
a=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v1-guide-native1254.png').convert('RGB'))
b=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v3-bounded-preview-native1254.png').convert('RGB'))
out=[]
for x,c,centers in [(439,'left outside',[394,509,653,832,1032]),(440,'left inside',[394,509,653,832,1032]),(849,'right inside',[382,496,635,807,1002]),(850,'right outside',[382,496,635,807,1002])]:
 v=b[:,x].mean(1); rows=[int(np.argmin(v[y-15:y+16])+y-15) for y in centers];out.append({'x':x,'side':c,'darkestRows':rows})
print(json.dumps(out))


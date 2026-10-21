from pathlib import Path
from PIL import Image,ImageDraw
import json
T=Path(__file__).resolve().parent;d=T/'repair-batches/internal-wall-strip-02';im=Image.open(d/'edit-target.png');dr=ImageDraw.Draw(im)
for b in [(570,280,690,415),(570,520,690,690),(570,775,690,940)]:dr.rectangle(b,outline=(255,20,40),width=2)
im.save(d/'annotation-only.png')
q=T/'repair-batches/internal-wall-strip-01/trials/v01-binary-seam';(q/'producer-review.json').write_text(json.dumps(dict(status='rejected_unadopted',reason='Generated source changes entire beam exposure; narrow exact native selection introduces conspicuous jagged lighting boundary on post/beam, especially middle patch. No pixels adopted.',adoptedPixels=0,actuallyViewed=['beam1-perimeter.png','beam2-perimeter.png','beam3-perimeter.png']),indent=2)+'\n')

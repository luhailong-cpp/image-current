from pathlib import Path
import json
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/internal-glaze-01';q=d/'trials/v01-binary-seam';a=json.loads((d/'derivation.json').read_text());im=Image.open(a['source'])
im.crop((750,830,1050,1250)).save(q/'left-context-before.png');im.crop((770,787,2120,1277)).save(q/'full-context-before.png')

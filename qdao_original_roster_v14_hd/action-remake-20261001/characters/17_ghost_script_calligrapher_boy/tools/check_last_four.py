from pathlib import Path
from PIL import Image
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_review_runtime import edge_counts
B=Path(__file__).resolve().parents[1]
for k in ['run-W-06-v7','run-W-14-v6','run-SE-08-v4','run-SE-16-v4']:
 im=Image.open(B/'staging'/f'{k}.png')
 print(k,edge_counts(im))


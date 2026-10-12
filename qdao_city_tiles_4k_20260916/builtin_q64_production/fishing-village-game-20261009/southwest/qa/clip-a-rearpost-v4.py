import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
Z=Path(__file__).resolve().parents[1];QA=Z/'qa'
paths={'base':QA/'repair-r09_c06-a-complete-upper-posts-source-native-v3.png','gen':Z/'native/r09_c06_repair_a_complete_posts_v3.png','afterv3':QA/'repair-r09_c06-objects-v3-a-full-after-100pct.png'}
for name,p in paths.items():
 out=QA/('repair-r09_c06-a-rear-'+name+'-detail-100pct.png');assert not out.exists();Image.open(p).crop((610,800,820,1230)).save(out)

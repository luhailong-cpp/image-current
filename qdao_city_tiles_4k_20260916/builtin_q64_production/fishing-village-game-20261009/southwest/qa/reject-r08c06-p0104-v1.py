import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
Q=Path(__file__).resolve().parent;Z=Q.parent;p=Z/'native/r08_c06_p01_04_v1.png.generation.json';r=json.loads(p.read_text(encoding='utf-8'));r['status']='rejected';r['rejectionReason']='Reframed/completed lantern and dropped blue awning from protected bottom native strip; background added depth blur.';p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')


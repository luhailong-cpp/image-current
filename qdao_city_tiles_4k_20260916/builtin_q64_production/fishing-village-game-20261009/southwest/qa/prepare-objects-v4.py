import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];QA=Z/'qa'
src=(QA/'repair-compose.py').read_text(encoding='utf-8')
src=src.replace('from PIL import Image','from PIL import Image, ImageDraw')
old='"repairBounds": list(bounds), "margin": margin, "pixels": repair})'
new='"repairBounds": list(bounds), "margin": margin, "clipPolygon": item.get("clipPolygon"), "pixels": repair})'
assert old in src;src=src.replace(old,new)
old='        selected = mask.astype(bool)\n'
new='''        if item.get("clipPolygon"):
            polygon = item["clipPolygon"]
            require(len(polygon) >= 3 and all(len(p) == 2 and all(type(v) is int for v in p) and 0 <= p[0] < NATIVE and 0 <= p[1] < NATIVE for p in polygon), "Invalid object polygon")
            object_mask = Image.new("L", (NATIVE, NATIVE), 0)
            ImageDraw.Draw(object_mask).polygon([tuple(p) for p in polygon], fill=1)
            mask &= np.asarray(object_mask, dtype=np.uint8)
        selected = mask.astype(bool)
'''
assert old in src;src=src.replace(old,new)
src=src.replace('"insideBounds AND x>=L[y] AND x<R[y] AND y>=T[x] AND y<B[x]"','"insideBounds AND x>=L[y] AND x<R[y] AND y>=T[x] AND y<B[x] AND optional object clipPolygon"')
src=src.replace('"interiorWhollyRepair": True','"interiorWhollyRepairBeforeOptionalObjectClip": True, "objectClipApplied": bool(item.get("clipPolygon"))')
p=QA/'repair-compose-object.py';assert not p.exists();p.write_text(src,encoding='utf-8')
m=json.loads((QA/'repair-r09_c06-objects-v3.manifest.json').read_text(encoding='utf-8-sig'));m['outputPrefix']='repair-r09_c06-objects-v4';m['status']='candidate_with_complete_object_qa_pending';m['notes']='v3 preserved. Rear thin post additionally clipped to true visible wood perimeter; foreground tabletop and cross brace excluded. Six approved salvage repairs and red full post unchanged.'
r=next(r for r in m['repairs'] if r['id']=='a-entire-rear-post');r['clipPolygon']=[[651,846],[769,892],[769,1020],[727,1027],[719,1038],[719,1089],[765,1116],[765,1127],[651,1180]]
p=QA/'repair-r09_c06-objects-v4.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print({'manifest':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})

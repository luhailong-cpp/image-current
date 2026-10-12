"""Replay the four independently reviewed native source selections."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Z))
import apply_native_tile_repair as r
Q=Path(__file__).resolve().parent
base=r.read_pixels(Z/'tiles/r03_c04_candidate-v1_4096.png',4096)
final,proof=r.validate_base(Z/'tiles/r03_c04_candidate-v5_4096.png',Z/'tiles/r03_c04_candidate-v5_4096.native-repair.json')
rebuilt=base.copy();selected=np.zeros((4096,4096),dtype=bool);items=[]
for version in range(2,6):
    record=r.read_json(Z/f'tiles/r03_c04_candidate-v{version}_4096.native-repair.json')
    box=record['cropBox'];x0,y0,x1,y1=box
    mask=r.read_mask(Path(record['mask']['path']))==255
    raw=r.read_pixels(Path(record['repairSource']['path']),1254)
    assert not np.any(selected[y0:y1,x0:x1]&mask)
    selected[y0:y1,x0:x1]|=mask
    rebuilt[y0:y1,x0:x1][mask]=raw[mask]
    Image.fromarray(final[y0:y1,x0:x1]).save(Q/f'final_repair_v{version}_100pct.png')
    items.append({'version':version,'raw':record['repairSource']['path'],'rawSha256':record['repairSource']['sha256'],'cropBox':box,'selectedPixelCount':int(mask.sum()),'visualReview':'pass by right_tile_resume and independently by root'})
assert np.array_equal(rebuilt,final)
assert np.array_equal(base[~selected],final[~selected])
edges={name:bool(np.array_equal(a,b)) for name,a,b in [('top',base[0],final[0]),('bottom',base[-1],final[-1]),('left',base[:,0],final[:,0]),('right',base[:,-1],final[:,-1])]}
assert all(edges.values())
Image.fromarray(final).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'PREVIEW_NOT_FOR_GAME_1024.png')
result={'status':'internal_native_qa_pass_external_boundaries_pending','final':r.file_info(Z/'tiles/r03_c04_candidate-v5_4096.png'),'record':r.file_info(Z/'tiles/r03_c04_candidate-v5_4096.native-repair.json'),'exactReplay':True,'unselectedPixelsUnchanged':True,'repairMasksDisjoint':True,'selectedPixelCount':int(selected.sum()),'edgePixelsUnchangedFromV1':edges,'baseNativeQa':{'index':r.file_info(Z/'qa/assembly_r03_c04_candidate-v1_4096/qa_index.json'),'reviewedAtNativeScale':33,'reviewerBreakdown':'right_tile_resume viewed 12 vertical, 8 horizontal, 9 junction crops; root independently viewed all 4 first-row/second-row horizontal crops and 3 second-row vertical strips','review':'architecture, stone fence, vegetation, cylinders and material continuity passed; four paving/wallskirt defects repaired below'},'repairs':items,'provenanceProof':proof,'externalBoundaryVisualAcceptance':False,'formalAcceptedCount':0,'previewNotForGame':True}
(Q/'closure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'selectedPixelCount':result['selectedPixelCount'],'edges':edges,'output':str(Q/'closure.json')}))

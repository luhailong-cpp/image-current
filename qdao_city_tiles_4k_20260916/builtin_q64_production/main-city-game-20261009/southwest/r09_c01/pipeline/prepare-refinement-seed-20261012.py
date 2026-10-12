from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B))
from native_pipeline import Pipeline, sha

tile, patch, attempt, base_attempt, prefix_name=sys.argv[1:]
assert 9<=int(tile[1:3])<=16 and 1<=int(tile[5:7])<=4
row,col=int(patch[1:3]),int(patch[4:6])
p=Pipeline(tile); T=B/tile
selected=p.selected_record(tile,row,col)
native,entry=p.native_record(tile,row,col,selected)
seed=native.copy(); neighbors=[]
left=p.neighbor(row,col,'left'); top=p.neighbor(row,col,'top')
if left:
    seed.paste(left[0],(0,0)); left[1].update(targetBox=[0,0,230,1254],effectiveTargetBox=[0,230 if top else 0,230,1254]); neighbors.append(left[1])
if top:
    seed.paste(top[0],(0,0)); top[1].update(targetBox=[0,0,1254,230],effectiveTargetBox=[0,0,1254,230]); neighbors.append(top[1])
seed_file=T/'pipeline/guides'/f'{patch}.{attempt}.native-continuity-seed.png'
assert not seed_file.exists(); seed_file.parent.mkdir(parents=True,exist_ok=True); seed.save(seed_file)
base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json'
r=json.loads(base.read_text(encoding='utf-8-sig'))
prefix=Path(prefix_name).read_text(encoding='utf-8-sig')
prompt=prefix+'\n\nInput image 1 is a mechanical native continuity seed: current native patch plus the exact selected native 230px top/left strips, pasted without resampling or feathering. Upper strip owns the corner. Preserve these anchor pixels, extend their coherent surfaces into the current interior, and eliminate any x230 or y230 strip division. Images 2, 3 and 4 are the mandatory geometry, clean daylight material and current Daoist Q-style references. Output exactly one native opaque 1254x1254 PNG, no resize, recenter, added scene, UI, people, text, props or watermark. The current camera, projected object silhouettes, scale and all fixed architectural intersections must remain unchanged except the specifically requested seam corrections.\n'
pp=T/'pipeline/prompts'/f'{patch}.{attempt}.prompt.txt'; rp=pp.with_name(f'{patch}.{attempt}.request.json')
assert not pp.exists() and not rp.exists(); pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),references=[p.ref(seed_file,'mechanical native edit seed, selected native with exact unresampled neighbor anchors')]+p.current_refs(),neighborSources=neighbors,cornerTreatment={'priority':'upper','bothSourcesPresent':bool(left and top),'sourceResampling':False},preparedAtUtc=datetime.now(timezone.utc).isoformat(),actualModel=None,actualQuality=None)
r['referenced_image_paths']=[x['file'] for x in r['references']]
r['refinementOf']={'generationRecord':entry['recordFile'],'sha256':entry['recordSha256'],'native':entry['nativeFile'],'nativeSha256':entry['nativeSha256']}
p.stable(); rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
derivation={'seed':str(seed_file),'sha256':sha(seed_file),'base':r['refinementOf'],'nativeNeighborPastes':neighbors,'operation':'exact native copy and top/left strip pastes only','sourceResampling':False,'imageRepainting':False,'gameArt':False}
Path(str(seed_file)+'.derivation.json').write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(rp)

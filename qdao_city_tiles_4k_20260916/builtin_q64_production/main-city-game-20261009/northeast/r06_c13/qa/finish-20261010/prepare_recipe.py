"""Build explicit ordered replay recipe; no production image writes."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
base=read(HERE/'records/base-replay.json');ops=[]
for old in base['operations']:
    op=dict(old);op['id']=Path(op['source']).stem;op['generationRecord']=str(ZONE/'qa/south-join-20261010/repairs/records'/f"{op['id']}.generation.json");ops.append(op)
for filename in ['roof-cross-seam-v1.material-proposal.json','roof-left-upper-v1.object-proposal-v3.json','roof-left-lower-v1.object-proposal-v3.json']:
    p=HERE/'records'/filename;rec=read(p)
    for item in rec['integerTileOperations']:
        if item['tile']!='r06_c13':continue
        ops.append({'id':rec['id'],'source':rec['source'],'sha256':rec['sourceSha256'],'sourceCrop':item['sourceCrop'],'destinationTileXY':item['destinationTileXY'],'mask':rec['mask'],'maskSha256':rec['maskSha256'],'maskCrop':item['maskCrop'],'generationRecord':str(HERE/'records'/f"{rec['id']}.generation.json"),'proposalRecord':str(p)})
spec={'tile':'r06_c13','status':'intermediate-complete-candidate-p43-and-flower-pending','output':str(HERE/'review/roof-integration-intermediate.png'),'operations':ops,'noResize':True,'noImageBlur':True,'formalAcceptedCount':0}
out=HERE/'records/roof-intermediate-replay.json';assert not out.exists();out.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)

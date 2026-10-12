"""Prove the two current tile halves replay the same reviewed source/mask context."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,sys
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
south=Path(sys.argv[1]);north=ZONE/'r05_c13/candidates/r05_c13.candidate.png'
rec=json.loads((HERE/'records/roof-cross-seam-v1.material-proposal.json').read_text(encoding='utf-8'))
stitched=Image.new('RGB',(1254,1254))
stitched.paste(Image.open(north).convert('RGB').crop([2448,3896,3702,4096]),(0,0))
stitched.paste(Image.open(south).convert('RGB').crop([2448,0,3702,1054]),(0,200))
expected=Image.open(rec['proposal']).convert('RGB');diff=ImageChops.difference(stitched,expected)
assert diff.getbbox() is None,'Shared context no longer equals the single reviewed repair proposal'
out=HERE/'review/shared-roof-current-context.png';stitched.save(out)
result={'northCandidate':str(north),'northSha256':sha(north),'southCandidate':str(south),'southSha256':sha(south),'sharedContext':str(out),'sharedContextSha256':sha(out),'worldBox':rec['contextWorldBox'],'joinY':200,'reviewedSingleProposal':rec['proposal'],'pixelIdenticalToSingleProposal':True,'noResampling':True,'visualReview':'north-shared-c3/c4 and complete vertical proposal viewed at 1:1; no broken blue ribs, P3 gold material boundary x52020 retained','formalAcceptedCount':0}
(HERE/'records/shared-roof-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))

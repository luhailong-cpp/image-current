from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
src=ZONE/'qa/r03_c11_cross_03_03_stair_finish_v5-candidate.png'; out=Image.open(src).convert('RGB');qa=ZONE/'qa/r03_c11-round2-final';qa.mkdir(exist_ok=True)
out.resize((1536,1536),Image.Resampling.LANCZOS).save(qa/'preview.png')
for r in range(4):
 for c in range(4):out.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(qa/f'core-{r+1}-{c+1}.png')
for i in range(1,4):
 for j in range(4):
  out.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)).save(qa/f'v{i}-{j+1}.png');out.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)).save(qa/f'h{i}-{j+1}.png')
for r in range(1,4):
 for c in range(1,4):out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(qa/f'cross-{r}-{c}.png')
right=ZONE/'tiles/r03_c12.png';im=Image.open(right).convert('RGB')
for r in range(4):
 strip=Image.new('RGB',(512,1024));strip.paste(out.crop((3840,r*1024,4096,(r+1)*1024)),(0,0));strip.paste(im.crop((0,r*1024,256,(r+1)*1024)),(256,0));strip.save(qa/f'external-right-{r+1}.png')
write(qa/'crop-index.json',{'candidate':src.as_posix(),'sha256':sha(src),'rightNeighbor':right.as_posix(),'rightNeighborSha256':sha(right),'inspectionScale':1,'nativeCropCounts':{'cores':16,'seams':24,'crosses':9,'right4kEdgeSegments':4},'status':'pending','formalAccepted':False,'generatedAtUtc':now()})

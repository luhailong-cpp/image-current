from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def board(name,size,items):
    b=Image.new('RGB',size); rec=[]
    for f,xy in items:
        p=P/f; im=Image.open(p); b.paste(im,xy)
        assert b.crop((xy[0],xy[1],xy[0]+im.width,xy[1]+im.height)).tobytes()==im.tobytes()
        rec.append({'source':str(p),'sha256':sha(p),'destination':xy,'dimensions':list(im.size)})
    dest=P/(name+'.png');b.save(dest)
    return {'file':str(dest),'sha256':sha(dest),'panels':rec,'exactPaste':True,'scale':1}
records=[]
records.append(board('r14-new-vertical-board',(2048,1024),[(f'r14_c12/new-v-r{r}-c{c}.png',(i*512,0)) for i,(r,c) in enumerate([(3,2),(3,3),(4,2),(4,3)])]))
records.append(board('r14-new-horizontal-board',(1024,1024),[(f'r14_c12/new-h-r{r}-c3.png',(0,i*512)) for i,r in enumerate([2,3])]))
records.append(board('r14-new-junction-board',(1024,1024),[(f'r14_c12/new-j-r{r}-c{c}.png',((i%2)*512,(i//2)*512)) for i,(r,c) in enumerate([(2,2),(2,3),(3,2),(3,3)])]))
records.append(board('r13-new-seam-board',(1536,1024),[('r13_c11/p31-p41.png',(0,0)),('r13_c11/p32-p42.png',(0,512)),('r13_c11/p41-p42.png',(1024,0))]))
records.append(board('r12-current-proposal-breakpoints',(1024,1024),[('r12_c13/v02-floor-issue.png',(0,0)),('r12_c13/v03-floor-issue.png',(512,0)),('r12_c13/v02-sail-issue.png',(0,512)),('r12_c13/v03-sail-issue.png',(512,512))]))
(P/'boards.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print([r['file'] for r in records])

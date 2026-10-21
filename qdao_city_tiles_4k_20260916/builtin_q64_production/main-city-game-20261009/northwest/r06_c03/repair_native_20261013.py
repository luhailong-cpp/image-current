from pathlib import Path
import json,hashlib,sys,shutil
from PIL import Image
T=Path(__file__).resolve().parent
B=T/'candidate/r06_c03-candidate-hard-b0c8f7b8ec2f.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name,box):
 d=T/'repair-batches'/name;d.mkdir(parents=True,exist_ok=False)
 assert box[2]-box[0]==1254 and box[3]-box[1]==1254
 cp=T/'current-fullqa-checkpoint-20261013.json';source=Path(json.loads(cp.read_text())['candidate']['file']) if cp.exists() else B
 out=d/'edit-target.png';Image.open(source).crop(box).save(out)
 write(d/'derivation.json',dict(source=str(source),sourceSha256=sha(source),tileCropLTRB=box,worldBox=[8192+box[0],20480+box[1],8192+box[2],20480+box[3]],output=str(out),sha256=sha(out),nativePixelScale=1,sourceResampled=False,sourceRecolored=False))
 print(str(out))
def ingest(name,host,hint):
 d=T/'repair-batches'/name;out=d/'native.png';assert not out.exists();assert Image.open(host).size==(1254,1254)
 shutil.copyfile(host,out)
 write(d/'generation.json',dict(file=str(out),sha256=sha(out),hostOutputPath=host,hostSha256=sha(host),hostBytesIdentical=sha(out)==sha(host),pixels=[1254,1254],entrance='image_gen.imagegen',actualModel=None,actualModelEvidence='Tool did not return model identity.',outputHint=hint,request=str(d/'request.json'),derivation=str(d/'derivation.json'),sourceResampled=False,sourceRecolored=False))
 print(json.dumps(dict(file=str(out),sha256=sha(out))))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2],list(map(int,sys.argv[3:])))
 elif sys.argv[1]=='ingest':ingest(*sys.argv[2:])

from pathlib import Path
import sys,shutil,hashlib,json
from PIL import Image
B=Path(__file__).resolve().parents[1]
tile,patch,attempt,src,rp=sys.argv[1:]
assert tile in {f"r{r:02d}_c06" for r in range(9,17)}
assert len(patch)==6 and patch.startswith("p") and "_" in patch
source=Path(src);receipt=Path(rp);assert source.is_file() and receipt.is_file()
dest=B/tile/"pipeline/returned-native"/f"{patch}.{attempt}.returned.png"
dest.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if dest.exists():assert sha(dest)==sha(source)
else:shutil.copy2(source,dest)
assert sha(dest)==sha(source)
with Image.open(dest) as im:size=list(im.size);mode=im.mode;fmt=im.format
d={"file":str(dest),"sha256":sha(dest),"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"nativePixels":size,"mode":mode,"format":fmt,"sourceResampling":False,"nativePixelsPreserved":True,"formalAccepted":False,"toolReceipt":str(receipt),"toolReceiptSha256":sha(receipt),"visualDisposition":"pending_actual_review"}
p=Path(str(dest)+".preservation.json")
if p.exists():assert json.loads(p.read_text(encoding="utf-8"))==d
else:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"saved":str(dest),"sha256":d["sha256"],"nativePixels":size,"formalAccepted":False}))


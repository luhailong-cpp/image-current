from pathlib import Path
from PIL import Image
import json,hashlib,shutil,datetime,sys
R=Path(__file__).resolve().parent
stem,ver,src=sys.argv[1:4];p=R/'native'/f'{stem}_{ver}.png'
assert not p.exists();shutil.copy2(src,p)
d=json.loads((R/'receipts'/f'{stem}_a01.json').read_text());d.update(file=str(p),sourcePath=src,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),actualNativeDimensions=list(Image.open(p).size),promptFile=str(R/'prompts'/f'{stem}_{ver}.txt'),referenceRecord=str(R/'prompts'/f'{stem}_{ver}.references.json'),savedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),revision=ver)
(R/'receipts'/f'{stem}_{ver}.json').write_text(json.dumps(d,indent=2))
s=R/'selected-revisions.json';sel=json.loads(s.read_text()) if s.exists() else {};sel[stem]=ver;s.write_text(json.dumps(sel,indent=2));print(json.dumps(d))

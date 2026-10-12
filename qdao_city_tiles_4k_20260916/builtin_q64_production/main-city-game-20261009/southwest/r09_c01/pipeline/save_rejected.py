from pathlib import Path
import json,hashlib,shutil,sys
p=Path(sys.argv[1]);d=json.loads(p.read_text(encoding='utf-8-sig'));s=Path(d['sourceOutputPath']);dest=Path(sys.argv[2]);assert not dest.exists();shutil.copy2(s,dest);d.update(sourceOutputSha256=hashlib.sha256(s.read_bytes()).hexdigest(),savedRejectedNative=str(dest));p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

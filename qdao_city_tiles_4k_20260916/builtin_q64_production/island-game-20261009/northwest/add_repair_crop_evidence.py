from pathlib import Path
import hashlib,json
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r03_c03_repair_second_cylinder_a01'; p=Z/'guides'/f'{stem}.input.json'; rec=json.loads(p.read_text(encoding='utf-8'))
base=Z/'tiles/r03_c03_candidate-v1_4096.png'; ass=base.with_suffix('.assembly.json'); crop=Z/'guides'/f'{stem}.native-crop.png'; deriv=Z/'guides'/f'{stem}.native-crop.derivation.json'
d=dict(derivedFrom=dict(path=base.as_posix(),sha256=sha(base),assemblyRecord=dict(path=ass.as_posix(),sha256=sha(ass))),cropBox=rec['tileCropBox'],operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output=dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254]))
assert not deriv.exists();deriv.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec['editTarget']=dict(path=crop.as_posix(),sha256=sha(crop),derivationRecord=dict(path=deriv.as_posix(),sha256=sha(deriv)))
p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

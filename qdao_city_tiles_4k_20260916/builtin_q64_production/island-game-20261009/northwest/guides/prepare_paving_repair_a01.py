from pathlib import Path
from PIL import Image
import hashlib,json
Z=Path(__file__).resolve().parent.parent
S='r03_c03_repair_paving_a01'
BOX=[2760,2720,4014,3974]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Z/'tiles/r03_c03_candidate-v1_4096.png'
assembly=Z/'tiles/r03_c03_candidate-v1_4096.assembly.json'
assert sha(src)=='d6d6add7839ca14d8b001a38ef2cb6a6f17663d6b8f8544f1bd363029b34a4ca'
out=Z/'guides'/f'{S}.native-crop.png';assert not out.exists()
full=Image.open(src);assert full.size==(4096,4096)
crop=full.crop(BOX);assert crop.size==(1254,1254);crop.save(out)
der=Z/'guides'/f'{S}.native-crop.derivation.json'
record=dict(derivedFrom=dict(path=src.as_posix(),sha256=sha(src),assemblyRecord=dict(path=assembly.as_posix(),sha256=sha(assembly))),cropBox=BOX,operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output=dict(path=out.as_posix(),sha256=sha(out),nativeSize=[1254,1254]))
write(der,record)
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
inputs=[dict(path=out.as_posix(),sha256=sha(out),nativeSize=[1254,1254],role='edit target: exact unresampled1254 crop of fully traced native4096 candidate-v1; actual visible paving seam failures',derivedFrom=dict(path=src.as_posix(),sha256=sha(src),assemblyRecord=assembly.as_posix(),assemblySha256=sha(assembly),cropBox=BOX,resized=False))]+refs
rec=dict(stem=S,tileId='r03_c03',tileCropBox=BOX,globalBox=[v+8192 for v in BOX],nativeSize=[1254,1254],inputs=inputs,operation='exact unresampled crop of assembled native art for builtin precise local edit',layoutPixelsForbiddenInFinal=True,isFinalArt=False,editTarget=dict(path=out.as_posix(),sha256=sha(out),derivationRecord=dict(path=der.as_posix(),sha256=sha(der))))
write(Z/'guides'/f'{S}.input.json',rec)
write(Z/'guides'/f'{S}.references.json',dict(inputs=inputs))
print(json.dumps(dict(crop=out.as_posix(),sha256=sha(out),globalBox=rec['globalBox'],sourceSha256=sha(src))))

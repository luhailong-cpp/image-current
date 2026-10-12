from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian')
p=root/'provenance/cast/E'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
rows=[]
for i in range(1,17):
    n=f'{i:02}';recpath=p/f'{n}.generation.json';rec=json.loads(recpath.read_text(encoding='utf8'))
    file=root/'runtime/cast/E'/f'{n}.png';im=Image.open(file)
    assert Path(rec['file']).resolve()==file.resolve()
    assert sha(file)==rec['sha256'];assert im.size==(1024,1024) and im.mode=='RGBA'
    a=im.getchannel('A');assert a.getextrema()==(0,255)
    assert Path(rec['prompt']).is_file() and Path(rec['evidence']['receipt']).is_file()
    native=Path(rec['derivedFrom']['nativeFile']);assert sha(native)==rec['derivedFrom']['sha256']
    for ref in rec['references']:
        f=Path(ref['path']);assert f.exists()
        if 'sha256' in ref: assert sha(f)==ref['sha256'],str(f)
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    if 9<=i<=13:
        assert Path(rec['editedFrom']['generationRecord']).exists()
        assert sha(Path(rec['editedFrom']['file']))==rec['editedFrom']['sha256']
        receipt=json.loads(Path(rec['evidence']['receipt']).read_text(encoding='utf8'))
        assert 'output_hint' in receipt and 'exec-' in receipt['output_hint']
    rows.append({'frame':i,'file':str(file),'sha256':sha(file),'nativeSHA':sha(native),'record':str(recpath),'recordMatchesRuntime':True,'sourceReferencesHashVerified':True,'size':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema())})
assert len({r['sha256'] for r in rows})==16
for page in range(2):
    sheet=Image.new('RGB',(1600,860),(51,58,61));d=ImageDraw.Draw(sheet)
    for k in range(8):
        n=page*8+k+1;im=Image.open(root/'runtime/cast/E'/f'{n:02}.png').resize((400,400),Image.Resampling.LANCZOS)
        x=(k%4)*400;y=(k//4)*430
        sheet.paste(im,(x,y+25),im);d.text((x+10,y+5),f'CAST E {n:02}',fill=(245,245,220))
    sheet.save(p/f'inspection-{page+1}.jpg',quality=95)
report={'reverifiedOn':'2026-10-08','timezone':'America/New_York','frameCount':16,'uniqueSHA256Count':16,'technicalChecks':'passed','newGenerationCalls':0,'corrected09Through13':'Each current main generation record has successful builtin output receipt and matches its runtime PNG; native and edit-target hashes verified.','frame12FailureMeaning':'Historical failed first repair attempt. Subsequent successful repair receipt12.receipt.json and current12.generation.json prove completion.','frames':rows,'visualReview':'pending final reinspection in this turn','dynamicPreview':'root combined review','clientIntegration':'not tested'}
(p/'revalidation-20261008.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))

"""Record source provenance without modifying image pixels."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('file'); p.add_argument('receipt'); p.add_argument('prompt'); a=p.parse_args()
    img=(ROOT/a.file).resolve(); rec=(ROOT/a.receipt).resolve(); prompt=(ROOT/a.prompt).resolve()
    assert all(x.is_relative_to(ROOT) for x in (img,rec,prompt))
    receipt=json.loads(rec.read_text(encoding='utf-8-sig'))
    im=Image.open(img); im.load()
    refs=[]
    for i,path in enumerate(receipt['submittedParameters']['referenced_image_paths']):
        rp=Path(path); roles=receipt.get('referenceRoles',[]); role=roles[i] if i<len(roles) else ('edit target and registration','identity reference','main style reference')[min(i,2)]
        ref={'file':str(rp),'sha256':sha(rp),'role':role}
        input_record=rp.with_name(rp.name+'.generation.json')
        if rp.resolve().is_relative_to(ROOT) and input_record.is_file():
            prior=ROOT/'sources/reference-history'/(ref['sha256']+'.generation.json')
            prior.parent.mkdir(parents=True,exist_ok=True)
            if not prior.exists():prior.write_bytes(input_record.read_bytes())
            assert json.loads(prior.read_text(encoding='utf-8-sig'))['sha256']==ref['sha256']
            ref.update(generationRecord=prior.relative_to(ROOT).as_posix(),generationRecordSha256=sha(prior))
        refs.append(ref)
    data={'schemaVersion':1,'file':a.file,'sha256':sha(img),'generatedAt':receipt['completedAt'],'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'nativeFrameSize':list(im.size),'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':receipt['submittedParameters']['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号/质量；无选择器。','evidence':{'receipt':a.receipt,'receiptSha256':sha(rec)},'prompt':a.prompt,'references':refs,'alphaExtrema':list(im.getchannel('A').getextrema()),'alphaBBox':list(im.getchannel('A').getbbox()),'visualReview':{'status':'pending','clientRuntimeVerified':False}}
    out=img.with_name(img.name+'.generation.json');out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'file':a.file,'sha256':data['sha256'],'nativeFrameSize':data['nativeFrameSize']}))
if __name__=='__main__': main()

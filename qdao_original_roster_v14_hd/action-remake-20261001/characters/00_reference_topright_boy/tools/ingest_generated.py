"""Copy a successful built-in output and record verified native file metadata."""
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--request',required=True)
    ap.add_argument('--receipt',required=True)
    a=ap.parse_args()
    src=Path(a.source); dst=(ROOT/a.output).resolve()
    if ROOT not in dst.parents: raise ValueError('Output must be inside actor directory')
    req_path=(ROOT/a.request).resolve(); rec_path=(ROOT/a.receipt).resolve()
    req=json.loads(req_path.read_text(encoding='utf-8-sig')); rec=json.loads(rec_path.read_text(encoding='utf-8-sig'))
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and sha(dst)!=sha(src): raise FileExistsError(dst)
    if not dst.exists(): shutil.copy2(src,dst)
    with Image.open(dst) as im: size=im.size; mode=im.mode; fmt=im.format
    meta={'file':dst.relative_to(ROOT).as_posix(),'sha256':sha(dst),'generatedAt':rec.get('completedAt'), 'recordedAt':datetime.now(timezone(timedelta(hours=-4))).isoformat(),'timezone':'America/New_York','nativeSize':list(size),'width':size[0],'height':size[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req.get('submittedParameters',{}),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；内置工具没有model/quality选择器，回执未披露实际版本或质量。','prompt':req.get('prompt'),'references':req.get('references'),'evidence':{'request':a.request,'requestSha256':sha(req_path),'receipt':a.receipt,'receiptSha256':sha(rec_path),'hostOutput':str(src)},'status':'generated_candidate_pending_sequence_review'}
    save(Path(str(dst)+'.generation.json'),meta)
    print(json.dumps({'file':meta['file'],'sha256':meta['sha256'],'size':size,'mode':mode},ensure_ascii=False))
if __name__=='__main__':main()

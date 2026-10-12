"""Record native built-in output and export by full-canvas resize only."""
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CONFIG=Path('D:/work/image/config/image-generation.json')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--key',required=True); p.add_argument('--prompt',required=True); p.add_argument('--refs',nargs='+',required=True); p.add_argument('--receipt',required=True); a=p.parse_args()
    key=Path(a.key); source=Path(a.source); native=ROOT/'source'/key.with_suffix('.png'); out=ROOT/'runtime'/key.with_suffix('.png')
    for f in (native,out): f.parent.mkdir(parents=True,exist_ok=True)
    if out.exists(): raise SystemExit('Refusing overwrite; use explicit retry key then review')
    shutil.copy2(source,native); im=Image.open(native); native_sha=sha(native)
    im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS).save(out)
    config=json.loads(CONFIG.read_text(encoding='utf-8-sig'))
    record={'schemaVersion':1,'file':str(out.relative_to(ROOT)).replace('\\','/'),'sha256':sha(out),'generatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未开放model/quality选择器且未披露可核实返回值','prompt':a.prompt,'references':[{'path':x,'role':'identity and pose anchor' if 'design/' in x else ('principal style reference' if 'attribute-panels' in x else 'original identity')} for x in a.refs],'evidence':{'toolOutputHint':a.receipt,'hostOutputPath':str(source)},'derivedFrom':{'file':str(native.relative_to(ROOT)).replace('\\','/'),'sha256':native_sha,'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'generationRecord':str((out.with_suffix('.png.generation.json')).relative_to(ROOT)).replace('\\','/'),'retained':'working native until export QA complete'},'operation':{'type':'full-canvas-resize','fromSize':[im.width,im.height],'toSize':[1024,1024],'resample':'Lanczos','translation':[0,0],'perFrameAlignment':False,'alpha':'preserved via RGBA resize'},'visualStatus':'pending-review','clientStatus':'not-integrated'}
    native_record=dict(record)
    native_record.update(file=str(native.relative_to(ROOT)).replace('\\','/'),sha256=native_sha,width=im.width,height=im.height,mode=im.mode)
    native_record.pop('derivedFrom',None); native_record.pop('operation',None)
    native_record_path=native.with_suffix('.png.generation.json')
    native_record_path.write_text(json.dumps(native_record,ensure_ascii=False,indent=2),encoding='utf-8')
    record['derivedFrom']['generationRecord']=str(native_record_path.relative_to(ROOT)).replace('\\','/')
    out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(out),'nativeSha256':native_sha,'sha256':record['sha256'],'nativeSize':[im.width,im.height]}))
if __name__=='__main__': main()

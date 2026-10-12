"""Copy a native built-in result and preserve its per-frame provenance; no drawing."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ingest(action, direction, number, source, receipt):
    nn=f'{number:02}'
    dest=ROOT/'work'/action/direction/(nn+'.png')
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest)
    info=Image.open(dest)
    raw=json.loads(Path(receipt).read_text(encoding='utf-8'))
    record={
      'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),
      'generatedAt':raw['completedAt'],'startedAt':raw['startedAt'],
      'width':info.width,'height':info.height,'format':info.format,'mode':info.mode,
      'tool':'image_gen.imagegen','route':'builtin',
      'configSnapshot':json.loads((ROOT/'provenance/config-snapshot.json').read_text(encoding='utf-8-sig')),
      'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':raw['references']},
      'actualModel':None,'actualQuality':None,
      'unverifiedReason':'宿主管理；工具无 model/quality 选择器，返回结果未披露实际模型或质量。',
      'prompt':f'prompts/{action}/{direction}/{nn}.txt',
      'references':[{'path':p,'role':(['原有E身份与解剖','原有W身份与解剖','主要画法材质完成度'][i] if i<3 else '本只动作连续性或定点修复参考'),'sha256':sha(Path(p))} for i,p in enumerate(raw['references'])],
      'evidence':{'receipt':str(Path(receipt).relative_to(ROOT)).replace('\\','/'),'outputHint':raw['output_hint'],'hostSourcePath':str(source)},
      'visualStatus':'pending-final-sequence-review'
    }
    out=ROOT/'provenance'/action/direction/(nn+'.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'saved':str(dest),'size':info.size,'mode':info.mode,'alphaExtrema':info.getchannel('A').getextrema() if info.mode=='RGBA' else None,'sha256':record['sha256']}))
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('action');p.add_argument('direction');p.add_argument('number',type=int);p.add_argument('source');p.add_argument('receipt');a=p.parse_args()
    ingest(a.action,a.direction,a.number,Path(a.source),Path(a.receipt))

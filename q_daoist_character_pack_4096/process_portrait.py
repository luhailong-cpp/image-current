"""Deterministic export of one image_gen portrait; never draws or generates art.

Raw candidates stay outside the deliverable. Keep prompt and processing provenance.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from PIL import Image

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--id', required=True)
    parser.add_argument('--processor', type=Path, default=Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py')
    args = parser.parse_args()
    if not args.id.replace('_', '').isalnum():
        parser.error('Use the existing portrait stem only')
    target = ROOT / f'{args.id}.png'
    prompt = ROOT / 'prompts' / f'{args.id}.prompt.txt'
    work = ROOT / '.work' / args.id
    work.mkdir(parents=True, exist_ok=True)
    with Image.open(args.raw) as im:
        native_size = list(im.size)
    subprocess.run([sys.executable,str(args.processor),'process','--input',str(args.raw),
        '--target','asset','--mode','single','--rows','1','--cols','1',
        '--cell-size','1254','--fit-scale','0.88','--align','feet','--shared-scale',
        '--component-mode','all','--min-component-area','16','--strict-qc',
        '--threshold','130','--edge-threshold','170','--prompt-file',str(prompt),
        '--output-dir',str(work)],check=True)
    native = Image.open(work/'sheet-transparent.png').convert('RGBA')
    final = native.resize((4096,4096),Image.Resampling.LANCZOS)
    final.save(target,optimize=True)
    alpha = final.getchannel('A')
    bounds = list(alpha.getbbox())
    assert alpha.getextrema() == (0,255)
    assert min(bounds[0],bounds[1],4096-bounds[2],4096-bounds[3]) > 16
    qa = json.loads((work/'pipeline-meta.json').read_text(encoding='utf-8'))
    record = {'file':target.name,'generator':'built-in image_gen','generation_file':args.raw.name,
        'raw_sha256':hashlib.sha256(args.raw.read_bytes()).hexdigest(),
        'native_generation_size':native_size,'export_size':[4096,4096],
        'native_4096_generation':False,'export_method':'skill chroma cleanup, fit/feet alignment, RGBA LANCZOS export',
        'prompt':prompt.relative_to(ROOT).as_posix(),'reference_delivery':'in-memory board via conversation image',
        'reference_baseline':'60134a6','alpha_range':[0,255],'subject_bounds':bounds,
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'processor_qc':qa.get('processing',qa),
        'art_only_not_engine_integrated':True}
    (ROOT/'records').mkdir(exist_ok=True)
    (ROOT/'records'/f'{args.id}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:record[k] for k in ('file','native_generation_size','export_size','alpha_range','subject_bounds')},ensure_ascii=False))

if __name__ == '__main__':
    main()

"""Clear only strongly saturated residual key pixels; keep valid violet paint."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ids',nargs='+')
    args=parser.parse_args()
    for stem in args.ids:
        if not stem.replace('_','').isalnum(): parser.error('Use existing portrait stems')
        path=ROOT/f'{stem}.png'; record_path=ROOT/'records'/f'{stem}.json'
        record=json.loads(record_path.read_text(encoding='utf8'))
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as im: pixels=np.array(im.convert('RGBA'))
        mask=(pixels[:,:,0]>200)&(pixels[:,:,1]<100)&(pixels[:,:,2]>200)&(pixels[:,:,3]>0)
        count=int(mask.sum())
        if count:
            pixels[mask]=[0,0,0,0]
            Image.fromarray(pixels).save(path,optimize=True)
        with Image.open(path) as final:
            assert final.size==(4096,4096) and final.mode=='RGBA'
            assert final.getchannel('A').getextrema()==(0,255)
            record['subject_bounds']=list(final.getchannel('A').getbbox())
        record['strong_chroma_cleanup']={'script':'clean_strong_chroma.py',
            'predicate':'R>200 and G<100 and B>200 and A>0','affected_pixels':count,
            'sha256_before':before,'purpose':'remove residual key-color specks only, retaining legitimate violet material'}
        record['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'file':path.name,'removed_key_pixels':count}))

if __name__=='__main__': main()

from pathlib import Path
import importlib.util,json,sys
from PIL import Image
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v3.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def qa(tile,patch,file):
    assert tile in ('r02_c05','r01_c05')
    p=m.spec(tile,patch);box=p['coreWorldBox'];im=Image.open(file).convert('RGB');out=[]
    sr,sc=p['subrow'],p['subcolumn']
    for edge in ('south','west'):
        dep=p['southContinuationDependency'] if edge=='south' else p['westContinuationDependency']
        n=m.selected(dep['tile']).get(dep['patch'])
        if n:
            nx=n['coordinates']['coreWorldBox'];ni=Image.open(n['file']).convert('RGB').crop((115,115,1139,1139))
        elif edge=='south' and dep['tile']=='r03_c05':
            ns=next(a for a in m.read(m.BOUNDARIES)['sources'] if a['tile']==dep['tile'] and a['role']=='canonical_adopted_candidate_north_edge')
            nx=ns['worldBox'];ni=Image.open(ns['file']).convert('RGB')
        else:continue
        if edge=='south':
            c=Image.new('RGB',(1024,320));c.paste(im.crop((115,979,1139,1139)),(0,0));x=box[0]-nx[0];c.paste(ni.crop((x,0,x+1024,160)),(0,160))
        else:
            c=Image.new('RGB',(320,1024));c.paste(ni.crop((864,0,1024,1024)),(0,0));c.paste(im.crop((115,115,275,1139)),(160,0))
        dest=m.next_path(B/tile/'reviews',Path(file).stem+'-'+edge+'-native100','.png');c.save(dest);out.append(str(dest))
    print(json.dumps(out))
if __name__=='__main__':qa(*sys.argv[1:])

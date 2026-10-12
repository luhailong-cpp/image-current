from pathlib import Path
import importlib.util,json,sys
from PIL import Image
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def qa(tile,patch,file):
    assert tile=='r02_c04'
    p=m.spec(tile,patch);box=p['coreWorldBox'];im=Image.open(file).convert('RGB').crop((115,115,1139,1139));out=[]
    for owned in sorted(m.TILES):
        for n in m.selected(owned).values():
            nx=n['coordinates']['coreWorldBox']; edge=None
            if nx[0]==box[0] and nx[1]==box[3]:edge='south'
            elif nx[0]==box[2] and nx[1]==box[1]:edge='east'
            elif nx[2]==box[0] and nx[1]==box[1]:edge='west'
            elif nx[0]==box[0] and nx[3]==box[1]:edge='north'
            if not edge:continue
            ni=Image.open(n['file']).convert('RGB').crop((115,115,1139,1139))
            if edge=='south':c=Image.new('RGB',(1024,320));c.paste(im.crop((0,864,1024,1024)),(0,0));c.paste(ni.crop((0,0,1024,160)),(0,160))
            elif edge=='north':c=Image.new('RGB',(1024,320));c.paste(ni.crop((0,864,1024,1024)),(0,0));c.paste(im.crop((0,0,1024,160)),(0,160))
            elif edge=='east':c=Image.new('RGB',(320,1024));c.paste(im.crop((864,0,1024,1024)),(0,0));c.paste(ni.crop((0,0,160,1024)),(160,0))
            else:c=Image.new('RGB',(320,1024));c.paste(ni.crop((864,0,1024,1024)),(0,0));c.paste(im.crop((0,0,160,1024)),(160,0))
            dest=m.next_path(B/tile/'qa',Path(file).stem+'-'+edge+'-native100','.png');c.save(dest);out.append({'edge':edge,'file':str(dest),'neighbor':n['file'],'neighborSHA256':n['sha256'],'sourceSHA256':m.sha(file)})
    manifest=m.next_path(B/tile/'qa',Path(file).stem+'-evidence');m.write_new(manifest,{'source':file,'evidence':out,'visualVerdict':'PENDING','formalAccepted':False});print(json.dumps(out))
if __name__=='__main__':qa(*sys.argv[1:])

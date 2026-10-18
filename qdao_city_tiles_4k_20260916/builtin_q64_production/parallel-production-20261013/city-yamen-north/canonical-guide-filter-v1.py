from pathlib import Path
from PIL import Image
import json,sys,importlib.util
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
q=m.read(sys.argv[1]);w=q['coordinates']['worldBoxWithHalo'];im=Image.open(q['guide']['layout']).convert('RGB');sz=im.size
im=im.transform((1254,1254),Image.Transform.EXTENT,(w[0]*sz[0]/65536,w[1]*sz[1]/65536,w[2]*sz[0]/65536,w[3]*sz[1]/65536),Image.Resampling.BICUBIC)
kept=[];excluded=[]
for item in q['guide']['nativeContextPastes']:
 if item['source']['role']=='current_selected_south_halo_context':
  excluded.append(item);continue
 assert m.sha(item['source']['file'])==item['source']['sha256']
 im.paste(Image.open(item['source']['file']).convert('RGB').crop(item['sourceCropLTRB']),tuple(item['guidePasteXY']));kept.append(item)
dest=m.next_path(B/'requests'/q['tile'],q['patch']+'-canonical-only-guide','.png');im.save(dest)
q['guide'].update(file=str(dest),sha256=m.sha(dest),nativeContextPastes=kept,excludedUnreliableLegacyHalo=excluded,correction='Only adopted delivery core pixels are authoritative across external boundary; old derived halo outside delivered tile core is not a fixed native constraint.')
q['referenced_image_paths'][0]=str(dest)
out=m.next_path(B/'requests'/q['tile'],q['patch']+'-canonical-only-request');m.write_new(out,q);print(json.dumps({'request':str(out),'guide':str(dest)}))


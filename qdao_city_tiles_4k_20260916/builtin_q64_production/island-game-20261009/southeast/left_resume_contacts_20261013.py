from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
import sys
folder=ROOT/'qa'/sys.argv[1]
m=read(folder/'seams-junctions-external.json')
groups=[('h',[x for x in m['entries'] if x['id'].startswith('h')]),('v',[x for x in m['entries'] if x['id'].startswith('v')]),('j',[x for x in m['entries'] if x['id'].startswith('j')]),('north',[x for x in m['entries'] if x['id'].startswith('north')]),('east',[x for x in m['entries'] if x['id'].startswith('east')])]
for name,entries in groups:
 for offset in range(0,len(entries),4):
  chunk=entries[offset:offset+4]
  w,h=Image.open(chunk[0]['file']).size
  im=Image.new('RGB',(w*2,h*((len(chunk)+1)//2)))
  for i,e in enumerate(chunk):
   assert sha(Path(e['file']))==e['sha256'];im.paste(Image.open(e['file']),((i%2)*w,(i//2)*h))
  out=folder/f'contact-{name}-{offset//4+1}.png';assert not out.exists();im.save(out)
print(str(folder))

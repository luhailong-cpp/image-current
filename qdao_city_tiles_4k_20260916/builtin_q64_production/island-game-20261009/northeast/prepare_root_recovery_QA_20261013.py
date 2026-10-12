from native_work import *
old=read(ZONE/'qa/r03_c10-native-v1-20261012-review.json')
newdir=ZONE/'qa/r03_c10-native-v2-20261013-final'
oldby={Path(e['file']).name:e for e in old['inspectedCrops']}
entries=[]
for p in sorted(newdir.glob('*.png')):
 e=oldby[p.name];same=sha(p)==e['sha256']; inherited=same and e['status'].startswith('passed')
 entries.append({'file':p.as_posix(),'sha256':sha(p),'status':'passed_inherited_identical_hash' if inherited else 'pending_visual_review','priorEvidence':e['file'],'priorStatus':e['status'],'inspectionScale':1,'resized':False})
qdir=ZONE/'qa/r03_c10-r03_c11-boundary-20261013';qdir.mkdir(exist_ok=False)
lp=ZONE/'tiles/r03_c10-native-v2-20261013.png';rp=Path(read(ZONE/'selection-r03_c11.json').get('candidatePath',ZONE/'tiles/r03_c11.png'))
li=Image.open(lp);ri=Image.open(rp)
b=[]
for j in range(4):
 im=Image.new('RGB',(512,1024));im.paste(li.crop((3840,j*1024,4096,(j+1)*1024)),(0,0));im.paste(ri.crop((0,j*1024,256,(j+1)*1024)),(256,0))
 p=qdir/f'segment-{j+1}-100pct.png';im.save(p);b.append({'file':p.as_posix(),'sha256':sha(p),'status':'pending_visual_review','inspectionScale':1,'resized':False})
out={'entries':entries,'inherited':sum(e['status'].startswith('passed') for e in entries),'boundary':b,'boundarySources':[{'file':str(lp),'sha256':sha(lp)},{'file':str(rp),'sha256':sha(rp)}]}
write(ZONE/'qa/root-recovery-QA-20261013.json',out)
print(json.dumps({'inherited':out['inherited'],'changed':[e['file'] for e in entries if e['status']=='pending_visual_review'],'boundary':[e['file'] for e in b]}))

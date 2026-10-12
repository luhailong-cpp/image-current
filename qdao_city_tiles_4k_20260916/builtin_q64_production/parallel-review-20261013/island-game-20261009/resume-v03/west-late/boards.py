exec((__import__('pathlib').Path(__file__).parent/'prepare.py').read_text(encoding='utf-8').split('snapshot=freeze')[0])
data=read(OUT/'prepared.json');current=read(OUT/'snapshots/current-adopted-20261012.json');adopted={x['tileId']:x for x in current['tiles']}
tiles={x['tileId']:x for x in data['tiles']}
prior=read(REVIEW/'resume-v03/west/summary.json'); old={t['tileId']:t for t in prior['tiles']}
def addcrop(tid,name,im,kind,**extra):
 p=OUT/'crops'/f'{tid}-{name}.png';im.save(p)
 row={'tileId':tid,'name':name,'kind':kind,'path':str(p),'dimensions':list(im.size),'sha256':sha(p),'pixelSha256':hashlib.sha256(im.tobytes()).hexdigest(),'visualStatus':'pending'}|extra
 data['crops'].append(row);return row
data['neighborChecks']=[]
for tid,side,other in [('r05_c02','north','r04_c02'),('r05_c02','east','r05_c03'),('r07_c03','north','r06_c03')]:
 im=Image.open(tiles[tid]['file']).convert('RGB'); before=Image.open(tiles[tid]['baselineFile']).convert('RGB');ni=Image.open(adopted[other]['image']['path']).convert('RGB');
 neighborHash=sha(adopted[other]['image']['path']);same=neighborHash==old[other]['sha256']
 data['sourceImages'].append({'path':adopted[other]['image']['path'],'sha256':neighborHash,'dimensions':list(ni.size)})
 for s in range(4):
  box=(s*1024,0,(s+1)*1024,256) if side=='north' else (3840,s*1024,4096,(s+1)*1024)
  changed=not np.array_equal(np.asarray(before.crop(box)),np.asarray(im.crop(box)))
  entry={'tileId':tid,'side':side,'neighbor':other,'segment':s+1,'tileStripChanged':changed,'neighborSourceUnchanged':same,'reusable':not changed and same}
  if changed or not same:
   joined=Image.new('RGB',(1024,512) if side=='north' else (512,1024))
   if side=='north': joined.paste(ni.crop((s*1024,3840,(s+1)*1024,4096)),(0,0));joined.paste(im.crop(box),(0,256))
   else:joined.paste(im.crop(box),(0,0));joined.paste(ni.crop((0,s*1024,256,(s+1)*1024)),(256,0))
   crop=addcrop(tid,f'neighbor-{side}-{other}-seg{s+1}',joined,'neighbor-seam',neighbor=other,segment=s+1,orientation='h' if side=='north' else 'v'); entry['crop']=crop['path']
  data['neighborChecks'].append(entry)
# Preserve exact lower halves of the already frozen partial r07_c04 edge crops.
for seg,num in [(2,1),(3,2)]:
 tid='r06_c04';p=REVIEW/f'resume-v03/west/edges/{num:03d}-r06_c04-s4{seg}--r07_c04-s1{seg}.png';prev=Image.open(p).convert('RGB');im=Image.open(tiles[tid]['file']).convert('RGB');before=Image.open(tiles[tid]['baselineFile']).convert('RGB');w,h=prev.size;half=h//2
 box=((seg-1)*1024,4096-half,seg*1024,4096); oldtop=before.crop(box)
 assert prev.size==(1024,512)
 same=np.array_equal(np.asarray(prev.crop((0,0,1024,256))),np.asarray(oldtop))
 joined=prev.copy();joined.paste(im.crop(box),(0,0))
 c=addcrop(tid,f'neighbor-south-r07_c04-seg{seg}',joined,'neighbor-seam',neighbor='r07_c04',segment=seg,orientation='h',priorCrop=str(p),priorCropSha256=sha(p),priorTopExactlyMatchesBaseline=same,retainedLowerHalfPixelSha256=hashlib.sha256(prev.crop((0,256,1024,512)).tobytes()).hexdigest())
 data['neighborChecks'].append(c)
boards=[]
for kind in ['h','v']:
 crops=[c for c in data['crops'] if c['kind'] in ['internal-seam','neighbor-seam'] and c['dimensions']==([1024,512] if kind=='h' else [512,1024])]
 for i in range(0,len(crops),8):
  group=crops[i:i+8];bw,bh=(2048,2048);board=Image.new('RGB',(bw,bh),(64,64,64));parts=[]
  for j,c in enumerate(group):
   pos=((j%2)*1024,(j//2)*512) if kind=='h' else ((j%4)*512,(j//4)*1024)
   board.paste(Image.open(c['path']),pos);parts.append({'index':j,'position':pos,'path':c['path'],'tileId':c['tileId'],'name':c['name']})
  p=OUT/f'board-{kind}-{i//8+1:02d}-100pct.png';board.save(p);boards.append({'path':str(p),'parts':parts,'pixelsNotResized':True,'visualStatus':'pending'})
data['boards']=boards;write(OUT/'prepared.json',data)
print(json.dumps({'boards':boards,'repairContexts':[c['path'] for c in data['crops'] if c['kind']=='repair-context'],'neighborChecks':data['neighborChecks']},ensure_ascii=False,indent=2))

from production import *
D=W/sys.argv[1];Q=D/'qa';Q.mkdir(exist_ok=True)
m=read(D/'r02_c02.assembly.json');tile=Image.open(m['candidate']['file']);a=np.asarray(tile);pair=Image.open(D/'full-context.png');records=[]
def crop(n,b,im=tile,role='native final candidate crop'):
 p=Q/(n+'.100pct.png');assert not p.exists();im.crop(b).save(p);records.append({'id':n,'file':str(p),'sha256':sha(p),'crop':b,'role':role,'nativeScale':1,'status':'prepared-unreviewed'});return Image.open(p)
for r in range(4):
 for c in range(4):crop(f'core-{r+1}-{c+1}',[c*1024,r*1024,(c+1)*1024,(r+1)*1024])
for r in range(4):
 sheet=Image.new('RGB',(900,1024))
 for c in range(1,4):sheet.paste(crop(f'v-seam-{r+1}-{c}',[c*1024-150,r*1024,c*1024+150,(r+1)*1024]),((c-1)*300,0))
 p=Q/f'v-contact-{r+1}.100pct.png';sheet.save(p);records.append({'id':f'v-contact-{r+1}','file':str(p),'sha256':sha(p),'contains':[f'v-seam-{r+1}-{c}' for c in range(1,4)],'nativeScale':1,'status':'prepared-unreviewed'})
for r in range(1,4):
 sheet=Image.new('RGB',(1024,1200))
 for c in range(4):sheet.paste(crop(f'h-seam-{r}-{c+1}',[c*1024,r*1024-150,(c+1)*1024,r*1024+150]),(0,c*300))
 p=Q/f'h-contact-{r}.100pct.png';sheet.save(p);records.append({'id':f'h-contact-{r}','file':str(p),'sha256':sha(p),'contains':[f'h-seam-{r}-{c}' for c in range(1,5)],'nativeScale':1,'status':'prepared-unreviewed'})
sheet=Image.new('RGB',(1200,1200))
for r in range(1,4):
 for c in range(1,4):sheet.paste(crop(f'junction-{r}-{c}',[c*1024-200,r*1024-200,c*1024+200,r*1024+200]),((c-1)*400,(r-1)*400))
p=Q/'junction-contact.100pct.png';sheet.save(p);records.append({'id':'junction-contact','file':str(p),'sha256':sha(p),'contains':[f'junction-{r}-{c}' for r in range(1,4) for c in range(1,4)],'nativeScale':1,'status':'prepared-unreviewed'})
for j in range(4):
 crop(f'east-{j+1}',[3911,115+j*1024,4511,115+(j+1)*1024],pair,'new tile with fixed adopted east neighbor; 300 pixels each side')
 crop(f'south-{j+1}',[115+j*1024,3911,115+(j+1)*1024,4511],pair,'new tile with fixed adopted south neighbor; 300 pixels each side')
 crop(f'north-own-{j+1}',[115+j*1024,115,115+(j+1)*1024,715],pair,'own north edge only; external neighbor unavailable')
 crop(f'west-own-{j+1}',[115,115+j*1024,715,115+(j+1)*1024],pair,'own west edge only; external neighbor unavailable')
crop('southeast-four-tile-junction',[3911,3911,4511,4511],pair,'new tile plus three fixed adopted neighbors')
preview=tile.copy();preview.thumbnail((1536,1536),Image.Resampling.LANCZOS);preview.save(Q/'overview.preview-only.png')
write(D/'qa-prepared.json',{'candidate':m['candidate'],'assembly':{'file':str(D/'r02_c02.assembly.json'),'sha256':sha(D/'r02_c02.assembly.json')},'records':records,'requiredCounts':{'core':16,'verticalSeam':12,'horizontalSeam':12,'junction':9},'status':'prepared-unreviewed','externalPending':['r01_c02 north','r02_c01 west']})
print(json.dumps({'qa':str(Q),'required':{'cores':16,'seams':24,'junctions':9},'status':'prepared-unreviewed'}))

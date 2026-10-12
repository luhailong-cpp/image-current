from production import *
T=W/'native-cut-trials';T.mkdir(exist_ok=True)
def join(a,ai,b,bi,k):return np.concatenate([a[:,:-230],a[:,-230:][:,:k],b[:,k:]],axis=1),np.concatenate([ai[:,:-230],ai[:,-230:][:,:k],bi[:,k:]],axis=1)
for k in [0,115,229]:
 rows=[];rowids=[]
 for r in range(1,5):
  for c in range(1,5):
   im=np.asarray(Image.open(native(r,c)).convert('RGB'));ii=np.full(im.shape[:2],(r-1)*4+c,np.uint16)
   if c==1:a=im;ai=ii
   else:a,ai=join(a,ai,im,ii,k)
  rows.append(a);rowids.append(ai)
 a=rows[0];ai=rowids[0]
 for r in range(1,4):a,ai=join(a.transpose(1,0,2),ai.T,rows[r].transpose(1,0,2),rowids[r].T,k);a=a.transpose(1,0,2);ai=ai.T
 p=T/f'fixed-{k}';p.mkdir(exist_ok=True);Image.fromarray(a).save(p/'native-context.png');Image.fromarray(ai).save(p/'source-id.png');tile=Image.fromarray(a[115:4211,115:4211]);tile.resize((1024,1024),Image.Resampling.LANCZOS).save(p/'overview.preview-only.png')
 v=Image.new('RGB',(900,1024));h=Image.new('RGB',(1024,1200))
 for c in range(1,4):v.paste(tile.crop((c*1024-150,2048,c*1024+150,3072)),((c-1)*300,0))
 for c in range(4):h.paste(tile.crop((c*1024,3072-150,(c+1)*1024,3072+150)),(0,c*300))
 v.save(p/'v-row3.100pct.png');h.save(p/'h-row3.100pct.png')
 print(str(p))

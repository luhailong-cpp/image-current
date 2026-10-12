from repair_composite import *
from PIL import ImageDraw
D=W/'object-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
def polygon(n,key,points):
 global a,i,s
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));m=Image.new('L',(1254,1254));ImageDraw.Draw(m).polygon(points,fill=255);mask=np.asarray(m)>0
 a[y:y+1254,x:x+1254][mask]=src[mask];i[y:y+1254,x:x+1254][mask]=key;s[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 m.save(D/(n+'.mask.png'));Image.fromarray(a[y:y+1254,x:x+1254]).save(D/(n+'.result.png'))
# Keep the repaired center's whole slabs, place boundary on matching surrounding tiles.
polygon('r02_c03_paving_join_a_v01',104,[(115,445),(225,400),(320,438),(457,355),(639,450),(744,400),(1075,540),(1150,650),(1055,715),(1140,772),(1025,850),(952,810),(812,900),(620,804),(505,872),(353,785),(268,828),(115,751)])
polygon('r02_c03_paving_join_b_v01',105,[(115,390),(270,350),(453,441),(634,350),(886,475),(1090,390),(1180,540),(1130,720),(993,800),(837,720),(710,800),(520,710),(405,780),(258,705),(115,760)])
finish(D,a,i,s)


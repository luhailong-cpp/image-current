from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,sys,importlib.util
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;SW=R.parent.parent;S=SW/'integrated-20261011/v2'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def crop(box):
 result=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));covered=np.zeros((result.height,result.width),bool);src=[]
 for tile,b in [('r10_c05',[16384,36864,20480,40960]),('r10_c06',[20480,36864,24576,40960])]:
  p=S/(tile+'.candidate.png');l,t,r,d=max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])
  if l>=r or t>=d:continue
  sc=[l-b[0],t-b[1],r-b[0],d-b[1]];dc=[l-box[0],t-box[1],r-box[0],d-box[1]]
  im=Image.open(p).convert('RGB');result.paste(im.crop(sc),(dc[0],dc[1]));covered[dc[1]:dc[3],dc[0]:dc[2]]=True
  ctx=S/(tile+'.candidate.context.png');assert np.array_equal(np.array(Image.open(ctx))[115:4211,115:4211],np.array(im))
  src.append({'tile':tile,'file':str(p),'sha256':sha(p),'coreWorldBox':b,'sourceCrop':sc,'destinationBox':dc,'context':str(ctx),'contextSha256':sha(ctx),'contextCoreEqualsCandidate':True})
 assert covered.all()
 return result,src
def prepare(name,box,window,specific):
 d=R/name;d.mkdir(parents=True,exist_ok=True);im,s=crop(box);assert im.size==(1254,1254);im.save(d/'input.png')
 c=read(SW.parent/'production-contract.json');refs=[str(d/'input.png')]+[c[k] for k in ('layoutReference','detailStyleReference','primaryStyleReference')]
 prompt='Use case: precise-object-edit. Edit Image 1 only, exactly native 1254x1254 opaque PNG. '+specific+'\nImage 2 is the approved whole map layout only; do not reproduce its whole view. Image 3 is the approved daylight clean natural pale-grey stone finish. Image 4 gives polished Daoist chibi rendering only, not its UI, characters or nighttime framing. This is an extreme macro staircase crop. Keep all positions, perspective, number and depth of stairs, horizontal edges, narrow seams, rounded bevels and shadows exactly. Change ONLY the sharp vertical tonal/microtexture join near image x=627 into a natural gentle continuous material transition between the existing left and right grey stone surfaces. The faint stone material on both sides must continue through the join, without a seam, visible rectangular patch, abrupt color/texture divider, diagonal brush band or blurry patch. Match the same stone style, no new decorative detail. No extra stairs, lines, architecture, props or foliage. No resizing, reframing, photo blur or diagonal shadows.'
 (d/'prompt.txt').write_text(prompt,encoding='utf-8')
 req={'name':name,'prompt':prompt,'promptFile':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'referenced_image_paths':refs,'references':[{'file':p,'sha256':sha(p),'role':role}for p,role in zip(refs,['exact native edit target','approved overall layout','approved daylight materials','approved Daoist style'])],'worldBox':box,'maskWindowInPatch':window,'sourceCrops':s,'requestedNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'preparedAtUtc':now(),'sourceResampling':False}
 write(d/'request.json',req);return req
def ingest(name,path,hint):
 d=R/name;r=read(d/'request.json');im=Image.open(path);assert im.size==(1254,1254);shutil.copyfile(path,d/'native.png')
 g={**r,'file':str(d/'native.png'),'sha256':sha(d/'native.png'),'sourceOutput':str(path),'sourceOutputSha256':sha(path),'actualNativePixels':list(im.size),'actualModel':None,'actualQuality':None,'receivedAtUtc':now(),'status':'returned_image','toolOutputHint':hint}
 write(d/'generation.json',g);write(d/'receipt.json',{'status':'returned_image','output_hint':hint,'sourceOutput':str(path),'sha256':sha(path),'actualNativePixels':list(im.size),'actualModel':None,'actualQuality':None,'atUtc':g['receivedAtUtc']});return {'file':g['file'],'sha256':g['sha256'],'receivedAtUtc':g['receivedAtUtc']}
def proposal(name):
 d=R/name;r=read(d/'generation.json')
 for x in r['references']:assert sha(x['file'])==x['sha256']
 old=np.array(Image.open(d/'input.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'))
 l,t,rr,bb=r['maskWindowInPatch'];a=old[t:bb,l:rr];b=new[t:bb,l:rr];h,w=a.shape[:2];assert min(h,w)>230
 spec=importlib.util.spec_from_file_location('q',SW/'local_repairs.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
 alpha=np.full((h,w),255,np.uint8);records=[]
 strips={'left':(a[:,:115],b[:,:115]),'right':(a[:,-115:][:,::-1],b[:,-115:][:,::-1]),'top':(a[:115].transpose(1,0,2),b[:115].transpose(1,0,2)),'bottom':(a[-115:][::-1].transpose(1,0,2),b[-115:][::-1].transpose(1,0,2))}
 for side,(before,after) in strips.items():
  seam=q.minimum_error_path(before,after,2);m=q.inclusion_mask(seam,2);records.append({'side':side,'distances':seam.tolist()})
  if side=='left':alpha[:,:115]=np.minimum(alpha[:,:115],m)
  if side=='right':alpha[:,-115:]=np.minimum(alpha[:,-115:],m[:,::-1])
  if side=='top':alpha[:115]=np.minimum(alpha[:115],m.T)
  if side=='bottom':alpha[-115:]=np.minimum(alpha[-115:],m.T[::-1])
 full=np.zeros((1254,1254),np.uint8);full[t:bb,l:rr]=alpha
 weight=full.astype(np.uint32)[...,None];mixed=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
 Image.fromarray(full).save(d/'alpha.png');Image.fromarray(np.uint8(full>0)*255).save(d/'copy-mask.png');Image.fromarray(mixed).save(d/'premixed.png',optimize=True)
 ys,xs=np.nonzero(full)
 rec={'status':'proposal_pending_parent_merge','name':name,'worldBox':r['worldBox'],'affectedWorldBox':[r['worldBox'][0]+int(xs.min()),r['worldBox'][1]+int(ys.min()),r['worldBox'][0]+int(xs.max())+1,r['worldBox'][1]+int(ys.max())+1],'premixed':str(d/'premixed.png'),'premixedSha256':sha(d/'premixed.png'),'input':str(d/'input.png'),'inputSha256':sha(d/'input.png'),'copyMask':str(d/'copy-mask.png'),'copyMaskSha256':sha(d/'copy-mask.png'),'alpha':str(d/'alpha.png'),'alphaSha256':sha(d/'alpha.png'),'sourceCrops':r['sourceCrops'],'generationRecord':str(d/'generation.json'),'generationRecordSha256':sha(d/'generation.json'),'maxFeatherRadiusPixels':2,'sourceResampling':False,'maskWindowInPatch':r['maskWindowInPatch'],'quiltingPaths':records,'copyRule':'Copy premixed once where copy-mask is nonzero; validate input under mask first; no reblending.','formalAccepted':False,'atUtc':now()}
 write(d/'proposal.json',rec);return {k:v for k,v in rec.items()if k!='quiltingPaths'}
if __name__=='__main__':
 if sys.argv[1]=='ingest':print(json.dumps(ingest(*sys.argv[2:5]),ensure_ascii=False))
 if sys.argv[1]=='proposal':print(json.dumps(proposal(sys.argv[2]),ensure_ascii=False))


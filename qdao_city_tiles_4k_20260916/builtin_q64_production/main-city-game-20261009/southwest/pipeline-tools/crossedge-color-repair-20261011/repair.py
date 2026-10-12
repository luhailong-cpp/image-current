from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,sys,importlib.util
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;SW=R.parent.parent;ROOT=SW.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
SOURCES={
'r10_c05':(SW/'r10_c05/repairs/output/r10_c05.repaired.candidate.png',[16384,36864,20480,40960]),
'r10_c06':(SW/'r10_c06/repairs-20261011/output/r10_c06.repaired.candidate.png',[20480,36864,24576,40960]),
'r11_c06':(SW/'r11_c06/pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png',[20480,40960,24576,45056])}
def cropworld(box):
 out=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));cover=np.zeros((out.height,out.width),bool);refs=[]
 for tile,(path,b) in SOURCES.items():
  l,t,r,d=max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])
  if l>=r or t>=d:continue
  im=Image.open(path).convert('RGB');assert im.size==(4096,4096)
  sc=[l-b[0],t-b[1],r-b[0],d-b[1]];dc=[l-box[0],t-box[1],r-box[0],d-box[1]]
  out.paste(im.crop(sc),(dc[0],dc[1]));cover[dc[1]:dc[3],dc[0]:dc[2]]=True
  refs.append({'tile':tile,'file':str(path),'sha256':sha(path),'coreWorldBox':b,'sourceCrop':sc,'destinationBox':dc,'sourceResampling':False})
 assert cover.all(),'uncovered image pixels'
 return out,refs
def prepare(name,box,window,content):
 d=R/name;d.mkdir(parents=True,exist_ok=True);assert not(d/'native.png').exists()
 im,src=cropworld(box);assert im.size==(1254,1254);im.save(d/'input.png')
 c=read(ROOT/'production-contract.json')
 refs=[str(d/'input.png')]+[c[k] for k in ('layoutReference','detailStyleReference','primaryStyleReference')]
 prompt='Use case: precise-object-edit. Edit Image 1 only at native 1254x1254. '+content+'\nPreserve exact framing, all existing objects and their silhouettes, all remote line positions. Do not zoom or recenter. Image 2 is approved whole-map geometry context only; Image 3 is approved daylight natural-grey stone and warm polished wood finish; Image 4 is approved Daoist chibi visual style only. No UI, text or whole city in output. Quiet hand-painted surfaces, no blur, no new stone joints, no extra decorations or vegetation. Return only the repaired close-up Image 1. Exact 1254x1254 opaque PNG.'
 (d/'prompt.txt').write_text(prompt,encoding='utf-8')
 rec={'name':name,'prompt':prompt,'promptFile':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'referenced_image_paths':refs,'references':[{'file':p,'sha256':sha(p),'role':role}for p,role in zip(refs,['exact composed native edit target','approved map geometry','approved material','approved primary style'])],'worldBox':box,'maskWindowInPatch':window,'sourceCrops':src,'requestedNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'sourceResampling':False,'preparedAtUtc':now()}
 write(d/'request.json',rec);return rec
def ingest(name,path,hint):
 d=R/name;r=read(d/'request.json');src=Path(path);im=Image.open(src);assert im.size==(1254,1254)
 assert not(d/'native.png').exists();shutil.copyfile(src,d/'native.png')
 rec={**r,'status':'returned_image','file':str(d/'native.png'),'sha256':sha(d/'native.png'),'sourceOutput':str(src),'sourceOutputSha256':sha(src),'actualNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'toolOutputHint':hint,'receivedAtUtc':now()}
 write(d/'generation.json',rec);write(d/'receipt.json',{'status':'returned_image','output_hint':hint,'sourceOutput':str(src),'sha256':sha(src),'actualNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'atUtc':now()});return rec
def proposal(name):
 d=R/name;r=read(d/'generation.json')
 for x in r['references']:assert sha(x['file'])==x['sha256']
 old=np.array(Image.open(d/'input.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'))
 l,t,rr,bb=r['maskWindowInPatch']
 if name=='east-stone-left-v01':l=270 # includes the entire adjacent left stone face, keeping pillar and drum outside
 a=old[t:bb,l:rr];b=new[t:bb,l:rr];h,w=a.shape[:2];assert min(h,w)>230
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
 if name=='wood-lower-v01':full[602:]=0 # preserve every stone-stair pixel; the model changed remote shadows
 weight=full.astype(np.uint32)[...,None];premixed=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
 assert np.array_equal(premixed[full==0],old[full==0])
 Image.fromarray(full).save(d/'alpha.png');Image.fromarray(np.uint8(full>0)*255).save(d/'copy-mask.png');Image.fromarray(premixed).save(d/'premixed.png',optimize=True)
 ys,xs=np.nonzero(full);affected=[r['worldBox'][0]+int(xs.min()),r['worldBox'][1]+int(ys.min()),r['worldBox'][0]+int(xs.max())+1,r['worldBox'][1]+int(ys.max())+1]
 rec={'name':name,'status':'proposal_pending_parent_merge','worldBox':r['worldBox'],'affectedWorldBox':affected,'native':str(d/'native.png'),'nativeSha256':sha(d/'native.png'),'premixed':str(d/'premixed.png'),'premixedSha256':sha(d/'premixed.png'),'alpha':str(d/'alpha.png'),'alphaSha256':sha(d/'alpha.png'),'copyMask':str(d/'copy-mask.png'),'copyMaskSha256':sha(d/'copy-mask.png'),'copyRule':'Copy premixed RGB only where copy-mask != 0. Do not blend premixed a second time. Preserve current destination outside mask. Revalidate source under mask before copy.','sourceCrops':r['sourceCrops'],'generationRecord':str(d/'generation.json'),'generationRecordSha256':sha(d/'generation.json'),'maskWindowInPatch':r['maskWindowInPatch'],'maxFeatherRadiusPixels':2,'quiltingPaths':records,'sourceResampling':False,'changedPixelCount':int(np.any(premixed!=old,axis=2).sum()),'actualModel':None,'actualQuality':None,'formalAccepted':False,'atUtc':now()}
 rec['maskWindowInPatch']=[l,t,rr,bb]
 if name=='wood-lower-v01':rec['excludedPatchBox']=[0,602,1254,1254];rec['exclusionReason']='Native output changed stone shadows outside wood task; sparse mask retains original stone exactly.'
 write(d/'proposal.json',rec);return {k:v for k,v in rec.items() if k!='quiltingPaths'}
if __name__=='__main__':
 if sys.argv[1]=='ingest':print(json.dumps(ingest(*sys.argv[2:5]),ensure_ascii=False))
 if sys.argv[1]=='proposal':print(json.dumps(proposal(sys.argv[2]),ensure_ascii=False))


"""Multiple disjoint native1254 hard-mask repairs over a pair, source-identity verified."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,re,importlib.util,datetime
import numpy as np
from PIL import Image,ImageDraw
Z=Path(__file__).resolve().parents[1];QA=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def inp(r):p=Path(r['path']);assert sha(p)==r['sha256'];return p
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def savepng(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
def savenpy(p,a):
 assert not p.exists();np.save(p,a);assert np.array_equal(np.load(p),a);return ref(p)
def savejson(p,a):
 assert not p.exists();p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');return ref(p)
def mod(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True,type=Path);ap.add_argument('--trial',action='store_true');args=ap.parse_args();m=read(args.manifest);pre=m['outputPrefix'];assert re.fullmatch('pair-[a-z0-9_-]+',pre);assert not list(QA.glob(pre+'-*'))
 t=read(inp(m['basePairTrace']));out=rgb(inp(t['context']));base=out.copy();ids=np.load(inp(t['sourceIds'])).astype(np.uint8);assert np.all(np.isin(ids,[0,1]));assert ids.shape==out.shape[:2];vertical=t['axis']=='vertical'
 c=mod('pair_repair_mask',QA/'repair-compose.py');h=mod('pair_repair_helper',Z/'tools/seam_helpers.py');repairs=[];legend={'0':t['inputs'][0],'1':t['inputs'][1]}
 for i,a in enumerate(m['repairs'],2):
  source=rgb(inp(a['source']));repair=rgb(inp(a['repair']));assert source.shape==repair.shape==(1254,1254,3);gen=read(inp(a['generationRecord']));assert gen['sha256']==a['repair']['sha256']
  l,top,r,bottom=a['contextBox'];assert [r-l,bottom-top]==[1254,1254] and 0<=l<r<=out.shape[1] and 0<=top<bottom<=out.shape[0];assert np.array_equal(source,base[top:bottom,l:r])
  mask,paths=c.closed_mask(source,repair,a['repairBounds'],a['margin'],a['contextBox'],h._minimum_vertical_seam)
  if 'clipPolygon' in a:
   poly=Image.new('L',(1254,1254),0);ImageDraw.Draw(poly).polygon([tuple(p) for p in a['clipPolygon']],fill=1);mask&=np.asarray(poly)
  sel=mask.astype(bool);assert np.all(ids[top:bottom,l:r][sel]<2),'Repair masks overlap'
  out[top:bottom,l:r][sel]=repair[sel];ids[top:bottom,l:r][sel]=i;assert np.array_equal(out[top:bottom,l:r][sel],repair[sel]);assert (ids==i).sum()==sel.sum()
  item=dict(a,sourceId=i,mask=savenpy(QA/(pre+'-'+a['id']+'-mask.npy'),mask),hardMaskPaths=paths,retainedPixels=int(sel.sum()),after=savepng(QA/(pre+'-'+a['id']+'-after-100pct.png'),out[top:bottom,l:r]))
  repairs.append(item);legend[str(i)]={'source':a['repair'],'contextBox':a['contextBox'],'generationRecord':a['generationRecord']}
 assert np.array_equal(out[ids<2],base[ids<2])
 for i,item in enumerate(t['inputs']):
  x=0 if vertical else 4096*i;y=4096*i if vertical else 0;native=rgb(inp(item['context']));chosen=ids[y:y+4326,x:x+4326]==i;assert np.array_equal(out[y:y+4326,x:x+4326][chosen],native[chosen]);assert (ids==i).sum()==chosen.sum()
 result={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'native_pair_multi_repaired_pending_visual_qa','inputs':t['inputs'],'provenance':t['provenance']+[m['basePairTrace']]+[a['generationRecord'] for a in m['repairs']],'basePairTrace':m['basePairTrace'],'axis':t['axis'],'globalContextBox':t['globalContextBox'],'manifest':ref(args.manifest),'script':ref(Path(__file__)),'hardSeamPathIn230Overlap':t['hardSeamPathIn230Overlap'],'repairs':repairs,'sourceLegend':legend,'tiles':[],'qa':[],'validation':{'allFinalPixelsMatchInputContextOrNativeRepair':True,'savedPixelsVerified':True,'allSourceHashesVerified':True,'sourceIdsOutsideContextRejected':True,'repairMasksDisjoint':True,'nativePixelsResampled':False,'featheringApplied':False,'colorProcessingApplied':False},'formalAcceptedCount':0}
 if not args.trial:
  result['context']=savepng(QA/(pre+'-context-native.png'),out);result['sourceIds']=savenpy(QA/(pre+'-source-ids.npy'),ids)
  for i,item in enumerate(t['tiles']):
   x1,y1,x2,y2=item['contextBox'];cx1,cy1,cx2,cy2=item['coreBox'];result['tiles'].append({'tile':item['tile'],'context':savepng(QA/(pre+'-'+item['tile']+'-context-native.png'),out[y1:y2,x1:x2]),'contextBox':item['contextBox'],'candidate':savepng(QA/(pre+'-'+item['tile']+'-candidate-4096.png'),out[cy1:cy2,cx1:cx2]),'coreBox':item['coreBox']})
 for i,item in enumerate(t['qa'],1):
  x1,y1,x2,y2=item['contextBox'];a=out[y1:y2,x1:x2];result['qa'].append(dict(savepng(QA/(pre+f'-shared-part{i:02d}-100pct.png'),a),contextBox=item['contextBox'],globalBox=item['globalBox'],exactPixelIdentityToV1=bool(np.array_equal(a,rgb(inp(item))))))
 trace=savejson(QA/(pre+'-trace.json'),result);print(json.dumps({'trace':trace,'qaCount':len(result['qa']),'repairCount':len(repairs),'context':result.get('context'),'tiles':result['tiles']}))
if __name__=='__main__':main()


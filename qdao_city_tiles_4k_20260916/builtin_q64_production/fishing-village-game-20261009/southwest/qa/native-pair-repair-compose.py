"""One native1254 hard-mask repair over a joined pair, with complete source identities."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,re,importlib.util,datetime
import numpy as np
from PIL import Image
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
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True,type=Path);args=ap.parse_args();m=read(args.manifest);pre=m['outputPrefix'];assert re.fullmatch('pair-[a-z0-9_-]+',pre);assert not list(QA.glob(pre+'-*'))
 t=read(inp(m['basePairTrace']));out=rgb(inp(t['context']));base=out.copy();ids=np.load(inp(t['sourceIds']));assert np.all(np.isin(ids,[0,1]));assert ids.shape==out.shape[:2];vertical=t['axis']=='vertical'
 source=rgb(inp(m['source']));repair=rgb(inp(m['repair']));assert source.shape==repair.shape==(1254,1254,3);gen=read(inp(m['generationRecord']));assert gen['sha256']==m['repair']['sha256']
 l,top,r,bottom=m['contextBox'];assert [r-l,bottom-top]==[1254,1254] and 0<=l<r<=out.shape[1] and 0<=top<bottom<=out.shape[0];assert np.array_equal(source,base[top:bottom,l:r])
 c=mod('pair_repair_mask',QA/'repair-compose.py');h=mod('pair_repair_helper',Z/'tools/seam_helpers.py');mask,paths=c.closed_mask(source,repair,m['repairBounds'],m['margin'],m['contextBox'],h._minimum_vertical_seam);sel=mask.astype(bool)
 out[top:bottom,l:r][sel]=repair[sel];ids[top:bottom,l:r][sel]=2;assert np.array_equal(out[ids!=2],base[ids!=2]);assert np.array_equal(out[top:bottom,l:r][sel],repair[sel])
 for i,item in enumerate(t['inputs']):
  x=0 if vertical else 4096*i;y=4096*i if vertical else 0;native=rgb(inp(item['context']));chosen=ids[y:y+4326,x:x+4326]==i;assert np.array_equal(out[y:y+4326,x:x+4326][chosen],native[chosen]);assert (ids==i).sum()==chosen.sum()
 assert (ids==2).sum()==sel.sum()
 result={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'native_pair_repaired_pending_visual_qa','inputs':t['inputs'],'provenance':t['provenance']+[m['basePairTrace'],m['generationRecord']],'basePairTrace':m['basePairTrace'],'axis':t['axis'],'globalContextBox':t['globalContextBox'],'manifest':ref(args.manifest),'script':ref(Path(__file__)),'hardSeamPathIn230Overlap':t['hardSeamPathIn230Overlap'],'context':savepng(QA/(pre+'-context-native.png'),out),'sourceIds':savenpy(QA/(pre+'-source-ids.npy'),ids),'sourceLegend':{'0':t['inputs'][0],'1':t['inputs'][1],'2':{'source':m['repair'],'contextBox':m['contextBox'],'generationRecord':m['generationRecord']}},'repair':{'source':m['source'],'repair':m['repair'],'contextBox':m['contextBox'],'repairBounds':m['repairBounds'],'margin':m['margin'],'mask':savenpy(QA/(pre+'-repair-mask.npy'),mask),'hardMaskPaths':paths,'retainedPixels':int(sel.sum()),'after':savepng(QA/(pre+'-repair-after-100pct.png'),out[top:bottom,l:r])},'tiles':[],'qa':[],'validation':{'allFinalPixelsMatchInputContextOrNativeRepair':True,'savedPixelsVerified':True,'allSourceHashesVerified':True,'sourceIdsOutsideContextRejected':True,'nativePixelsResampled':False,'featheringApplied':False,'colorProcessingApplied':False},'formalAcceptedCount':0}
 for i,item in enumerate(t['tiles']):
  x1,y1,x2,y2=item['contextBox'];cx1,cy1,cx2,cy2=item['coreBox'];result['tiles'].append({'tile':item['tile'],'context':savepng(QA/(pre+'-'+item['tile']+'-context-native.png'),out[y1:y2,x1:x2]),'contextBox':item['contextBox'],'candidate':savepng(QA/(pre+'-'+item['tile']+'-candidate-4096.png'),out[cy1:cy2,cx1:cx2]),'coreBox':item['coreBox']})
 for i,item in enumerate(t['qa'],1):
  x1,y1,x2,y2=item['contextBox'];a=out[y1:y2,x1:x2];result['qa'].append(dict(savepng(QA/(pre+f'-shared-part{i:02d}-100pct.png'),a),contextBox=item['contextBox'],globalBox=item['globalBox'],exactPixelIdentityToV1=bool(np.array_equal(a,rgb(inp(item))))))
 trace=savejson(QA/(pre+'-trace.json'),result);print(json.dumps({'context':result['context'],'tiles':result['tiles'],'trace':trace,'qaCount':len(result['qa'])}))
if __name__=='__main__':main()

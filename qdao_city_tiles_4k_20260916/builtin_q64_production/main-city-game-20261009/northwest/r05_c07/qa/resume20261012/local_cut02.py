import json,importlib.util,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
tile=Path(__file__).resolve().parents[2];zone=tile.parent
def mod(name):
 spec=importlib.util.spec_from_file_location(name,zone/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=mod('production_v2');a=mod('assemble_native')
basepath=tile/'candidate/r05_c07-candidate-localcut-374432b8ed07.assembly.json';base=json.loads(basepath.read_text())
assert p.sha(Path(base['output']['file']))==base['output']['sha256']
out=np.array(Image.open(base['output']['file']));initial=out.copy();source_map=np.array(Image.open(base['sourceMap']['file']))
sources={}
for s in base['nativeSources']:
 ref=p.validate_native(p.selected_path(tile,s['id']),tile,s['id']);assert ref['sha256']==s['sha256'];sources[s['id']]=np.array(Image.open(ref['file']).convert('RGB'))
cuts=[]
for r in (1,4):
 left=sources[f's{r:02d}_01'][115:1139,1024:1254];right=sources[f's{r:02d}_02'][115:1139,0:230]
 path=a.minimum_vertical_seam(left,right);mask=np.arange(230)[None,:]>=path[:,None]
 out[(r-1)*1024:r*1024,909:1139]=np.where(mask[:,:,None],right,left)
 source_map[(r-1)*1024:r*1024,909:1139]=np.where(mask,(r-1)*4+2,(r-1)*4+1)
 cuts.append({'axis':'x','row':r,'tileOverlapBox':[909,(r-1)*1024,1139,r*1024],'binaryPathIn230Overlap':path.tolist(),'reason':'Test minimum native sample difference for existing grout/road crossing offsets'})
for s in base['nativeSources']:
 sid=(s['row']-1)*4+s['column'];ys,xs=np.where(source_map==sid);ox=(s['column']-1)*1024-115;oy=(s['row']-1)*1024-115
 assert np.all((xs-ox>=0)&(xs-ox<1254)&(ys-oy>=0)&(ys-oy<1254))
 assert np.array_equal(out[ys,xs],sources[s['id']][ys-oy,xs-ox])
sig=hashlib.sha256(json.dumps({'base':base['output']['sha256'],'cuts':cuts},sort_keys=True).encode()).hexdigest()[:12]
name='r05_c07-candidate-localcut-'+sig;target=tile/'candidate'/(name+'.png');assert not target.exists()
output=a.save_png(Image.fromarray(out),target);mapref=a.save_png(Image.fromarray(source_map),tile/'candidate'/(name+'.source-map.png'));qa=a.write_qa(Image.fromarray(out),output,tile/'qa'/name)
base.update({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'output':output,'qa':qa,'sourceMap':mapref,'verticalNativeCuts':cuts,'script':{'file':str(Path(__file__)),'sha256':p.sha(Path(__file__))},'changedPixelCount':int(np.count_nonzero(np.any(out!=initial,axis=2))),'derivedFromPreviousCandidate':{'file':str(basepath),'sha256':p.sha(basepath)}})
a.write_json(tile/'candidate'/(name+'.assembly.json'),base)
a.write_json(tile/'candidate'/(name+'.png.derivation.json'),{'operation':'Binary selection of unchanged native pixels at identical world coordinates','output':output,'assemblyManifest':str(tile/'candidate'/(name+'.assembly.json')),'sourceMap':mapref,'sourceResampled':False,'formalAccepted':False,'everyOutputPixelProvenNative':True})
outdir=tile/'qa'/name
for title,box in [('upper-left-seam',[850,280,1280,560]),('lower-left-seam',[850,630,1280,890]),('bottom-road-join',[910,3350,1210,3650])]:Image.fromarray(out).crop(box).save(outdir/(title+'.png'))
print(json.dumps({'output':output,'qa':str(outdir),'changedPixelCount':base['changedPixelCount']}))


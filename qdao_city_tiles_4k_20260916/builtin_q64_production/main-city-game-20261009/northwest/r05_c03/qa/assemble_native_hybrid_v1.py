import sys,pathlib,json,hashlib,numpy as np
from PIL import Image
Z=pathlib.Path(__file__).resolve().parents[2];T=Z/'r05_c03';sys.path.insert(0,str(Z));import assemble_native as A
basepath=T/'candidate/r05_c03-candidate-hard-65f341e34b58.png';base=np.asarray(Image.open(basepath).convert('RGB'));new=np.asarray(Image.open(T/'native/s04_01_fix03.png').convert('RGB'))
# All coordinates below are native source coordinates. Source at tile origin (-115,2957).
old=base[2957:2957+1139,0:1139] # only use matching source bounds
def cost_region(x0,y0,x1,y1):
 return base[2957+y0:2957+y1,x0-115:x1-115],new[y0:y1,x0:x1]
left_a,left_b=cost_region(870,80,980,350);left=A.minimum_vertical_seam(left_a,left_b)+870
right_a,right_b=cost_region(1140,80,1240,350);right=A.minimum_vertical_seam(right_a,right_b)+1140
top_a,top_b=cost_region(870,80,1240,115);top=A.minimum_vertical_seam(top_a.transpose(1,0,2),top_b.transpose(1,0,2))+80
bottom_a,bottom_b=cost_region(870,280,1240,350);bottom=A.minimum_vertical_seam(bottom_a.transpose(1,0,2),bottom_b.transpose(1,0,2))+280
yy,xx=np.mgrid[80:350,870:1240]
mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
out=base.copy();roi=out[3037:3307,755:1125];roi[mask]=new[80:350,870:1240][mask]
proof=np.all(out[np.s_[:]]==base,axis=2);proof[3037:3307,755:1125]|=np.all(roi==new[80:350,870:1240],axis=2);assert proof.all()
params={'left':left.tolist(),'right':right.tolist(),'top':top.tolist(),'bottom':bottom.tolist(),'nativeRoi':[870,80,1240,350]}
sig=hashlib.sha256(json.dumps({'base':A.sha(basepath),'extra':A.sha(T/'native/s04_01_fix03.png'),'params':params},sort_keys=True).encode()).hexdigest()[:12]
name='r05_c03-candidate-native-hybrid-'+sig;im=Image.fromarray(out);ref=A.save_png(im,T/'candidate'/(name+'.png'))
m=json.loads((T/'candidate/r05_c03-candidate-hard-65f341e34b58.assembly.json').read_text());m.update(output=ref,method='hard-native-cores-with-authorized-second-native-source-binary-region',createdAtUtc=A.now(),additionalNativeSources=[{'file':str(T/'native/s04_01_fix03.png'),'sha256':A.sha(T/'native/s04_01_fix03.png'),'originInTile':[-115,2957],'generationRecord':str(T/'native/s04_01_fix03.png.generation.json')}],regionSelection=params,nativePixelProof={'passed':bool(proof.all()),'pixels':16777216,'sourcePixelsUsed':int(mask.sum()),'allPixelsEqualOneRecordedNativeAtSameWorldCoordinates':True},script={'file':str(pathlib.Path(__file__).resolve()),'sha256':A.sha(pathlib.Path(__file__))})
m['qa']=A.write_qa(im,ref,T/'qa'/name);A.write_json(T/'candidate'/(name+'.assembly.json'),m)
mp=T/'qa'/name/'secondary-source-mask-native-scale.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp)
im.crop((715,2997,1165,3347)).save(T/'qa'/name/'mask-boundary-native.png')
A.write_json(T/'candidate'/(name+'.png.derivation.json'),{'output':ref,'assemblyManifest':str(T/'candidate'/(name+'.assembly.json')),'sourceResampled':False,'sourceUpscaled':False,'colorMatching':False,'feathering':False,'pixelProof':m['nativePixelProof'],'operation':m['method']})
print(json.dumps({'candidate':ref,'qa':str(T/'qa'/name),'proof':m['nativePixelProof']},indent=2))


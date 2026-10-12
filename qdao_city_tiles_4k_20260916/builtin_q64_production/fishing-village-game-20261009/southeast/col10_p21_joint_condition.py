from PIL import Image
import tile_native_workflow as w
import json
T=w.ZONE/'r12_c10';stem='p21-v3';q=w.read(T/'p21-v2.request.json')
base=T/'layout-only/p21-native-conditioned.png';im=Image.open(base).convert('RGB')
repair=T/'repairs/stairs-joint-p11-p21-v3.png';im.paste(Image.open(repair).crop((0,350,1254,1254)),(0,0))
out=T/'layout-only/p21-joint-conditioned-v3.png';im.save(out)
w.write(out.with_suffix('.png.derivation.json'),{'operation':'native unscaled joint repair overlap conditioning','base':str(base),'baseSha256':w.sha(base),'repair':str(repair),'repairSha256':w.sha(repair),'sourceCrop':[0,350,1254,1254],'destination':[0,0,1254,904],'globalBox':[36749,45965,38003,47219],'resamplingApplied':False,'notFinalArtwork':True})
q['referenced_image_paths'][0]=str(out)
q['prompt']='''Complete this native 1254 x 1254 map patch by outpainting ONLY the blurred lower portion of Image 1. Keep the ENTIRE sharp upper 904-pixel region exactly as it is: all three continuous straight stair fronts, their individual top and bottom lines, grey treads, camera, stone scale and material. The straightness of those long edges is correct; do not introduce any L-shaped turn or side face. The remaining bottom section completes the lowest stone step, then transitions to golden wooden dock floor as indicated by the sharp far-left bottom strip. Continue its precise wood board widths and diagonal direction with crisp wood grain. No new object, post, rail or stair. Image 2 full-map layout only; image 3 daylight detail/material only; image 4 PRIMARY clean rounded Q Daoist painterly game style only. Same bright warm daylight. No text, UI, borders or scene overview. The upper sharp part is the actual full native registered joint, not a thumbnail. Preserve it and extend the bottom at native crisp detail.'''
(T/(stem+'.prompt.txt')).write_text(q['prompt'],encoding='utf-8');w.write(T/(stem+'.request.json'),q)
print(json.dumps({k:q[k] for k in ['prompt','referenced_image_paths','transparent_background']}))

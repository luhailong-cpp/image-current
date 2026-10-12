from PIL import Image
import json
for p in ["C:/Users/luyua/.codex/generated_images/01a10bb7-53c7-7351-8a03-b483e31d5415/exec-bfd8e035-b274-4e1d-8c1c-4e0948d32f4e.png","C:/Users/luyua/.codex/generated_images/01a10bb7-53c7-7351-8a03-b483e31d5415/exec-04c9f3e4-37c5-4074-9454-84ba7596c93c.png"]:
 im=Image.open(p);a=im.getchannel("A");s=a.point(lambda x:255 if x>=128 else 0);edge=a.crop((im.width-1,0,im.width,im.height))
 print(json.dumps({"path":p,"size":im.size,"bbox128":s.getbbox(),"rightEdgeMax":edge.getextrema(),"rightEdgeOpaque":sum(v>=128 for v in edge.getdata())}))


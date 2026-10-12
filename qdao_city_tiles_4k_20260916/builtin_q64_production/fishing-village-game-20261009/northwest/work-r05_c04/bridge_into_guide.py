from workflow import *
id='r05_c04_s01_s04_v01';p=W/'guides'/(id+'.positional.png');out=W/'guides'/(id+'.with-head.png');im=Image.open(p).convert('RGB');n=B/'native/r05_c04_slim_post_head_bridge_v01.png';im.paste(Image.open(n).crop((115,769,1254,1254)),(0,0));im.save(out)
d=read(str(p)+'.derivation.json');d['headBridge']={'file':str(n),'sha256':sha(n),'sourceCrop':[115,769,1254,1254],'destinationBox':[0,0,1139,485]};d['sha256']=sha(out);write(str(out)+'.derivation.json',d)
q=read(W/'receipts'/(id+'.request.json'));q['referenced_image_paths'][0]=str(out);q['referenceHashes'][0]=sha(out);write(W/'receipts'/(id+'.request.json'),q)

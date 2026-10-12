from workflow import *
c=read(B.parent/'production-contract.json');box=[13700,19700,16208,22208];im=Image.open(c['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in box),resample=Image.Resampling.BICUBIC);im.save(W/'guides/south-post-layout-context.png')

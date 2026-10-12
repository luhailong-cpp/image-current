from production import *
D=W/'resume-20261012-v1';F=D/'composition-v2';Q=D/'neighbor-qa';Q.mkdir(exist_ok=True)
pair=np.asarray(Image.open(F/'full-pair.png'));pid=np.asarray(Image.open(F/'source-id.png'));pm=read(F/'assembly.json')
m=read(B/'work-r03_c02/west-final/r03_c02.west-final.assembly.json');ss={str(s['sourceId']):s for s in m['sources']};ids=np.asarray(Image.open(m['sourceIdMap']['file']))
b=[7565,8077,8819,9331];gy,gx=np.indices((1254,1254));gx+=b[0];gy+=b[1]
jm=read(B/'work-r03_c02/west-final/final-joint.assembly.json');s=jm['sources']['19'];assert s['globalNativeBox']==b
a=np.asarray(Image.open(s['file'])).copy();base=np.asarray(Image.open(m['candidate']['file']))
basecond=(gx<8192)&(gy>=8192);a[basecond]=base[gy[basecond]-8192,gx[basecond]-4096]
cond=(gx>=8077)&(gx<12403)&(gy>=3981)&(gy<9331);a[cond]=pair[gy[cond]-3981,gx[cond]-8077]
p=Q/'west-roof-current-proposed.png';Image.fromarray(a).save(p)
write(str(p)+'.derivation.json',{'globalBox':b,'nativeScaleResampled':False,'baseAssembly':str(B/'work-r03_c02/west-final/r03_c02.west-final.assembly.json'),'baseAssemblySha256':sha(B/'work-r03_c02/west-final/r03_c02.west-final.assembly.json'),'proposedPair':str(F/'full-pair.png'),'proposedPairSha256':sha(F/'full-pair.png'),'junctionGlobalX':8077,'neighborTileBoundaryGlobalX':8192,'guideOnly':True})
print(str(p))

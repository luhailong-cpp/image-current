import production as p
from PIL import Image
import sys
a_stem,b_stem,stem=sys.argv[1:4]
a=p.ROOT/'native'/f'{a_stem}.png'; b=p.ROOT/'native'/f'{b_stem}.png'
base=p.load(str(a)+'.generation.json')['coordinates']['nativeGlobalBox']
other=p.load(str(b)+'.generation.json')['coordinates']['nativeGlobalBox']
assert other[0]-base[0]==1024 and base[1]==other[1]
im=Image.new('RGB',(2278,1254));im.paste(Image.open(a).crop([0,0,1139,1254]),[0,0]);im.paste(Image.open(b).crop([115,0,1254,1254]),[1139,0])
out=p.ROOT/'guides'/f'{stem}.native-edit-target.png';im.crop([512,0,1766,1254]).save(out)
box=[base[0]+512,base[1],base[0]+1766,base[3]]
co={'tile':p.load(str(a)+'.generation.json')['coordinates']['tile'],'role':f'horizontal seam repair between{a_stem}and{b_stem}','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
p.dump(p.ROOT/'prompts'/f'{stem}.coordinates.json',co)
p.dump(str(out)+'.derivation.json',{'operation':'native hard crop/paste no resampling','derivedFrom':[p.metadata(a,'left native'),p.metadata(b,'right native')],'assemblySourceCrops':[[0,0,1139,1254],[115,0,1254,1254]],'assemblyDestinationTopLeft':[[0,0],[1139,0]],'assemblyCrop':[512,0,1766,1254],'coordinates':co})
p.dump(p.ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':[p.metadata(out,'native seam edit target, seamx627'),p.metadata(a,'left native context')]+[p.metadata(*r) for r in p.REFS],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(out)


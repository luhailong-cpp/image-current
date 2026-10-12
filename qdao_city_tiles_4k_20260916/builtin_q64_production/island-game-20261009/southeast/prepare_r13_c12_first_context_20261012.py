from workflow import *
from PIL import Image
pid='r13_c12_p11';v='v01'
layout=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(layout).convert('RGB')
f=ROOT/'native/r12_c12_p41_v01.png';im.paste(Image.open(f).convert('RGB').crop((0,1024,1254,1254)),(0,0))
j=ROOT/'native/r12_c12_lower_deck_joint_v01.png'
# The accepted overlay owns tile12 x512..1536, and extends its native bottom halo into tile13.
im.paste(Image.open(j).convert('RGB').crop((115,1024,742,1254)),(627,0))
g=ROOT/'guides'/f'{pid}.native-context-{v}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'usableAsFinalArt':False,'operation':'exact unscaled native north strips, overlay ownership preserved','nativeGlobalBox':patch(pid)['nativeGlobalBox'],'sources':[{'file':str(layout),'sha256':sha(layout),'role':'layout only'},{'file':str(f),'sha256':sha(f),'sourceCrop':[0,1024,1254,1254],'destination':[0,0]},{'file':str(j),'sha256':sha(j),'sourceCrop':[115,1024,742,1254],'destination':[627,0],'adoptionManifest':str(ROOT/'adopted-overlay-r12_c12-lower-deck-20261012-v01.json')}]})
pp=ROOT/'progress-r13_c12.json';assert not pp.exists()
write(pp,{'tile':'r13_c12','updatedAt':now(),'status':'context_prepared_pending_native_generation','generatedNativeCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'workingVersions':{},'missingPatches':[f'r13_c12_p{r}{c}' for r in range(1,5) for c in range(1,5)],'northOverlayOwnership':str(ROOT/'adopted-overlay-r12_c12-lower-deck-20261012-v01.json')})
print(g)

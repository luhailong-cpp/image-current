from pathlib import Path
import json,sys
from PIL import Image
Z=Path(__file__).resolve().parent
sys.path.insert(0,str(Z))
import r05_c14_extension as E
p='r05_c14_p11'; v='v2'
old=Z/'native'/f'{p}-v1.png'
south=Z/'native'/'r05_c14_p21-v1.png'
im=Image.open(old).convert('RGB')
# GUIDE ONLY: lengthen the plain left shaft and remove the premature collar/foam.
im.paste(im.crop((0,400,430,770)).resize((430,624),Image.Resampling.BICUBIC),(0,400))
im.paste(Image.open(south).convert('RGB').crop((0,0,1254,230)),(0,1024))
guide=Z/'guides'/f'{p}-{v}.native-repair-guide.png'; im.save(guide)
ops={'purpose':'GUIDE ONLY; no resulting guide pixel is final art','sources':[E.ref(old,'existing structure guide excluding wrong lower-left collar'),E.ref(south,'exact south anchor top230')],'operations':[{'cropBox':[0,400,430,770],'guideResizeTo':[430,624],'pasteAt':[0,400],'reason':'extend plain shaft, remove old too-high collar and foam'},{'source':str(south),'cropBox':[0,0,1254,230],'pasteAt':[0,1024],'scale':1}],'nativeFinalMustBeActualBuiltinOutput':True}
E.write(str(guide)+'.derived.json',ops)
plan=json.loads((Z/'records'/f'{p}.plan.json').read_text())
plan['createdAtUtc']=E.now()
plan['references'][-1]=E.ref(guide,'GUIDE ONLY with exact native south230 and corrected long left shaft')
plan['configSnapshot']=json.loads(E.CONFIG.read_text(encoding='utf-8-sig'))
plan['configSource']=E.ref(E.CONFIG,'configured target only, not actual selector')
plan['configSnapshotCaptureStage']='prepare_before_generation'
plan['repairSource']=E.ref(old,'existing failed candidate retained')
E.write(Z/'records'/f'{p}-{v}.plan.json',plan)
print(json.dumps({'guide':str(guide),'worldBox':plan['coordinates']['nativeGlobalBox'],'refs':[x['path'] for x in plan['references']]}))


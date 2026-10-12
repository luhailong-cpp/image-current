import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=ROOT/'finish-20261012';out=HERE/'d1-right-v1';out.mkdir(exist_ok=True)
ref=ROOT/'resume-20261012/prepared-contexts/d1-right/context-native.png';a=Image.open(ref).convert('RGB');f=HERE/'d1-left-v1/raw-native.png';b=Image.open(f).convert('RGB')
a.paste(b.crop((1100,270,1254,755)),(0,270));p.save_png(out/'edit-guide-with-left-anchor.png',a)
p.put_json(out/'preparation.json',{'tile':'r03_c05','tileBox':[1100,430,2354,1684],'worldBox':[17484,8622,18738,9876],'baseReference':p.reference(ref,'native target'),'leftAnchor':p.reference(f,'saved source pixels from left repair'),'leftAnchorNativeBox':[1100,270,1254,755],'anchorDestinationXY':[0,270],'guideRole':'edit input only, no claim of generated final art','resized':False})
p.save_png(HERE/'d1-left-west-current-native.png',Image.open(ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png').crop((3936,700,4096,1150)))
print(out)


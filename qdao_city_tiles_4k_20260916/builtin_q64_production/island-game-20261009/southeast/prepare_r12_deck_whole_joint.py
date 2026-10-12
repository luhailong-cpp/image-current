from workflow import *
from PIL import Image
name='r12_c12_deck_whole_joint_v01'; origin=[1421,-115];size=1254
im=Image.new('RGB',(size,size));parts=[]
def place(f,crop,dest):
    src=ROOT/f;im.paste(Image.open(src).convert('RGB').crop(crop),dest);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest})
# Exact true-core pieces, boundary inside the whole object window at x627.
place('native/r12_c12_p12_v02.png',[512,0,1139,1254],[0,0])
place('native/r12_c12_p13_v04.png',[115,0,742,1254],[627,0])
place('tiles/r11_c12.candidate-v02.png',[1421,3981,2675,4096],[0,0])
place('native/r12_c12_p22_v01.png',[512,115,1139,230],[0,1139])
place('native/r12_c12_p23_v03.png',[115,115,742,230],[627,1139])
guide=ROOT/'guides'/f'{name}.png';assert not guide.exists();im.save(guide)
write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'tile':'r12_c12','tileRelativeOrigin':origin,'width':1254,'height':1254,'sources':parts,'usableAsFinalArt':False,'operation':'exact native crop/paste whole wood-board junction reference'})
refs=[{'file':str(guide),'sha256':sha(guide),'role':'whole native wooden floor edit target with actual four edge context'}]+read(ROOT/'references.json')
prompt='''Edit attached image 1 into ONE complete native 1254 x 1254 game-art image. This is a precisely registered close-up of the wooden pier floor, from an existing continuous daylight Q Daoist game map. Image 1 is the exact full-size editable floor target, not a collage layout to invent. Last three references are whole island layout, material example, and approved painting style. No zoom, camera movement, text, people, or additional props.

Repair the COMPLETE set of wooden floorboards crossing the middle of this image, especially the broken dark plank grooves around vertical x627. The source images were joined at x627; that temporary assembly boundary must disappear. Build coherent long diagonal honey-gold floorboards, keeping the groove endpoints and spacing in the outer margins. Preserve TOP 115 pixels, BOTTOM 115 pixels, LEFT 115 pixels and RIGHT 115 pixels exactly as they are: these are fixed neighboring real artwork. The entire interior is editable. Where left/right groove phases cannot form one straight board, make a small believable transverse plank butt joint with two complete board ends within the central region x400..850, instead of a disconnected fading groove, forked line, or sharp vertical image seam. No long vertical divider stripe. Unify entire affected board surfaces and grain, preserve their current warm tone and lighting. Do not move or duplicate the partial gold railing finial near lower-left. This is an object repair, not a sharpness pass. Return one opaque square full crop with crisp hand-painted material at unchanged native scale.'''
pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
args={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'tileRelativeOrigin':origin,'submittedArguments':args,'actualModel':None,'actualQuality':None})
print(json.dumps(args))

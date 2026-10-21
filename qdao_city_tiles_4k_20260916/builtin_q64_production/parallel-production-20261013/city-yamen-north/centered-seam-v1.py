from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib,shutil,sys,importlib.util
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
D=B/'r02_c04/centered-seam-repair'
def prep():
 m.gate(True,'r02_c04')
 base=B/'r02_c04/native/s04_01-v004.png'
 southern=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r03_c04/finish-20261012-integrated/s01_01-derived.png')
 canonical=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/delivery-20261012-v1/r03_c04.png')
 im=Image.new('RGB',(1254,1254)); im.paste(Image.open(base).crop((0,512,1254,1139)),(0,0));im.paste(Image.open(southern).crop((0,115,1254,742)),(0,627));im.paste(Image.open(canonical).crop((0,0,1139,627)),(115,627))
 guide=m.next_path(D,'s04_01-south-centered-target','.png');im.save(guide)
 q={'schemaVersion':1,'kind':'centered_native_seam_repair_request','tile':'r02_c04','patch':'s04_01','createdAtUTC':m.now(),'base':str(base),'baseSHA256':m.sha(base),'repairWorldBox':[12173,7565,13427,8819],'nativePixels':[1254,1254],'guide':str(guide),'guideSHA256':m.sha(guide),'guideIsNativeCoordinateComposite':True,'guideIsModelOutput':False,'resampled':False,'sources':[{'file':str(base),'sha256':m.sha(base),'sourceCrop':[0,512,1254,1139],'paste':[0,0]},{'file':str(southern),'sha256':m.sha(southern),'sourceCrop':[0,115,1254,742],'paste':[0,627],'role':'left115 halo only; canonical overwrites rest'},{'file':str(canonical),'sha256':m.sha(canonical),'sourceCrop':[0,0,1139,627],'paste':[115,627],'role':'fixed neighbor actual delivery'}],'editPermittedWorldBox':[12173,7965,13427,8192],'applyRepairCrop':[0,400,1254,627],'applyToBaseXY':[0,912],'neighborFileWritesAllowed':False,'prompt':'Use case: precise-object-edit. Repair the short tile row just ABOVE the middle of this exact1254x1254 roof crop. The fixed tile-boundary is at y627. The blue tile collar curve around y590 leaves an unnaturally short tile before the next fixed collar below the boundary near y680. Repaint ONLY rows400..626 in the upper half: reconcile those blue tile collars into regular overlapping ceramic rows that continue smoothly into the lower half, without a shortened sliver, cut highlight, abrupt phase change or doubled rim at y627. Keep every column x-position, width and vertical highlight. The gold strip at x300..480 remains exactly unchanged. Preserve ALL lower-half pixels y627..1253 exactly; that neighboring tile is fixed. Preserve ALL rows0..399 exactly. Do not shift the framing or introduce any new feature. Paint a clean continuous teal ceramic surface, crisp Daoist chibi hand-painted material, no blur. Output the same1254x1254 image only.','referenced_image_paths':[str(guide)],'transparent_background':False,'actualModel':None,'route':'builtin_image_gen','plannedDerivation':'Only generated upper repair band will be copied at identical world pixels into a NEW derived1254 core source. The generated image remains separate and unmodified. No source scaling/warp/blur or neighboring file edits.'}
 request=m.next_path(D,'s04_01-centered-request');m.write_new(request,q);print(json.dumps({'request':str(request),'guide':str(guide)}))
def archive(request,host):
 q=m.read(request);dest=m.next_path(D,'s04_01-centered-native-repair','.png');assert Image.open(host).size==(1254,1254);shutil.copyfile(host,dest);rec={'kind':'native_generated_centered_repair','nativeToolOutput':True,'file':str(dest),'sha256':m.sha(dest),'hostOutput':host,'hostSHA256':m.sha(host),'pixels':[1254,1254],'repairWorldBox':q['repairWorldBox'],'requestFile':request,'requestSHA256':m.sha(request),'actualModel':None,'route':'builtin_image_gen','resizedAfterGeneration':False,'formalAccepted':False};m.write_new(dest.with_suffix('.png.generation.json'),rec);print(json.dumps(rec))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prep()
 elif sys.argv[1]=='archive':archive(*sys.argv[2:])


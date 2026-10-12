from native_work import *
im=Image.open(ZONE/'qa/connected-area/r03-r04_c12-c13.native.png')
out=ZONE/'qa/south-color-band-locate';out.mkdir(exist_ok=True)
for name,box in [('gourd-context',(3072,1536,5376,2560)),('gourd-a',(3085,1421,4339,2675)),('gourd-b',(4109,1421,5363,2675)),('bottle',(2445,2445,3699,3699))]:
 im.crop(box).save(out/f'{name}.png')
print(out.as_posix())


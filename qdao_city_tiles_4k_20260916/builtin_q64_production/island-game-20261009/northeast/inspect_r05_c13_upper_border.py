from native_work import *
a=ZONE/'tiles/r04_c13.png';b=ZONE/'tiles/r05_c13.png';out=Image.new('RGB',(4096,512));out.paste(Image.open(a).crop((0,3840,4096,4096)),(0,0));out.paste(Image.open(b).crop((0,0,4096,256)),(0,256))
qa=ZONE/'qa/r05_c13-upper-border-round2';qa.mkdir(exist_ok=True)
for j in range(4):out.crop((j*1024,0,(j+1)*1024,512)).save(qa/f'segment-{j+1}-100pct.png')
write(qa/'record.json',dict(upper=dict(file=a.as_posix(),sha256=sha(a)),lower=dict(file=b.as_posix(),sha256=sha(b)),operation='exact native256 strips joined without resizing',review='pending'))


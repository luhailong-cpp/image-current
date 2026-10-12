from pathlib import Path
p=Path('tools/build_preview.py')
s=p.read_text(encoding='utf-8')
start="const cp=frame.contactPosition;const contact=cp?"
a=s.index(start);b=s.index("$('frame-meta').textContent=contact+",a)
declaration=s[a:b]
s=s[:a]+s[b:]
s=s.replace("$('frame-meta').textContent=contact+`帧", "$('frame-meta').textContent=`帧",1)
needle="$('sprite').src=frame.url;$('sprite').hidden=false;$('empty').hidden=true;$('frame-meta').textContent="
assert needle in s
s=s.replace(needle,"$('sprite').src=frame.url;$('sprite').hidden=false;$('empty').hidden=true;"+declaration+"$('frame-meta').textContent=contact+",1)
p.write_text(s,encoding='utf-8')

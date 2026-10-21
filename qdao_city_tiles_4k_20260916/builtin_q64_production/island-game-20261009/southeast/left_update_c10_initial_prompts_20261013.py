from workflow import ROOT,read,write,sha,now
for rc in ['11','14']:
 f=ROOT/'prompts'/f'r13_c10_p{rc}_v01.request.json';r=read(f);p=__import__('pathlib').Path(r['promptPath']);s=p.read_text(encoding='utf-8')
 if rc=='11':s=s.replace('existing dark green vegetation only where shown in the bottom-right layout.', 'bare stone fills this entire close crop, with no vegetation or flowers.')
 else:s=s.replace('Tall bare rounded tan-gray coastal rock planes and clear blue sea at the right margin,', 'Tall rounded tan-gray coastal rock planes filling the right side; only the tiny blue sea sliver at the upper-left where shown,')
 p.write_text(s,encoding='utf-8');r['promptSha256']=sha(p);r['updatedBeforeSubmissionAt']=now();write(f,r)
print('Corrected scene wording to actual viewed guides before submission')

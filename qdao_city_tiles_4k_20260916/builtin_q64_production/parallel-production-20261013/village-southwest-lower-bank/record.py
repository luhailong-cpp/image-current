from produce import *
stem=sys.argv[1]; p=ROOT/'native'/f'{stem}.png'; req=json.loads((ROOT/'requests'/f'{stem}.json').read_text())
receipt=ROOT/'native'/f'{stem}.receipt.json'
if receipt.exists():
    rr=json.loads(receipt.read_text());req['prompt']=rr['prompt'];req['receipt']=receipt.as_posix()
    if 'references' in rr: req['references']=[{**r,'sha256':sha(r['path'])} for r in rr['references']]
im=Image.open(p); assert im.size==(1254,1254),im.size
rec={**req,'file':p.as_posix(),'sha256':sha(p),'nativeDimensions':list(im.size),'selected':True,'status':'quick_layout_pass_internal_seams_pending','actualModel':None,'modelEvidence':'Built-in tool returned no model identifier; no paid API used','nativePixelsResampled':False,'savedAtUtc':datetime.now(timezone.utc).isoformat()}
write(ROOT/'native'/f'{stem}.generation.json',rec)
records=[json.loads(p.read_text()) for p in (ROOT/'native').glob('*.generation.json')]
selected={(r['tile'],r['patch']) for r in records if r.get('selected')}
write(ROOT/'selected-sources.json',{'sources':[{'tile':r['tile'],'patch':r['patch'],'file':r['file'],'sha256':r['sha256']} for r in records if r.get('selected')],'uniqueSelectedCores':len(selected),'generatedVersions':len(records)})
write(ROOT/'progress.json',{'status':'native_production','current':stem,'selectedCores':len(selected),'generatedNativeFiles':len(records),'targetCores':32,'complete4kCount':0,'internalPassed4kCount':0,'actualModel':None,'rejectedOrSupersededFiles':len([r for r in records if not r.get('selected')]),'updatedAtUtc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'file':p.as_posix(),'sha256':rec['sha256'],'dimensions':im.size}))

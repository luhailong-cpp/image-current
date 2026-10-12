from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
z=Path(__file__).resolve().parent
src=Path('C:/Users/luyua/.codex/generated_images/01a1296e-842b-7612-a54f-33f30f70b44f')
items=[('r04_c02_repair_eastupper_a01','exec-1ff259bb-82e7-4eea-a7c9-30ca398d6dd7.png',True),('r04_c02_repair_eastroof_a01','exec-1e66a365-606f-4657-91cf-1c24263c3b8f.png',False)]
for stem,filename,returned in items:
 p=z/'prompts'/f'{stem}.prompt.txt'
 refs=json.loads((z/'guides'/f'{stem}.references.json').read_text(encoding='utf-8'))
 refs=refs if isinstance(refs,list) else refs['inputs']
 f=src/filename
 r=dict(tool='image_gen.imagegen',route='builtin',submitted=dict(promptText=p.read_text(encoding='utf-8'),promptFile=p.as_posix(),referenced_image_paths=[x['path'] for x in refs],transparent_background=False,model=None,quality=None),returned=dict(output_hint=(f'Generated images are saved as {f.as_posix()} by default.' if returned else None),actualModel=None,actualQuality=None,receiptRecoveredFromFilesystem=not returned,originalResponseAvailable=returned),generatedFile=f.as_posix(),generatedFileSha256=hashlib.sha256(f.read_bytes()).hexdigest(),archivedAtUtc=datetime.now(timezone.utc).isoformat(),migrationRecovery=dict(execCell='105',waitResult='exec cell 105 not found after migration NEW_TASK; store lifetime ended',mappingEvidence='eastupper output path was shown in completed subresult; eastroof is the sole subsequent PNG in the same output directory, visually identified as the requested exact roof crop',newGenerationRequested=False,acceptedOrMerged=False))
 with (z/'receipts'/f'{stem}.receipt.json').open('x',encoding='utf-8') as h: json.dump(r,h,ensure_ascii=False,indent=2)
 print(json.dumps(dict(stem=stem,source=f.as_posix(),sha256=r['generatedFileSha256'],originalResponseAvailable=returned)))


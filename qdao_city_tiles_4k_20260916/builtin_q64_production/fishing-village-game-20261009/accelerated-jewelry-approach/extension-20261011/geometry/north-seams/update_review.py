from pathlib import Path
import json, datetime
p=Path(__file__).with_name('partial-qa.json')
d=json.loads(p.read_text(encoding='utf-8'))
findings={
 'r05_c10-north-c1':'原尺寸复看：红木立面、浅木器架直杆和斜横杆在北边连续，无轮廓跳变；南侧木纹略粗、笔触略亮，属于局部材质差异，未形成贯穿水平色带，不建议仅为此返工。',
 'r05_c11-north-c4':'原尺寸复看：蓝瓦排布、弧面高光、金檐斜边连续，无瓦沟错位或直切；新侧笔触稍细碎，未见明显接缝线，不建议返工。',
 'r05_c11-north-c3':'p13-v2原尺寸复看：斜石缝、左侧金绳及灰白网缘、右侧金檐卷角与木构连续。浅砂/灰石纹理有细小变化，但无物体断裂或硬水平带。'}
for e in d['segments']:
    if e['segment'] in findings and e['status']!='waiting_for_selected_native':
        e['status']='reviewed_candidate_no_repair_requested'
        e['visualFindings']=findings[e['segment']]
d['reviewedSegments']=sum(e['status'].startswith('reviewed') for e in d['segments'])
d['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
d['formalAccepted']=False
d['currentConclusion']='3/8 northern boundary segments visually reviewed; no true geometry break found. Awaiting remaining first-row natives, especially repaired net continuation r05_c11 p11/p12. Exterior formal acceptance remains false.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(d['currentConclusion'])

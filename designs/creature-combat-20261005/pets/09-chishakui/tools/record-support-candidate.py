from pathlib import Path
from PIL import Image
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
for arg in sys.argv[1:]:
    p=ROOT/arg; r=json.loads(p.read_text(encoding='utf-8')); src=Path(r['sourcePath'])
    with Image.open(src) as im:
        native={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
        im=im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS); pix=im.load(); metrics={}
        for label,(x0,x1) in {'screenLeft':(280,490),'screenRight':(575,780)}.items():
            points=[]
            for y in range(875,980):
                for x in range(x0,x1):
                    red,green,blue,a=pix[x,y]
                    if a>=128 and blue>red*1.15 and blue>green*1.06 and red<155:points.append((x,y))
            metrics[label]={'blueCentroid':[round(sum(x for x,y in points)/len(points),3),round(sum(y for x,y in points)/len(points),3)],'matchedPixels':len(points)}
        metrics['alpha16Bbox']=im.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox()
    config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
    out={'file':r['sourcePath'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generatedAt':r['completedAt'],'native':native,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':r['references'],'promptFile':r['promptFile']},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool does not expose or return model/quality metadata.','evidence':{'receipt':arg,'output_hint':r.get('output_hint')},'referenceEvidenceAtSubmission':[{'path':x,'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in r['references']],'metrics':metrics,'metricCaution':'Color-region centroid only, not anatomical or skeleton coordinates; corroborate by actual visual inspection.','visualStatus':r.get('visualStatus')}
    p.with_name(p.name.replace('.receipt.json','.native.generation.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'receipt':arg,'native':native,'metrics':metrics}))

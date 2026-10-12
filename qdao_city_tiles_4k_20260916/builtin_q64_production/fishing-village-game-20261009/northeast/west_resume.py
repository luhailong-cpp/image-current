from pathlib import Path
import argparse,json,uuid
import west_sol as w
def prepare(p,v,subject):
 w.prepare(p,v,subject,'guide')
 planp=w.R/f'{p}-{v}.plan.json';d=w.read(planp);refs=d['references'];d['references']=[refs[3],refs[0],refs[1],refs[2]]
 d['references'][0]['role']='PRIMARY EDIT TARGET: exact coordinate frame and sharp native edge anchors'
 d['guidePurpose']='Layout-only guide as first edit target; native sharp anchors remain at exact coordinates; reference images are style/layout only'
 prompt=f'''Edit IMAGE 1 only. Replace its blurred interior with crisp hand-painted native art, making the existing sharp top and right edge strips continue naturally into the same square. Preserve image 1 EXACT frame, object position, scale, camera and top/right edge geometry. Do not borrow scene composition from images 2, 3 or 4. Image 2 is the whole-map placement reference, image 3 supplies daylight material/rendering quality only, image 4 supplies rounded Daoist Q painterly style only. No inset panels, divider, text, UI, people, border or watermark. Output exactly 1254x1254 opaque square, coordinate {p}, native world box {d['coordinates']['nativeGlobalBox']}, core [115,115,1139,1139], halo 115. Join each original contour entering from the sharp image 1 top230 and right230 edge anchors; anchors take precedence over blurred details. No shifted contours, repeated props, exposure stripe or blurry final pixels.\nSpecific scene: {subject}'''
 (w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
 for path,obj in [(planp,d),(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in d['references']],transparent_background=False))]:
  tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('patch');a.add_argument('--version',default='v1');a.add_argument('--subject',required=True);q=a.parse_args();prepare(q.patch,q.version,q.subject)

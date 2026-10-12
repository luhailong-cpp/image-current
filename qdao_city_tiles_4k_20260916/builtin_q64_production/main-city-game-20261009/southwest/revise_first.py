from production import *
reject=T/'rejected'/'p01_01.attempt02';reject.mkdir(parents=True,exist_ok=True)
old=T/'native'/'p01_01.png';recpath=Path(str(old)+'.generation.json')
rec=json.loads(recpath.read_text(encoding='utf-8'))
for sub,filename in [('prompts','p01_01.prompt.txt'),('prompts','p01_01.request.json'),('receipts','p01_01.receipt.json')]:
    shutil.copy2(T/sub/filename,reject/filename)
shutil.move(str(old),str(reject/'p01_01.png'))
rec.update({'file':str(reject/'p01_01.png'),'prompt':str(reject/'p01_01.prompt.txt'),'disposition':'rejected_wrong_framing','reason':'Rail, banner, stairs, plaza absent from exact mapped guide. Not usable native map coverage.'})
rec['evidence']['toolReceipt']=str(reject/'p01_01.receipt.json')
write(reject/'p01_01.png.generation.json',rec);recpath.unlink()
req=json.loads((T/'prompts'/'p01_01.request.json').read_text(encoding='utf-8'))
req['prompt']='''Use case: precise-object-edit. Edit ONLY image 1, the pixelated tan wood guide. Produce a 1254x1254 opaque native painted crop of this SAME small floor area. Images 2,3,4 are context/style references ONLY. The output must look like a macro-close square sample of wooden arena floor, with precisely the same shapes and placement as image 1.\nCRITICAL EXACT COMPOSITION: The entire square is flat warm honey-tan wooden planks seen from the fixed overhead game-map camera. Broad long horizontal board divisions at approximately y=0, 140, 300, 450, 620, 790, 930, 1090 and 1240, with clean warm-toned seams. A single smooth cream painted arc enters the TOP EDGE at x=640, curves downward and right, and exits the RIGHT EDGE at y=630. Line width about 50 pixels, flat paint on the wood. At the extreme top right corner, keep the tiny sliver of a second cream stroke shown in the guide. The lower half is entirely uninterrupted wood. No railings, no posts, no red flags, no grey stone, no stairs, no buildings, no ground outside the arena, no full emblem, no black character. Those objects are outside this tiny crop and MUST NOT appear.\nCreate fresh sharp hand-painted native wood detail: gently rounded clean plank edges, modest warm wood grain flowing horizontally, restrained painted shading, daylight matching image 3, refined Daoist chibi finish of image 4. Image 2 explains that this is a tiny piece of the wooden arena, not permission to include anything else. Preserve exact crop/framing of image 1. Do not zoom out. Do not turn it into a showcase object. Do not leave large pixel blocks. No text, border, grid or watermark.\n'''
(T/'prompts'/'p01_01.prompt.txt').write_text(req['prompt'],encoding='utf-8');write(T/'prompts'/'p01_01.request.json',req)
progress('p01_01 corrected attempt3: strictly wood-only macro crop and cream arc. 1 native returned, 0 usable; no 4K candidate.')

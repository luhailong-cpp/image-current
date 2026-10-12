from native_work import *
p=ZONE/'progress.json'; q=read(p)
for error in q['errors']:
    if error['stage']=='r03_c13_p02_02 attempt1': error['resolved']=True; error['recovery']='same builtin request succeeded on attempt2; native output saved and inspected'
q['status']='adjacent_native_generation_and_local_repair'; q['currentPatch']='r03_c13_p02_03'; q['nextStep']='Generate rock/lantern support fragment; native_column repairs p02_02 and continues column2'; q['updatedAtUtc']=now(); write(p,q)

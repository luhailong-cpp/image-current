"""Prepare an isolated, byte-preserving CURRENT snapshot: one root, no history.

No arguments/--help/status are read-only. Only explicit prepare writes a new
private run below this script's directory. No work files, live Git metadata,
network, purchases or publication are changed. Requires Python 3.11+ and Git.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import uuid

ROOT=Path(r'D:\work\image')
WORK=Path(__file__).absolute().parent
GIT=Path(r'C:\Program Files\Git\ucrt64\bin\git.exe')
POLICY='current-only-single-root-no-history'
REF='refs/heads/codex/current-only-lfs-20261012'
DOCS='docs/current-only-migration-20261012'
CHUNK=4*1024*1024
BINARY=frozenset(('.png .jpg .jpeg .webp .gif .apng .bmp .tif .tiff .ico '
 '.mp4 .mov .webm .avi .wav .mp3 .ogg .zip .7z .rar .npz .npy .bin '
 '.psd .kra .blend .fbx .glb .ttf .otf .pyd .dll .exe .whl .pdf .docx .xlsx .pptx').split())
GATES=('after_required_dependency_restoration','obsolete_flow_cleanup_reviewed',
 'current_designs_preserved','current_characters_and_pets_preserved',
 'current_ui_and_festival_assets_preserved','all_current_previews_preserved',
 'all_three_current_maps_preserved','required_sources_and_runtime_dependencies_preserved')

def require(ok,message):
    if not ok:raise RuntimeError(message)

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def physical(path):
    p=Path(path).absolute()
    for x in [p,*p.parents]:
        try:s=x.lstat()
        except FileNotFoundError:continue
        require(not stat.S_ISLNK(s.st_mode) and not getattr(s,'st_file_attributes',0)&0x400,
                'Reparse/symlink/junction refused: '+str(x))
    return p.resolve()

def sha(path):
    with physical(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def raw_oid(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def jsbytes(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def new_file(path,data):
    with physical(path).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def load(path):return json.loads(physical(path).read_text('utf-8-sig'))
def clean_env():
    e={k:v for k,v in os.environ.items() if not k.upper().startswith(('GIT_','LFS_'))}
    e.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_OPTIONAL_LOCKS='0',
             GIT_NO_REPLACE_OBJECTS='1',GIT_TERMINAL_PROMPT='0',GIT_LFS_SKIP_SMUDGE='1')
    return e
def command(gitdir,*args):
    return [str(GIT),'--no-optional-locks','--git-dir='+str(gitdir),'-c','core.hooksPath='+os.devnull,
            '-c','core.fsmonitor=false','-c','core.autocrlf=false','-c','gc.auto=0',
            '-c','maintenance.auto=false','-c','protocol.allow=never',*args]
def git(gitdir,*args,data=None):
    p=subprocess.run(command(gitdir,*args),input=data,capture_output=True,env=clean_env())
    require(p.returncode==0,'Git failed '+args[0]+': '+p.stderr.decode('utf-8','replace')[-1500:])
    return p.stdout
def name_ok(name):
    require(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and ':' not in name
            and '\0' not in name and all(x not in ('','.','..') and not x.endswith((' ','.'))
            for x in name.split('/')),'Unsafe repository path: '+repr(name))
    require(all(x.casefold()!='.git' for x in name.split('/')),'Git internal path refused')
    return name
def qpath(name):
    # Git C quoting uses byte octal escapes, never JSON's Unicode escapes.
    return b'"'+b''.join(bytes((v,)) if 32<=v<127 and v not in (34,92) else
                        ('\\%03o'%v).encode() for v in name.encode('utf-8'))+b'"'
def sig(s):
    return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,getattr(s,'st_birthtime_ns',s.st_ctime_ns))
def strow(s):return {'size':s.st_size,'mtime_ns':s.st_mtime_ns,'device':s.st_dev,'inode':s.st_ino,
                     'birthtime_ns':getattr(s,'st_birthtime_ns',s.st_ctime_ns)}
def fingerprint(root):
    d=root/'.git'
    return {'files':{n:sha(d/n) if (d/n).is_file() else None for n in
                     ('HEAD','index','config','packed-refs','shallow','info/grafts')},
            'refs_sha256':hashlib.sha256(git(d,'for-each-ref','--format=%(refname) %(objectname)')).hexdigest()}
def rows(path):
    p=physical(path)
    if p.suffix.lower()=='.jsonl':
        return [json.loads(line) for line in p.read_text('utf-8-sig').splitlines() if line.strip()]
    v=load(p);return v if isinstance(v,list) else v['entries']
def unique_rows(rr):
    result={};fold=set()
    for r in rr:
        n=name_ok(r['path']);require(n not in result and n.casefold() not in fold,'Duplicate/case-colliding path: '+n)
        require(isinstance(r['size'],int) and not isinstance(r['size'],bool) and r['size']>=0,'Invalid file size')
        result[n]=r;fold.add(n.casefold())
    return result

def scan(root):
    result={};fold=set();stack=[root]
    while stack:
        directory=stack.pop()
        for e in os.scandir(physical(directory)):
            if directory==root and e.name.casefold()=='.git':continue
            p=physical(e.path);s=p.stat()
            if stat.S_ISDIR(s.st_mode):stack.append(p);continue
            require(stat.S_ISREG(s.st_mode),'Only regular current files supported: '+str(p))
            n=name_ok(p.relative_to(root).as_posix())
            require(n.casefold() not in fold,'Case-colliding source path: '+n);fold.add(n.casefold())
            result[n]=strow(s)
    return result

def check_scan(actual,inventory,omissions):
    require(set(actual)-set(omissions)==set(inventory),'Current source path set differs from approved inventory/omissions')
    for n,r in inventory.items():
        require(actual[n]['size']==r['size'] and actual[n]['mtime_ns']==r['mtime_ns'],
                'Current source size/time differs from approved inventory: '+n)

class Importer:
    def __init__(self,gitdir,run):
        self.errors=(run/'fast-import.stderr').open('xb');self.next=1;self.ids={}
        self.p=subprocess.Popen(command(gitdir,'fast-import','--quiet','--done'),stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL,stderr=self.errors,env=clean_env())
    def send(self,data):self.p.stdin.write(data)
    def blob(self,data=None,stream=None,size=None,oid=None):
        if oid in self.ids:return self.ids[oid]
        mark=':'+str(self.next);self.next+=1
        if data is not None:size=len(data)
        self.send(b'blob\nmark '+mark.encode()+b'\ndata '+str(size).encode()+b'\n')
        if data is not None:self.send(data)
        else:
            left=size
            while left:
                b=stream.read(min(left,CHUNK));require(b,'Short private ordinary spool');self.send(b);left-=len(b)
        self.send(b'\n');self.ids[oid]=mark;return mark
    def finish(self,entries,epoch):
        msg=b'Current complete artwork snapshot; previous Git history intentionally omitted.\n'
        self.send(b'commit '+REF.encode()+b'\ncommitter Image migration <local@invalid> '+str(epoch).encode()+b' +0000\n')
        self.send(b'data '+str(len(msg)).encode()+b'\n'+msg+b'deleteall\n')
        for n,r in sorted(entries.items()):
            self.send(b'M '+r['mode'].encode()+b' '+r['import_id'].encode()+b' '+qpath(n)+b'\n')
        self.send(b'\ndone\n');self.p.stdin.close();rc=self.p.wait();self.errors.close()
        require(rc==0,'Private fast-import failed; run and stderr retained')
    def abort(self):
        try:self.p.stdin.close()
        except (OSError,ValueError):pass
        if self.p.poll() is None:self.p.terminate();self.p.wait()
        self.errors.close()

def batch_existing(gitdir,identities):
    if not identities:return set()
    data=''.join(oid+'\n' for oid in identities).encode()
    rr=git(gitdir,'cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)',data=data).splitlines()
    require(len(rr)==len(identities),'Wrong batch-check result length');present=set()
    for (oid,size),r in zip(identities.items(),rr):
        fields=r.split()
        if len(fields)==2 and fields[1]==b'missing':continue
        require(fields==[oid.encode(),b'blob',str(size).encode()],'Existing ordinary object type/size mismatch')
        present.add(oid)
    return present

VERIFIER = '''"""Verify the committed current snapshot and hydrated working bytes (Python 3.11+)."""
import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[2]
here=pathlib.Path(__file__).resolve().parent
ledger=here/'data-ledger.jsonl'
receipt=json.loads((here/'receipt.json').read_text('utf-8'))
assert hashlib.sha256(ledger.read_bytes()).hexdigest()==receipt['data_ledger_sha256'],'ledger hash'
for name,digest in receipt['portable_files'].items():
 with (root/name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest,name+' portable evidence'
cmd=['git','-C',str(root),'-c','core.autocrlf=false']
tree={}
for part in subprocess.check_output(cmd+['ls-tree','-r','-z','HEAD']).split(b'\\0'):
 if part:
  info,path=part.split(b'\\t',1);mode,kind,oid=info.decode().split();tree[path.decode()]=(mode,oid)
count=0;data_paths=set()
for line in ledger.read_text('utf-8').splitlines():
 r=json.loads(line);p=root/r['path'];assert tree.get(r['path'])==(r['mode'],r['oid']),r['path']+' Git identity'
 data_paths.add(r['path'])
 assert p.is_file() and p.stat().st_size==r['payload_bytes'],r['path']+' absent/unhydrated/size'
 with p.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 assert actual==r['payload_sha256'],r['path']+' working bytes'
 count+=1
assert count==receipt['data_path_count'] and len(data_paths)==count,'data path count'
assert set(tree)==data_paths|set(receipt['portable_files'])|{str((here/'receipt.json').relative_to(root)).replace('\\\\','/')},'complete tree path set'
print(json.dumps({'passed':True,'verified_data_paths':count,'working_bytes_checked':True,
 'publication_or_migration_complete':False}))
'''

class Builder:
    def __init__(self,root=ROOT,work=WORK):
        self.root=physical(root);self.work=physical(work)
        require(self.root/'.git' in self.work.parents,'Private work must be inside source .git')
        physical(self.root/'.git/objects')
    def validate(self,input_file,input_sha):
        ip=physical(input_file);require(sha(ip)==input_sha,'Approved input hash differs');s=load(ip)
        require(s.get('schema_version')==1 and s.get('approved') is True and s.get('policy')==POLICY,'Reviewed current-only approval required')
        require(physical(s['repository'])==self.root,'Wrong source repository')
        require(all(s.get('required_preservation_checks',{}).get(k) is True for k in GATES),'Current preservation checks incomplete')
        require(s.get('source_frozen') is True and s.get('expected_parent_count')==0,'Frozen source and zero-parent policy required')
        pins={'approval':{'path':str(ip),'sha256':input_sha},
              'source_inventory':{'path':s['source_inventory_file'],'sha256':s['source_inventory_sha256']},
              'protected_roster':{'path':s['protected_roster_file'],'sha256':s['protected_roster_sha256']},
              'authorized_absent_roster':{'path':s['authorized_absent_roster_file'],'sha256':s['authorized_absent_roster_sha256']}}
        ev=s.get('evidence_pins',{})
        require(all(k in ev for k in ('freeze','restoration','authorized_cleanup')),'Missing required frozen/restoration/cleanup evidence')
        for role,pin in ev.items():
            require(re.fullmatch('[a-z][a-z0-9_-]*',role) and role not in pins,'Invalid/duplicate evidence role')
            pins[role]=pin
        for p in pins.values():
            require(re.fullmatch('[0-9a-f]{64}',p['sha256']) and sha(p['path'])==p['sha256'],'Pinned evidence differs')
        inventory=unique_rows(rows(s['source_inventory_file']));require(inventory,'Empty current inventory')
        for r in inventory.values():
            require(isinstance(r.get('mtime_ns'),int) and r.get('mode') in ('100644','100755'),'Inventory requires mtime_ns and explicit regular Git mode')
        protected=unique_rows(rows(s['protected_roster_file']));require(protected,'Empty current protected roster')
        require(len(protected)==s.get('expected_protected_path_count'),'Protected roster count differs')
        for n,r in protected.items():
            require(n in inventory and r['size']==inventory[n]['size'] and re.fullmatch('[0-9a-f]{64}',r.get('sha256','')),
                    'Protected path missing/invalid in inventory: '+n)
        absent=unique_rows(rows(s['authorized_absent_roster_file']))
        require(len(absent)==s.get('expected_authorized_absent_count') and not (set(absent)&set(inventory)),
                'Authorized screenshot absence roster differs or includes a retained path')
        omissions={}
        for r in s.get('approved_omissions',[]):
            n=name_ok(r['path']);require(n not in omissions and n not in inventory and r.get('reason'),'Invalid approved omission')
            omissions[n]=r
        require(not any(n==DOCS or n.startswith(DOCS+'/') for n in inventory),'Portable docs path already exists; refuse overwrite')
        extra=set(s.get('additional_lfs_paths',[]))
        require(all(n in inventory for n in extra),'Additional LFS path not current')
        require(s.get('attributes_overlay_approved') is True,'Candidate-only byte-preserving/LFS attributes overlay must be approved')
        return s,pins,inventory,protected,omissions,extra,absent

    def run(self,input_file,input_sha,run_id=None):
        spec,pins,inventory,protected,omissions,extra,absent=self.validate(input_file,input_sha)
        before=fingerprint(self.root);initial=scan(self.root);check_scan(initial,inventory,omissions)
        require(not (set(absent)&set(initial)),'Authorized deleted screenshot reappeared on disk')
        lock=physical(self.work/'current-only-snapshot.lock');token=uuid.uuid4().hex
        with lock.open('x',encoding='ascii') as f:
            identity=os.fstat(f.fileno());f.write(token);f.flush();os.fsync(f.fileno())
        run=None;imp=None
        try:
            self.validate(input_file,input_sha)
            require(fingerprint(self.root)==before,'Live Git metadata changed before preparation')
            rid=run_id or uuid.uuid4().hex;require(re.fullmatch('[a-zA-Z0-9_-]{1,80}',rid),'Invalid private run id')
            run=physical(self.work/('current-only-'+rid));require(not run.exists(),'Existing private run is preserved; inspect it or use a new run id')
            run.mkdir();new_file(run/'intent.json',jsbytes({'input':str(input_file),'input_sha256':input_sha,'policy':POLICY,
                'created_utc':now(),'script_sha256':sha(__file__),'live_git_before':before,'network':False}))
            bare=run/'snapshot.git'
            subprocess.run([str(GIT),'init','--bare','--template=','--object-format=sha1','--initial-branch=codex/current-only-lfs-20261012',str(bare)],
                           check=True,capture_output=True,env=clean_env())
            physical(bare/'objects/info');new_file(bare/'objects/info/alternates',(str(self.root/'.git/objects').replace('\\','/')+'\n').encode())
            # The alternate is read-only object reuse. No historical ref/commit is imported.
            lfs=bare/'lfs/objects';lfs.mkdir(parents=True);temps=run/'payload-tmp';temps.mkdir()
            new_file(run/'inventory-before.json',jsbytes(initial))
            spool=run/'ordinary-spool.bin';data={};ordinary={};cache={};source_ledger=[];original_attrs=None
            with spool.open('xb') as sf:
                for index,n in enumerate(sorted(inventory)):
                    if index%2000==0:print(json.dumps({'phase':'source-pass-1','paths':index,'total':len(inventory)}),flush=True)
                    p=physical(self.root/n);r=inventory[n];selected=(Path(n).suffix.lower() in BINARY or n in extra) and r['size']>0
                    temp=temps/(uuid.uuid4().hex+'.tmp') if selected else None
                    dst=temp.open('xb') if selected else sf;offset=sf.tell();sh=hashlib.sha256();gh=hashlib.sha1(b'blob '+str(r['size']).encode()+b'\0');count=0;prefix=b''
                    try:
                        with p.open('rb') as src:
                            first=os.fstat(src.fileno());require(strow(first)==initial[n],'Source changed before read: '+n)
                            for b in iter(lambda:src.read(CHUNK),b''):
                                if len(prefix)<1024:prefix=(prefix+b)[:1024]
                                dst.write(b);sh.update(b);gh.update(b);count+=len(b)
                            require(sig(first)==sig(os.fstat(src.fileno()))==sig(p.stat()),'Source changed during first read: '+n)
                        if selected:dst.flush();os.fsync(dst.fileno())
                    finally:
                        if selected:dst.close()
                    require(count==r['size'],'Source size changed: '+n)
                    require(not (selected and prefix.startswith(b'version https://git-lfs.github.com/spec/')),
                            'Unhydrated LFS pointer source refused: '+n)
                    digest=sh.hexdigest();oid=gh.hexdigest()
                    if n in protected:require(protected[n]['sha256']==digest,'Protected source SHA mismatch: '+n)
                    if 'sha256' in r:require(r['sha256']==digest,'Approved source SHA mismatch: '+n)
                    row={'path':n,'mode':r['mode'],'source_bytes':count,'source_sha256':digest,'raw_oid':oid,'source_stat':initial[n],
                         'kind':'lfs' if selected else 'ordinary'}
                    if selected:
                        require(digest not in cache or cache[digest]['size']==count,'Conflicting payload identity')
                        canonical=physical(lfs/digest[:2]/digest[2:4]/digest)
                        if digest not in cache:
                            require(sha(temp)==digest,'Private LFS copied bytes hash mismatch');canonical.parent.mkdir(parents=True,exist_ok=True)
                            require(not canonical.exists(),'Unexpected private canonical LFS object')
                            os.link(temp,canonical);cache[digest]={'sha256':digest,'size':count,'storage_path':str(canonical)}
                        temp.unlink()
                        pointer=('version https://git-lfs.github.com/spec/v1\noid sha256:'+digest+'\nsize '+str(count)+'\n').encode()
                        data[n]={'mode':r['mode'],'oid':raw_oid(pointer),'git_bytes':len(pointer),'payload_bytes':count,
                                 'payload_sha256':digest,'pointer':pointer,'lfs_sha256':digest}
                    else:
                        require(count<=100*1024*1024,'Ordinary blob exceeds 100 MiB; explicitly classify it for LFS: '+n)
                        ordinary[oid]=count
                        data[n]={'mode':r['mode'],'oid':oid,'git_bytes':count,'payload_bytes':count,'payload_sha256':digest,'offset':offset}
                    source_ledger.append(row)
                    if n=='.gitattributes':
                        require(count<16*1024*1024 and not selected,'Unexpected attributes size/type')
                        pos=sf.tell();sf.flush()
                        with spool.open('rb') as a:a.seek(offset);original_attrs=a.read(count)
                sf.flush();os.fsync(sf.fileno())
            # The second and last source content pass verifies every included file.
            recheck=[]
            for index,row in enumerate(source_ledger):
                if index%2000==0:print(json.dumps({'phase':'source-pass-2','paths':index,'total':len(inventory)}),flush=True)
                n=row['path'];p=physical(self.root/n)
                with p.open('rb') as src:
                    first=os.fstat(src.fileno());require(strow(first)==initial[n],'Source changed before second read: '+n)
                    digest=hashlib.file_digest(src,'sha256').hexdigest()
                    require(sig(first)==sig(os.fstat(src.fileno()))==sig(p.stat()),'Source changed during second read: '+n)
                require(digest==row['source_sha256'],'Source bytes changed between passes: '+n)
                recheck.append({'path':n,'size':row['source_bytes'],'sha256':digest})
            final_scan=scan(self.root);require(final_scan==initial,'Current path inventory changed during capture')
            self.validate(input_file,input_sha);require(fingerprint(self.root)==before,'Live Git metadata changed during capture')
            new_file(run/'inventory-after.json',jsbytes(final_scan))
            new_file(run/'source-recheck.jsonl',b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode() for r in recheck))
            source_bytes=b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode() for r in source_ledger)
            new_file(run/'source-ledger.jsonl',source_bytes)
            attr_parts=[original_attrs or b'',b'\n# Current-only portable snapshot: raw bytes, no newline/encoding filters.\n* -text -filter -ident -working-tree-encoding\n']
            for n,r in sorted(data.items()):
                if 'lfs_sha256' in r:attr_parts.append(qpath(n)+b' filter=lfs diff=lfs merge=lfs -text -ident -working-tree-encoding\n')
            attrs=b''.join(attr_parts)
            def generated(n,content):
                data[n]={'mode':'100644','oid':raw_oid(content),'git_bytes':len(content),'payload_bytes':len(content),
                         'payload_sha256':hashlib.sha256(content).hexdigest(),'content':content}
            generated('.gitattributes',attrs)
            data_ledger=b''.join((json.dumps({'path':n,**{k:r[k] for k in ('mode','oid','git_bytes','payload_bytes','payload_sha256')},
                                 **({'lfs_sha256':r['lfs_sha256']} if 'lfs_sha256' in r else {})},ensure_ascii=False)+'\n').encode()
                                for n,r in sorted(data.items()))
            portable={DOCS+'/source-ledger.jsonl':source_bytes,DOCS+'/data-ledger.jsonl':data_ledger,
                      DOCS+'/inventory-before.json':jsbytes(initial),DOCS+'/inventory-after.json':jsbytes(final_scan),
                      DOCS+'/source-recheck.jsonl':(run/'source-recheck.jsonl').read_bytes(),DOCS+'/verify_current_snapshot.py':VERIFIER.encode()}
            evidence_map={}
            for role,pin in sorted(pins.items()):
                source=physical(pin['path']);content=source.read_bytes();require(hashlib.sha256(content).hexdigest()==pin['sha256'],'Evidence changed before portable copy')
                target=DOCS+'/evidence/'+role+source.suffix.lower();portable[target]=content
                evidence_map[role]={'path':target,'sha256':pin['sha256'],'original_path':str(source)}
            if original_attrs is not None:portable[DOCS+'/original-root-gitattributes.txt']=original_attrs
            receipt={'schema_version':1,'policy':POLICY,'source_path_count':len(source_ledger),'data_path_count':len(data),
                     'source_ledger_sha256':hashlib.sha256(source_bytes).hexdigest(),'data_ledger_sha256':hashlib.sha256(data_ledger).hexdigest(),
                     'source_recheck_sha256':sha(run/'source-recheck.jsonl'),'source_two_passes_equal':True,
                     'inventory_before_after_equal':True,'protected_path_count':len(protected),'evidence':evidence_map,
                     'lfs_payloads':[{'sha256':k,'size':v['size']} for k,v in sorted(cache.items())],
                     'historical_commits_included':0,'expected_root_parent_count':0,'network_or_push':False,
                     'publication_complete':False,'migration_complete':False,'receipt_has_no_self_commit_reference':True}
            portable[DOCS+'/receipt.json']=jsbytes(receipt)
            portable[DOCS+'/README.txt']=(
                'CURRENT SNAPSHOT, NO PREVIOUS HISTORY\nPython 3.11+ and Git LFS are needed on the new computer.\n'
                'Before checkout use: git config core.autocrlf false\nAfter clone/install: git lfs pull\n'
                'Verify hydrated images AND ordinary source bytes: python '+DOCS+'/verify_current_snapshot.py\n'
                'This receipt records local preparation only. It is not evidence of remote storage, publication or full migration.\n'
                'source-ledger preserves every approved source byte identity; data-ledger describes candidate data, with only a reviewed attributes overlay.\n'
                'All evidence files and source/recheck inventories are committed here; no old-machine .git file is required to read them.\n').encode()
            receipt['portable_files']={n:hashlib.sha256(content).hexdigest() for n,content in portable.items() if n!=DOCS+'/receipt.json'}
            portable[DOCS+'/receipt.json']=jsbytes(receipt)
            for n,content in portable.items():generated(n,content)
            existing=batch_existing(bare,ordinary);imp=Importer(bare,run)
            with spool.open('rb') as sf:
                for n,r in sorted(data.items()):
                    if 'content' in r:r['import_id']=imp.blob(data=r['content'],oid=r['oid'])
                    elif 'pointer' in r:r['import_id']=imp.blob(data=r['pointer'],oid=r['oid'])
                    elif r['oid'] in existing:r['import_id']=r['oid']
                    else:sf.seek(r['offset']);r['import_id']=imp.blob(stream=sf,size=r['git_bytes'],oid=r['oid'])
            imp.finish(data,int(dt.datetime.now(dt.timezone.utc).timestamp()));imp=None
            commit=git(bare,'rev-parse',REF).decode().strip();tree=git(bare,'rev-parse',REF+'^{tree}').decode().strip()
            require(git(bare,'rev-list','--parents','-n','1',REF).decode().split()==[commit],'Candidate is not a single zero-parent root')
            require(git(bare,'rev-list','--count',REF).strip()==b'1','Historical ancestry entered candidate')
            require(git(bare,'for-each-ref','--format=%(refname)').decode().splitlines()==[REF],'Unexpected candidate refs')
            require(not git(bare,'remote').strip(),'Unexpected private remote')
            # Copy ONLY this root's reachable ordinary objects out of the read-
            # only alternate, then remove the borrowed-store dependency. Never
            # use --local here: it would deliberately omit borrowed blobs.
            git(bare,'repack','-a','-d')
            (bare/'objects/info/alternates').unlink()
            git(bare,'fsck','--strict','--no-reflogs',commit)
            observed={}
            for part in git(bare,'ls-tree','-r','-l','-z',REF).split(b'\0'):
                if not part:continue
                info,path=part.split(b'\t',1);mode,kind,oid,size=info.decode().split();require(kind=='blob','Nonblob in candidate')
                observed[path.decode('utf-8')]=(mode,oid,int(size))
            require(observed=={n:(r['mode'],r['oid'],r['git_bytes']) for n,r in data.items()},'Imported whole tree differs from complete ledger')
            # Effective attributes are checked in one private-index batch. Nested
            # attributes can never silently defeat raw bytes or LFS hydration.
            private_env=clean_env();private_env['GIT_INDEX_FILE']=str(run/'verification.index')
            p=subprocess.run(command(bare,'read-tree',commit),capture_output=True,env=private_env);require(p.returncode==0,'Private verification index failed')
            p=subprocess.run(command(bare,'check-attr','--cached','-z','--stdin','filter','text','ident','working-tree-encoding'),
                             input=b''.join(n.encode()+b'\0' for n in data),capture_output=True,env=private_env)
            require(p.returncode==0,'Effective attribute verification failed');parts=p.stdout.split(b'\0');require(parts[-1]==b'','Attribute framing')
            attrs_result={}
            for i in range(0,len(parts)-1,3):attrs_result[(parts[i].decode(),parts[i+1].decode())]=parts[i+2].decode()
            for n,r in data.items():
                require(attrs_result.get((n,'filter'))==('lfs' if 'lfs_sha256' in r else 'unset') and
                        all(attrs_result.get((n,a))=='unset' for a in ('text','ident','working-tree-encoding')),
                        'Nested/conflicting effective byte/LFS attributes: '+n)
            require(scan(self.root)==initial,'Source inventory changed after import');self.validate(input_file,input_sha)
            after=fingerprint(self.root);require(after==before,'Live Git metadata changed before completion')
            report={'schema_version':1,'passed':True,'policy':POLICY,'repository':str(self.root),'isolated_git_dir':str(bare),
                    'candidate_ref':REF,'candidate_commit':commit,'candidate_tree':tree,'parent_count':0,'reachable_commit_count':1,
                    'source_inventory_sha256':spec['source_inventory_sha256'],'approved_input_file':str(input_file),'approved_input_sha256':input_sha,
                    'script_sha256':sha(__file__),'source_path_count':len(inventory),'target_path_count':len(data),'protected_path_count':len(protected),
                    'authorized_screenshots_absent':len(absent),'standalone_objects_no_alternates':True,
                    'source_bytes':sum(r['source_bytes'] for r in source_ledger),'source_passes':2,'catchup_path_count':0,
                    'source_ledger_file':str(run/'source-ledger.jsonl'),'source_ledger_sha256':sha(run/'source-ledger.jsonl'),
                    'lfs_object_count':len(cache),'lfs_unique_bytes':sum(r['size'] for r in cache.values()),
                    'largest_lfs_object_bytes':max((r['size'] for r in cache.values()),default=0),
                    'lfs_objects':list(cache.values()),'ordinary_unique_bytes':sum({r['oid']:r['git_bytes'] for r in data.values() if 'lfs_sha256' not in r}.values()),
                    'portable_receipt_path':DOCS+'/receipt.json','attributes_overlay_only_source_content_change':True,
                    'whole_tree_verified':True,'effective_attributes_verified':True,'source_before_after_equal':True,
                    'live_git_before':before,'live_git_after':after,'live_git_written':False,'working_files_written':False,
                    'network_or_push':False,'publication_complete':False,'migration_complete':False}
            new_file(run/'report.json',jsbytes(report));return {**report,'report_file':str(run/'report.json')}
        except Exception as e:
            if imp:imp.abort()
            if run and run.exists():new_file(run/'failure.json',jsbytes({'passed':False,'error':str(e),'private_partial_files_preserved':True,
                'live_git_written':False,'working_files_written':False,'network_or_push':False}))
            raise
        finally:
            if lock.exists():
                s=lock.lstat()
                if (s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino) and lock.read_text('ascii')==token:lock.unlink()

def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='command');sp.add_parser('status')
    q=sp.add_parser('prepare');q.add_argument('--input',required=True);q.add_argument('--input-sha256',required=True)
    q.add_argument('--reviewed-script-sha256',required=True);q.add_argument('--run-id')
    a=p.parse_args()
    if a.command is None:p.print_help();return
    if a.command=='status':
        print(json.dumps({'policy':POLICY,'production_preparation_requested':False,'live_git_written':False,'network':False}));return
    require(sha(__file__)==a.reviewed_script_sha256,'Reviewed script changed')
    require(physical(WORK)==physical(ROOT/'.git/history-prune-image2-20261012'),'Wrong private script location')
    r=Builder().run(a.input,a.input_sha256,a.run_id)
    print(json.dumps({k:r[k] for k in ('passed','candidate_commit','candidate_tree','parent_count','source_path_count','lfs_unique_bytes','report_file')},indent=2))

if __name__=='__main__':main()

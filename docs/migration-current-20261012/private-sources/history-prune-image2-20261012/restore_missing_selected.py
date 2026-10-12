"""Restore only reviewed missing paths, without touching Git refs/index.

No arguments/--help are read-only. All bytes are first verified in a private
spool. Existing targets are always refused; failed partial files are preserved
and journaled, never silently deleted or overwritten. No fetch/LFS smudge runs.
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

ROOT = Path(r'D:\work\image')
WORK = Path(__file__).absolute().parent
GIT = Path(r'C:\Program Files\Git\ucrt64\bin\git.exe')
POINTER = re.compile(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n\Z')

def require(ok, message):
    if not ok: raise RuntimeError(message)

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()

def physical(path):
    path = Path(path).absolute()
    for p in [path, *path.parents]:
        try: s = p.lstat()
        except FileNotFoundError: continue
        require(not stat.S_ISLNK(s.st_mode) and not (getattr(s, 'st_file_attributes', 0) & 0x400),
                'Symlink/junction/reparse path refused: '+str(p))
    return path.resolve()

def digest(path):
    with physical(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def load(path): return json.loads(physical(path).read_text('utf-8-sig'))

def new_json(path, data):
    with physical(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())

def env():
    e = {k:v for k,v in os.environ.items() if not k.upper().startswith(('GIT_', 'LFS_'))}
    e.update(GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1', GIT_CONFIG_NOSYSTEM='1',
             GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0', GIT_LFS_SKIP_SMUDGE='1')
    return e

def command(root, *args):
    return [str(GIT), '--no-optional-locks', '--git-dir='+str(root/'.git'),
            '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath='+os.devnull,
            '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', '-c', 'protocol.allow=never', *args]

def git(root, *args, data=None):
    p = subprocess.run(command(root, *args), input=data, capture_output=True, cwd=root, env=env())
    require(p.returncode == 0, 'Read-only Git command failed: '+p.stderr.decode('utf-8', 'replace')[-1200:])
    return p.stdout

def fingerprint(root):
    return {'files':{name:digest(root/'.git'/name) if (root/'.git'/name).is_file() else None
                     for name in ('HEAD','index','config','packed-refs','shallow','info/grafts')},
            'refs_sha256':hashlib.sha256(git(root, 'for-each-ref', '--format=%(refname) %(objectname)')).hexdigest()}

def safe_target(root, name):
    require(isinstance(name, str) and name and '\\' not in name and ':' not in name and '\0' not in name
            and all(x not in ('','.','..') and not x.endswith((' ','.')) for x in name.split('/')),
            'Unsafe target path')
    require(name.split('/')[0].casefold() != '.git', 'Git internal target forbidden')
    p = physical(root/name)
    require(root in p.parents, 'Target escaped repository')
    return p

def signature(s):
    # On Windows path.stat and fstat may expose different legacy ctime values.
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, getattr(s, 'st_birthtime_ns', s.st_ctime_ns))

class BlobReader:
    def __init__(self, root):
        self.p = subprocess.Popen(command(root, 'cat-file', '--batch'), stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=root, env=env())
    def spool(self, row, path):
        oid = row['oid']; self.p.stdin.write((oid+'\n').encode()); self.p.stdin.flush()
        header = self.p.stdout.readline().split()
        require(len(header)==3 and header[0].decode()==oid and header[1]==b'blob', 'Missing/wrong Git object')
        size = int(header[2]); require(size == row['git_blob_bytes'], 'Git blob size differs from approved source')
        gh = hashlib.sha1(b'blob '+str(size).encode()+b'\0'); sh=hashlib.sha256(); left=size
        with path.open('xb') as f:
            while left:
                b=self.p.stdout.read(min(left, 1024*1024)); require(b, 'Short Git blob read')
                left-=len(b); gh.update(b); sh.update(b); f.write(b)
            f.flush(); os.fsync(f.fileno())
        require(self.p.stdout.read(1)==b'\n' and gh.hexdigest()==oid, 'Git blob SHA1/framing mismatch')
        return {'sha256':sh.hexdigest(), 'size':size}
    def close(self):
        self.p.stdin.close(); self.p.stdout.close(); self.p.stderr.close()
        if self.p.poll() is None:
            try:self.p.wait(timeout=5)
            except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=5)

def hydrate(cache, target, expected_sha, expected_size):
    cache=physical(cache); require(cache.is_file(), 'Missing hydrated LFS cache')
    with cache.open('rb') as src, target.open('xb') as dst:
        first=os.fstat(src.fileno()); require(first.st_size==expected_size, 'LFS source size mismatch')
        sh=hashlib.sha256(); count=0
        for b in iter(lambda:src.read(1024*1024), b''):dst.write(b); sh.update(b); count+=len(b)
        dst.flush(); os.fsync(dst.fileno()); last=os.fstat(src.fileno())
    require(signature(first)==signature(last)==signature(cache.stat()), 'LFS source changed while reading')
    require(count==expected_size and sh.hexdigest()==expected_sha, 'Hydrated LFS SHA256 mismatch')
    return {'sha256':expected_sha, 'size':expected_size}

class Restorer:
    def __init__(self, root=ROOT, work=WORK):
        self.root=physical(root); self.work=physical(work)
        require(self.root/'.git' in self.work.parents, 'Restore work directory must be inside private .git')
        physical(self.root/'.git')

    def validate(self, input_path, input_sha):
        input_path=physical(input_path); require(digest(input_path)==input_sha, 'Reviewed input hash mismatch')
        spec=load(input_path)
        require(spec.get('schema_version')==1 and spec.get('approved') is True, 'Restoration list is not approved')
        require(physical(spec['repository'])==self.root, 'Wrong repository')
        require(re.fullmatch('[0-9a-f]{40}',spec['source_commit']), 'Invalid source commit')
        require(git(self.root, 'rev-parse', spec['source_commit']+'^{commit}').decode().strip()==spec['source_commit'], 'Source commit missing')
        ap=physical(spec['source_audit_file']); require(digest(ap)==spec['source_audit_sha256'], 'Source audit changed')
        audit=load(ap); require(audit.get('object_errors')==[], 'Source audit has missing/corrupt objects')
        ar={}
        for row in audit['entries']:
            require(row['path'] not in ar, 'Duplicate source audit path'); ar[row['path']]=row
        entries=spec['entries'];require(isinstance(entries,list) and entries, 'Empty restore list')
        seen=set(); by_case=set()
        for row in entries:
            name=row['path']; target=safe_target(self.root,name)
            require(name not in seen and name.casefold() not in by_case, 'Duplicate/case-colliding restore target')
            seen.add(name);by_case.add(name.casefold())
            require(not target.exists(), 'Existing target refused: '+name)
            require(name in ar and all(row.get(k)==ar[name].get(k) for k in ('mode','oid','git_blob_bytes'))
                    and ar[name]['source_commit']==spec['source_commit'], 'Unreviewed path/object/size/mode: '+name)
            require(row['mode'] in ('100644','100755') and re.fullmatch('[0-9a-f]{40}',row['oid'])
                    and isinstance(row['git_blob_bytes'],int) and row['git_blob_bytes']>=0 and row.get('reason'), 'Invalid restore row')
            require(('expected_payload_sha256' in row)==('expected_payload_bytes' in row), 'Incomplete payload proof')
            if 'expected_payload_sha256' in row:
                require(re.fullmatch('[0-9a-f]{64}',row['expected_payload_sha256']) and isinstance(row['expected_payload_bytes'],int)
                        and row['expected_payload_bytes']>=0, 'Invalid payload proof')
        # Bind the audit to the immutable commit itself, rather than trusting a
        # path/OID audit as proof of membership in that committed tree.
        tree={}
        for part in git(self.root, 'ls-tree', '-r', '-l', '-z', spec['source_commit']).split(b'\0'):
            if not part:continue
            info,path=part.split(b'\t',1);name=path.decode('utf-8')
            if name in seen:
                mode,kind,oid,size=info.decode().split();require(kind=='blob','Restore target is not a blob')
                tree[name]=(mode,oid,int(size))
        require(all(tree.get(r['path'])==(r['mode'],r['oid'],r['git_blob_bytes']) for r in entries), 'Source commit tree membership differs')
        caches={}
        for row in spec.get('lfs_sources',[]):
            sha=row['sha256'];require(re.fullmatch('[0-9a-f]{64}',sha) and sha not in caches, 'Invalid/duplicate LFS cache')
            p=physical(row['storage_path']);require(self.root/'.git' in p.parents and p.is_file(), 'LFS cache must be a real private Git file')
            require(isinstance(row['size'],int) and row['size']>=0 and p.stat().st_size==row['size'], 'LFS cache size mismatch')
            caches[sha]={**row,'storage_path':str(p)}
        return spec,caches

    def run(self, input_path, input_sha):
        spec,caches=self.validate(input_path,input_sha);before=fingerprint(self.root)
        lock=physical(self.work/'restore-selected.lock');token=uuid.uuid4().hex
        with lock.open('x',encoding='ascii') as f:
            identity=os.fstat(f.fileno());f.write(token);f.flush();os.fsync(f.fileno())
        run=self.work/('restore-selected-'+uuid.uuid4().hex);reader=None;done=[];attempted=[];spools=[]
        try:
            # Validate again after winning the exclusive lock and before output.
            self.validate(input_path,input_sha);run.mkdir();journal=run/'journal.jsonl'
            def log(row):
                with journal.open('a',encoding='utf-8',newline='\n') as f:
                    f.write(json.dumps({'utc':now(),**row},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
            reader=BlobReader(self.root)
            for i,row in enumerate(spec['entries']):
                target=safe_target(self.root,row['path']);require(not target.exists(), 'Existing target appeared: '+row['path'])
                raw=physical(run/(str(i)+'.git-blob'));spools.append(str(raw));payload=reader.spool(row,raw);spool=raw;lfs=False
                small=raw.read_bytes() if payload['size']<=1024 else b''
                pointer=POINTER.fullmatch(small)
                require(not small.startswith(b'version https://git-lfs.github.com/spec/') or pointer is not None,
                        'Noncanonical LFS pointer refused')
                if pointer:
                    sha=pointer[1].decode();size=int(pointer[2]);require(sha in caches and caches[sha]['size']==size, 'LFS pointer lacks reviewed hydrated cache')
                    require(row.get('expected_payload_sha256')==sha and row.get('expected_payload_bytes')==size, 'LFS pointer lacks exact original payload proof')
                    spool=physical(run/(str(i)+'.hydrated'));spools.append(str(spool))
                    payload=hydrate(caches[sha]['storage_path'],spool,sha,size);lfs=True
                if 'expected_payload_sha256' in row:
                    require(payload=={'sha256':row['expected_payload_sha256'],'size':row['expected_payload_bytes']}, 'Approved original payload differs')
                require(digest(spool)==payload['sha256'], 'Verified spool changed before restoration')
                # mkdir only creates missing ordinary parents. Existing reparse
                # ancestors have been rejected and are checked once again here.
                safe_target(self.root,row['path']);target.parent.mkdir(parents=True,exist_ok=True);safe_target(self.root,row['path'])
                started={'path':row['path'],'mode':row['mode'],'git_oid':row['oid'],'payload_sha256':payload['sha256'],
                         'payload_bytes':payload['size'],'hydrated_lfs':lfs}
                log({'event':'before_exclusive_create',**started});attempted.append(started)
                sh=hashlib.sha256();count=0
                # O_EXCL is the final no-overwrite check, including a late race.
                fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0),int(row['mode'][-3:],8))
                with os.fdopen(fd,'wb') as dst, spool.open('rb') as src:
                    dest_identity=os.fstat(dst.fileno())
                    for b in iter(lambda:src.read(1024*1024),b''):dst.write(b);sh.update(b);count+=len(b)
                    dst.flush();os.fsync(dst.fileno())
                require(count==payload['size'] and sh.hexdigest()==payload['sha256'], 'Restored copy differs from verified spool')
                safe_target(self.root,row['path']);st=target.stat()
                require((st.st_dev,st.st_ino)==(dest_identity.st_dev,dest_identity.st_ino) and st.st_size==count, 'Restored target was concurrently replaced')
                require(digest(target)==payload['sha256'], 'Restored disk bytes differ')
                done.append(started);log({'event':'restored_verified',**started})
                raw.unlink()
                if spool!=raw:spool.unlink()
            require(digest(input_path)==input_sha and digest(spec['source_audit_file'])==spec['source_audit_sha256'], 'Reviewed evidence changed during restore')
            after=fingerprint(self.root);require(after==before,'Live Git metadata changed concurrently during restoration')
            report={'passed':True,'created_utc':now(),'input_file':str(input_path),'input_sha256':input_sha,
                    'source_commit':spec['source_commit'],'restored_count':len(done),'restored_bytes':sum(r['payload_bytes'] for r in done),
                    'entries':done,'git_before':before,'git_after':after,'live_refs_index_written':False,
                    'existing_files_overwritten':False,'network_or_push':False,
                    'mode_note':'Original Git index mode stays unchanged. On Windows executable mode is recorded by that index; filesystem creates use the recorded permissions.'}
            new_json(run/'report.json',report);return {**report,'report_file':str(run/'report.json')}
        except Exception as e:
            if run.exists():
                new_json(run/'failure.json',{'passed':False,'error':str(e),'verified_restored':done,'attempted_targets':attempted,
                                            'remaining_spool_files':[p for p in spools if Path(p).exists()],
                                            'partial_files_preserved':True,'live_refs_index_written':False,'network_or_push':False})
            raise
        finally:
            if reader:reader.close()
            if lock.exists():
                s=lock.lstat()
                if (s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino) and lock.read_text('ascii')==token:lock.unlink()

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command');q=s.add_parser('restore')
    q.add_argument('--input',required=True);q.add_argument('--input-sha256',required=True);q.add_argument('--reviewed-script-sha256',required=True)
    a=p.parse_args()
    if a.command is None:p.print_help();return
    require(digest(__file__)==a.reviewed_script_sha256,'Reviewed script changed')
    require(physical(WORK)==physical(ROOT/'.git/history-prune-image2-20261012'),'Wrong private script location')
    r=Restorer().run(a.input,a.input_sha256)
    print(json.dumps({k:r[k] for k in ('passed','restored_count','restored_bytes','report_file','live_refs_index_written')},indent=2))

if __name__=='__main__':main()

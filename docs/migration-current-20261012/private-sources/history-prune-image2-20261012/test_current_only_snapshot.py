"""Tiny offline fixtures only; never invoke production entrypoints or network."""
import hashlib,importlib.util,json,os,pathlib,subprocess,sys,uuid
W=pathlib.Path(__file__).resolve().parent
SCRIPT=W/'prepare_current_only_snapshot.py'
spec=importlib.util.spec_from_file_location('current_builder',SCRIPT);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE=W/('current-root-fixture-'+uuid.uuid4().hex[:10]);BASE.mkdir()
INITIAL=m.sha(SCRIPT);results=[]

def fixture(label):
    root=BASE/label;root.mkdir()
    subprocess.run([str(m.GIT),'init','--template=',str(root)],env=m.clean_env(),capture_output=True,check=True)
    work=root/'.git/private';work.mkdir()
    content={'code.txt':b'alpha\r\nbeta\r\n','.gitattributes':b'*.txt text eol=lf\n',
             'pictures/角色 space.PNG':b'\x89PNG\r\nfixture-content\x00','other/duplicate.png':b'\x89PNG\r\nfixture-content\x00',
             'empty.png':b'','代码/原始.svg':'<svg>原始</svg>\r\n'.encode(),
             'script.sh':b'#!/bin/sh\necho okay\n',
             'docs/pointer-example.txt':b'version https://git-lfs.github.com/spec/v1\noid sha256:'+b'1'*64+b'\nsize 9\n'}
    for n,b in content.items():p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    # Existing ordinary blobs are reused from a local historical source, but
    # the produced standalone root must not acquire that commit or ancestry.
    oid=m.git(root/'.git','hash-object','-w','--stdin',data=content['code.txt']).decode().strip()
    tree=m.git(root/'.git','mktree',data=('100644 blob '+oid+'\told.txt\n').encode()).decode().strip()
    old=m.git(root/'.git','-c','user.name=Fixture','-c','user.email=fixture@invalid','commit-tree',tree,data=b'old history\n').decode().strip()
    m.git(root/'.git','update-ref','refs/heads/old-fixture',old)
    inventory=[{'path':n,'size':len(b),'mtime_ns':(root/n).stat().st_mtime_ns,'mode':'100755' if n=='script.sh' else '100644'} for n,b in content.items()]
    protected=[{'path':n,'size':len(content[n]),'sha256':hashlib.sha256(content[n]).hexdigest()} for n in ('pictures/角色 space.PNG','other/duplicate.png')]
    ip=work/'inventory.jsonl';ip.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in inventory),encoding='utf-8')
    pp=work/'protected.json';pp.write_bytes(m.jsbytes(protected))
    ap=work/'absent.json';ap.write_bytes(m.jsbytes([{'path':'screenshots/removed.png','size':42}]))
    evidence={}
    for role in ('freeze','restoration','authorized_cleanup'):
        p=work/(role+'.json');p.write_bytes(m.jsbytes({'fixture':True,'role':role,'approved':True}));evidence[role]={'path':str(p),'sha256':m.sha(p)}
    approval={'schema_version':1,'approved':True,'policy':m.POLICY,'repository':str(root),'source_frozen':True,'expected_parent_count':0,
              'source_inventory_file':str(ip),'source_inventory_sha256':m.sha(ip),'protected_roster_file':str(pp),'protected_roster_sha256':m.sha(pp),
              'expected_protected_path_count':2,'authorized_absent_roster_file':str(ap),'authorized_absent_roster_sha256':m.sha(ap),
              'expected_authorized_absent_count':1,'evidence_pins':evidence,'required_preservation_checks':{k:True for k in m.GATES},
              'approved_omissions':[],'attributes_overlay_approved':True}
    approve=work/'approve.json';approve.write_bytes(m.jsbytes(approval))
    return root,work,approve,approval,content,old

def save(path,value):path.write_bytes(m.jsbytes(value));return m.sha(path)
def case(name,fn):
    try:detail=fn();results.append({'name':name,'passed':True,'detail':detail})
    except Exception as e:results.append({'name':name,'passed':False,'error':str(e)})
def rejected(label,change,needle):
    root,work,p,a,c,old=fixture(label);change(root,work,p,a,c);p.write_bytes(m.jsbytes(a))
    before=m.fingerprint(root)
    try:m.Builder(root,work).run(p,m.sha(p),'test')
    except Exception as e:
        assert needle in str(e),(needle,str(e));assert m.fingerprint(root)==before
        return str(e)
    raise AssertionError('Expected refusal')

def success():
    root,work,p,a,c,old=fixture('success');before=m.fingerprint(root)
    r=m.Builder(root,work).run(p,m.sha(p),'success');bare=pathlib.Path(r['isolated_git_dir'])
    assert r['passed'] and r['parent_count']==0 and r['reachable_commit_count']==1 and r['source_passes']==2
    assert r['lfs_object_count']==1 and r['lfs_unique_bytes']==len(c['pictures/角色 space.PNG'])
    assert not (bare/'objects/info/alternates').exists() and m.fingerprint(root)==before
    assert all((root/n).read_bytes()==b for n,b in c.items())
    assert m.git(bare,'show',r['candidate_commit']+':code.txt')==c['code.txt']
    assert m.git(bare,'show',r['candidate_commit']+':代码/原始.svg')==c['代码/原始.svg']
    assert m.git(bare,'show',r['candidate_commit']+':empty.png')==b''
    assert m.git(bare,'rev-list','--all').decode().splitlines()==[r['candidate_commit']]
    absent=subprocess.run(m.command(bare,'cat-file','-t',old),capture_output=True,env=m.clean_env());assert absent.returncode!=0
    assert m.git(bare,'show',r['candidate_commit']+':'+m.DOCS+'/evidence/protected_roster.json')==(work/'protected.json').read_bytes()
    for obj in r['lfs_objects']:assert m.sha(obj['storage_path'])==obj['sha256']
    # New-computer fixture: ordinary clone without smudge; manually hydrate from
    # the private verified payload, then run the committed portable verifier.
    clone=BASE/'portable-checkout'
    subprocess.run([str(m.GIT),'-c','protocol.file.allow=always','clone',str(bare),str(clone)],env=m.clean_env(),capture_output=True,check=True)
    for n in ('pictures/角色 space.PNG','other/duplicate.png'):(clone/n).write_bytes(c[n])
    result=subprocess.run([sys.executable,str(clone/m.DOCS/'verify_current_snapshot.py')],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    (clone/'code.txt').write_bytes(b'wrong')
    result=subprocess.run([sys.executable,str(clone/m.DOCS/'verify_current_snapshot.py')],capture_output=True,text=True)
    assert result.returncode!=0,'Portable verifier ignored changed ordinary bytes'
    return {'commit':r['candidate_commit'],'standalone':True,'unique_lfs_objects':1,'portable_working_byte_verifier':True}

case('single_root_raw_CRLF_unicode_modes_dedup_portable_working_bytes',success)
case('unapproved_input_refused',lambda:rejected('unapproved',lambda r,w,p,a,c:a.update(approved=False),'approval'))
case('old_history_policy_refused',lambda:rejected('policy',lambda r,w,p,a,c:a.update(policy='projected-history'),'approval'))
case('nonzero_parent_intent_refused',lambda:rejected('parents',lambda r,w,p,a,c:a.update(expected_parent_count=1),'zero-parent'))
case('missing_preservation_gate_refused',lambda:rejected('gate',lambda r,w,p,a,c:a['required_preservation_checks'].update(current_designs_preserved=False),'checks incomplete'))
case('unfrozen_input_refused',lambda:rejected('freeze',lambda r,w,p,a,c:a.update(source_frozen=False),'Frozen'))
case('unlisted_new_source_refused',lambda:rejected('newpath',lambda r,w,p,a,c:(r/'new.png').write_bytes(b'new'),'path set'))
case('missing_current_source_refused',lambda:rejected('missing',lambda r,w,p,a,c:(r/'code.txt').unlink(),'path set'))
case('source_changed_size_refused',lambda:rejected('size',lambda r,w,p,a,c:(r/'code.txt').write_bytes(b'different'),'size/time'))
case('pinned_evidence_drift_refused',lambda:rejected('evidence',lambda r,w,p,a,c:(w/'freeze.json').write_bytes(b'{}'),'Pinned evidence'))
case('protected_roster_count_refused',lambda:rejected('pcount',lambda r,w,p,a,c:a.update(expected_protected_path_count=6516),'roster count'))
def badprotected(r,w,p,a,c):
    f=w/'protected.json';v=m.load(f);v[0]['sha256']='0'*64;a['protected_roster_sha256']=save(f,v)
case('protected_source_hash_refused',lambda:rejected('phash',badprotected,'Protected source SHA'))
case('authorized_screenshot_reappearance_refused',lambda:rejected('absent',lambda r,w,p,a,c:((r/'screenshots').mkdir(),(r/'screenshots/removed.png').write_bytes(b'x')),'path set'))
def unhydrated(r,w,p,a,c):
    f=r/'pictures/角色 space.PNG';f.write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:'+b'1'*64+b'\nsize 2\n')
    inv=m.rows(w/'inventory.jsonl')
    for v in inv:
        if v['path']=='pictures/角色 space.PNG':v.update(size=f.stat().st_size,mtime_ns=f.stat().st_mtime_ns)
    (w/'inventory.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in inv),encoding='utf-8');a['source_inventory_sha256']=m.sha(w/'inventory.jsonl')
    pr=m.rows(w/'protected.json');pr[0].update(size=f.stat().st_size,sha256=m.sha(f));a['protected_roster_sha256']=save(w/'protected.json',pr)
case('unhydrated_binary_pointer_refused',lambda:rejected('pointer',unhydrated,'Unhydrated LFS'))
def nested(r,w,p,a,c):
    f=r/'pictures/.gitattributes';f.write_bytes(b'*.PNG -filter text\n');inv=m.rows(w/'inventory.jsonl')
    inv.append({'path':'pictures/.gitattributes','size':f.stat().st_size,'mtime_ns':f.stat().st_mtime_ns,'mode':'100644'})
    (w/'inventory.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in inv),encoding='utf-8');a['source_inventory_sha256']=m.sha(w/'inventory.jsonl')
case('nested_attribute_override_refused',lambda:rejected('nested',nested,'Nested/conflicting'))
def owned_run():
    root,work,p,a,c,old=fixture('existingrun');(work/'current-only-test').mkdir();(work/'current-only-test/unknown').write_bytes(b'keep')
    try:m.Builder(root,work).run(p,m.sha(p),'test')
    except RuntimeError as e:assert 'Existing private run' in str(e)
    else:raise AssertionError('Existing run overwritten')
    assert (work/'current-only-test/unknown').read_bytes()==b'keep';return 'preserved'
case('existing_partial_run_preserved',owned_run)
def concurrent_lock():
    root,work,p,a,c,old=fixture('lock');lock=work/'current-only-snapshot.lock';lock.write_text('another owner')
    try:m.Builder(root,work).run(p,m.sha(p),'test')
    except FileExistsError:pass
    else:raise AssertionError('Lock ignored')
    assert lock.read_text()=='another owner';return 'preserved'
case('another_owner_lock_preserved',concurrent_lock)
def qpaths():
    assert m.qpath('a"\\中').decode('ascii')=='"a\\042\\134\\344\\270\\255"'
    for bad in ('../x','a/../x','.git/config','x/.git/config','x\\y','C:/x','/x','x./z'):
        try:m.name_ok(bad)
        except RuntimeError:continue
        raise AssertionError(bad)
    return 'octal UTF-8 Git quoting and unsafe paths checked'
case('git_path_quoting_and_unsafe_paths',qpaths)
def no_writes():
    root,work,p,a,c,old=fixture('readonly');before=m.fingerprint(root)
    for arg in ([],['--help'],['status']):
        rr=subprocess.run([sys.executable,str(SCRIPT),*arg],capture_output=True);assert rr.returncode==0
    assert before==m.fingerprint(root);return 'help/status only'
case('default_help_status_read_only',no_writes)
def changed_second_pass():
    root,work,p,a,c,old=fixture('pass2change');original=m.hashlib.file_digest;target=root/'code.txt'
    def interrupt(stream,*args,**kwargs):
        if pathlib.Path(stream.name)==target:target.write_bytes(b'changed while verifying')
        return original(stream,*args,**kwargs)
    m.hashlib.file_digest=interrupt
    try:
        try:m.Builder(root,work).run(p,m.sha(p),'test')
        except RuntimeError as e:assert 'second read' in str(e) or 'between passes' in str(e),str(e)
        else:raise AssertionError('Source changed during second pass was accepted')
    finally:m.hashlib.file_digest=original
    assert (work/'current-only-test/failure.json').exists();return 'failure receipt retained'
case('source_change_during_second_pass_refused',changed_second_pass)
def reparse_guard():
    root,work,p,a,c,old=fixture('reparse');target=BASE/'junction-target';target.mkdir();link=root/'linked'
    rr=subprocess.run(['cmd','/c','mklink','/J',str(link),str(target)],capture_output=True)
    assert rr.returncode==0,rr.stderr
    try:m.scan(root)
    except RuntimeError as e:assert 'Reparse' in str(e)
    else:raise AssertionError('Junction scanned')
    return 'real Windows junction rejected; preserved fixture'
case('source_junction_refused',reparse_guard)
assert m.sha(SCRIPT)==INITIAL,'Script changed during fixture'
report={'script':str(SCRIPT),'script_sha256':INITIAL,'script_unchanged_during_test':True,'passed':all(r['passed'] for r in results),
        'test_count':len(results),'results':results,'fixture_root':str(BASE),'production_executed':False,'network_executed':False}
(W/'current-only-snapshot-offline-verification.json').write_bytes(m.jsbytes(report))
print(json.dumps(report,ensure_ascii=True,indent=2));sys.exit(0 if report['passed'] else 1)

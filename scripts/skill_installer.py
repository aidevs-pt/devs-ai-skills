"""Local, copy-based installer with ownership records, preflight checks, and safe removal."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from repo import ROOT, SLUG, catalog, identity, read_json, safe_package, tree_hash

AGENTS={
 'claude':('.claude/skills','.claude/skills'),
 'codex':('.agents/skills','.agents/skills'),
 'cursor':('.cursor/skills','.cursor/skills'),
 'copilot':('.github/skills','.copilot/skills'),
 'gemini':('.gemini/skills','.gemini/skills'),
 'universal':('.agents/skills','.agents/skills')}
LOCK='.devs-ai-installed.json'


def destination(agent,scope,project,user_home=None):
    if agent not in AGENTS:raise ValueError('Unknown agent')
    base=Path(project).resolve() if scope=='project' else Path(user_home or Path.home()).resolve()
    path=base/AGENTS[agent][scope=='user']
    # Do not follow existing symlink components into another project or user tree.
    cursor=path
    while cursor!=base:
        if cursor.is_symlink():raise ValueError(f'Symlinked install location: {cursor}')
        cursor=cursor.parent
    return path


def load_lock(target):
    path=target/LOCK
    if path.is_symlink():raise ValueError('Symlinked installation record')
    value=read_json(path) if path.exists() else {'schema_version':1,'installed':{}}
    if value.get('schema_version')!=1 or not isinstance(value.get('installed'),dict):
        raise ValueError('Invalid installation record')
    for name,record in value['installed'].items():
        if not SLUG.fullmatch(name) or len(name)>64 or not isinstance(record,dict):
            raise ValueError('Invalid skill identity in installation record')
    return value


def save_lock(target,lock):
    fd,name=tempfile.mkstemp(prefix='.devs-lock-',dir=target)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(lock,f,indent=2,sort_keys=True);f.write('\n')
        os.replace(name,target/LOCK)
    finally:
        if os.path.exists(name):os.unlink(name)


def selection(names,bundle,all_skills=False):
    known={s['name'] for s in catalog()}
    if bundle:
        collections=read_json(ROOT/'bundles.json')
        if bundle not in collections:raise ValueError(f'Unknown bundle: {bundle}')
        names=collections[bundle]
    if all_skills:names=sorted(known)
    names=list(dict.fromkeys(names))
    if not names:raise ValueError('Choose skill names, --bundle, or --all')
    if set(names)-known:raise ValueError('Unknown skills: '+', '.join(sorted(set(names)-known)))
    return names


def install(names,target,dry_run=False):
    lock=load_lock(target)
    plan=[]
    for name in names:
        source=safe_package(ROOT,name)
        dest=target/name
        if dest.is_symlink():raise ValueError(f'Refusing symlink destination: {dest}')
        source_hash=tree_hash(source)
        if dest.resolve()==source.resolve():
            plan.append({'name':name,'action':'already_canonical'});continue
        record=lock['installed'].get(name)
        if dest.exists():
            if not dest.is_dir() or not record:
                raise ValueError(f'Unmanaged destination exists: {dest}. Choose another project or resolve the conflict manually.')
            if tree_hash(dest)!=record.get('sha256'):
                raise ValueError(f'Locally modified skill: {name}. Preserve your changes before updating.')
        plan.append({'name':name,'action':'update' if dest.exists() else 'install','sha256':source_hash})
    if dry_run:return plan
    target.mkdir(parents=True,exist_ok=True)
    for item in plan:
        if item['action']=='already_canonical':continue
        name=item['name'];source=safe_package(ROOT,name);dest=target/name
        staging=Path(tempfile.mkdtemp(prefix='.devs-stage-',dir=target))
        payload=staging/'payload';backup=staging/'backup'
        try:
            shutil.copytree(source,payload,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            if tree_hash(payload)!=item['sha256']:raise ValueError('Copy verification failed')
            had_old=dest.exists()
            if had_old:os.replace(dest,backup)
            try:
                os.replace(payload,dest)
                lock['installed'][name]={'sha256':item['sha256'],'version':read_json(source/'skill.json')['version'],
                                          'publisher':identity()['publisher'],'source':str(ROOT)}
                save_lock(target,lock)
            except Exception:
                if dest.exists():shutil.rmtree(dest)
                if backup.exists():os.replace(backup,dest)
                raise
        finally:shutil.rmtree(staging,ignore_errors=True)
    return plan


def remove(names,target,dry_run=False):
    lock=load_lock(target)
    plan=[]
    for name in names:
        source=safe_package(ROOT,name)
        dest=target/name;record=lock['installed'].get(name)
        if dest.resolve()==source.resolve():raise ValueError('Cannot remove the canonical repository source')
        if not record:raise ValueError(f'No DEVS AI ownership record for {name}')
        if dest.is_symlink() or not dest.is_dir() or tree_hash(dest)!=record.get('sha256'):
            raise ValueError(f'Changed, missing, or symlinked skill: {name}; refusing deletion')
        plan.append({'name':name,'action':'remove'})
    if dry_run:return plan
    for item in plan:
        dest=target/item['name']
        staging=Path(tempfile.mkdtemp(prefix='.devs-remove-',dir=target))
        backup=staging/'backup';old=lock['installed'].pop(item['name'])
        try:
            os.replace(dest,backup)
            try:save_lock(target,lock)
            except Exception:
                os.replace(backup,dest);lock['installed'][item['name']]=old;raise
        finally:shutil.rmtree(staging,ignore_errors=True)
    return plan


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['install','update','remove','status'])
    parser.add_argument('skills',nargs='*')
    parser.add_argument('--bundle')
    parser.add_argument('--all',action='store_true')
    parser.add_argument('--agent',choices=list(AGENTS),default='universal')
    parser.add_argument('--scope',choices=['project','user'],default='project')
    parser.add_argument('--project',type=Path,default=Path.cwd())
    parser.add_argument('--user-home',type=Path,help=argparse.SUPPRESS)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(argv)
    try:
        target=destination(args.agent,args.scope,args.project,args.user_home)
        if args.command=='status':
            lock=load_lock(target);result=[]
            for name,record in lock['installed'].items():
                dest=target/name
                result.append({'name':name,'matches_installation':dest.is_dir() and not dest.is_symlink() and tree_hash(dest)==record['sha256']})
        else:
            if args.command=='update' and not args.skills and not args.bundle and not args.all:
                args.skills=list(load_lock(target)['installed'])
            names=selection(args.skills,args.bundle,args.all)
            result=(remove if args.command=='remove' else install)(names,target,args.dry_run)
        print(json.dumps({'destination':str(target),'dry_run':args.dry_run,'result':result},indent=2))
    except (OSError,ValueError,KeyError) as exc:parser.exit(2,f'Installer error: {exc}\n')


if __name__=='__main__':main()

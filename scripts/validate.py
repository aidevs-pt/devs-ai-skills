"""Validate package structure, local links, Python portability, catalogs, and authoring surfaces."""
from __future__ import annotations
import argparse
import ast
import json
import re
import sys
from pathlib import Path
from repo import ROOT, CATEGORIES, SLUG, catalog, frontmatter, read_json, skill_dirs

FORBIDDEN_IMPORTS={'socket','urllib','http','subprocess','requests','openai','anthropic'}
LOCAL_ONLY_IMPORTS={'urllib.parse'}
REQUIRED=['SKILL.md','skill.json','agents/openai.yaml','references/input-contract.md',
          'references/workflow.md','assets/example-input.json','assets/expected-output.json',
          'assets/output-template.md','evals/cases.json','LICENSE.txt']


def local_links(path,base,errors):
    text=path.read_text(encoding='utf-8')
    for raw in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',text):
        target=raw.split('#',1)[0].strip('<>')
        if not target or re.match(r'^[a-z][a-z0-9+.-]*:',target):continue
        dest=(path.parent/target).resolve()
        if not dest.is_relative_to(base.resolve()):errors.append(f'{path}: link escapes package: {target}')
        elif not dest.exists():errors.append(f'{path}: missing link: {target}')


def validate(root=ROOT):
    root=Path(root);errors=[];seen=set()
    paths=skill_dirs(root)
    if not paths:errors.append('No canonical skills found')
    for path in paths:
        base=path.parent
        for required in REQUIRED:
            if not (base/required).is_file():errors.append(f'{base.name}: missing {required}')
        if (base/'SCAFFOLD_NOT_READY').exists():errors.append(f'{base.name}: scaffold is not ready')
        try:
            fm,body=frontmatter(path)
            if set(fm)!={'name','description'}:errors.append(f'{base.name}: use only name/description frontmatter')
            name=fm.get('name','')
            if not isinstance(name,str) or not SLUG.fullmatch(name) or len(name)>64 or name!=base.name:
                errors.append(f'{base.name}: invalid or mismatched skill name')
            if name in seen:errors.append(f'Duplicate skill identity: {name}')
            seen.add(name)
            desc=fm.get('description','')
            if not isinstance(desc,str) or not 1<=len(desc)<=1024 or 'Use ' not in desc:
                errors.append(f'{base.name}: invalid triggering description')
            if len(path.read_text().splitlines())>500:errors.append(f'{base.name}: SKILL.md exceeds 500 lines')
            if re.search(r'TODO|SCAFFOLD_NOT_READY|REPLACE_ME',body):errors.append(f'{base.name}: unfinished instructions')
            meta=read_json(base/'skill.json')
            if meta.get('name')!=name or meta.get('category') not in CATEGORIES:errors.append(f'{name}: invalid skill metadata')
            if not re.fullmatch(r'\d+\.\d+\.\d+',meta.get('version','')):errors.append(f'{name}: invalid version')
            if not isinstance(meta.get('priority'),int):errors.append(f'{name}: missing priority')
            if meta.get('license')!='MIT':errors.append(f'{name}: unexpected license')
            for key in ['title','audience','summary','free_result','differentiator','service_bridge','paid_moment','primary_query','page_slug']:
                value=meta.get(key)
                if not isinstance(value,str) or not value.strip() or re.search(r'TODO|REPLACE_ME|SCAFFOLD_NOT_READY',value):
                    errors.append(f'{name}: incomplete metadata {key}')
            if meta.get('status') not in {'alpha','beta','stable'}:errors.append(f'{name}: unfinished release status')
            for tool in meta.get('tools',[]):
                f=(base/tool).resolve()
                if not f.is_relative_to(base.resolve()) or not f.is_file():errors.append(f'{name}: missing/outside tool {tool}')
            for f in base.rglob('*'):
                if f.is_symlink():errors.append(f'{name}: symlink {f}')
                if f.is_file() and f.suffix=='.json':read_json(f)
                if f.is_file() and f.suffix=='.md':local_links(f,base,errors)
                if f.is_file() and f.suffix=='.py':
                    tree=ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
                    for node in ast.walk(tree):
                        imported=[]
                        if isinstance(node,ast.Import):imported=[x.name for x in node.names]
                        elif isinstance(node,ast.ImportFrom):imported=[node.module or '']
                        for full_module in imported:
                            mod=full_module.split('.')[0]
                            if full_module not in LOCAL_ONLY_IMPORTS and (mod in FORBIDDEN_IMPORTS or mod not in sys.stdlib_module_names|{'skill_io','__future__'}):
                                errors.append(f'{name}: nonportable/disallowed import {full_module}')
                        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'eval','exec'}:
                            errors.append(f'{name}: dynamic code execution')
            ui=(base/'agents/openai.yaml').read_text()
            for key in ['display_name:','short_description:','default_prompt:']:
                if key not in ui:errors.append(f'{name}: missing UI metadata {key}')
            if '$'+name not in ui:errors.append(f'{name}: default prompt must name this skill')
            evals=read_json(base/'evals/cases.json')
            if len(evals.get('cases',[]))<3:errors.append(f'{name}: needs normal, edge, and input-injection cases')
        except (OSError,ValueError,TypeError,KeyError,SyntaxError) as exc:errors.append(f'{base.name}: {exc}')
    try:
        from build_manifest import outputs
        for name,expected in outputs(root).items():
            p=root/name
            if not p.exists() or p.read_text(encoding='utf-8')!=expected:errors.append('Generated drift: '+name)
        author=root/'.github/agents/devs-ai-skill-author.agent.md'
        fm,body=frontmatter(author)
        if fm.get('name')!='DEVS AI Skill Author' or fm.get('target')!='vscode':errors.append('Incorrect Copilot author identity/target')
        for command in ['create_skill.py','build_manifest.py','validate.py','unittest']:
            if command not in body:errors.append('Copilot agent missing workflow: '+command)
        for f in [author,root/'.github/copilot-instructions.md']:
            local_links(f,root,errors)
    except (OSError,ValueError,TypeError,KeyError) as exc:errors.append('Repository surfaces: '+str(exc))
    return errors


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args()
    errors=validate()
    if args.json:print(json.dumps({'ok':not errors,'errors':errors},indent=2))
    elif errors:print('\n'.join(errors),file=sys.stderr)
    else:print(f'Validated {len(skill_dirs())} skill packages, generated catalogs, and authoring surfaces.')
    return 1 if errors else 0


if __name__=='__main__':sys.exit(main())

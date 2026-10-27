"""Browse or install DEVS AI skills from this local repository."""
import argparse
import json
import sys
from repo import ROOT, catalog


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ('install','update','remove','status'):
        from skill_installer import main as installer
        return installer(argv)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['list','search','info','doctor'],nargs='?',default='list')
    parser.add_argument('query',nargs='?')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args(argv)
    if args.command=='doctor':
        from validate import validate
        errors=validate()
        print(json.dumps({'ok':not errors,'errors':errors},indent=2));return 1 if errors else 0
    skills=catalog()
    if args.command=='search':
        q=(args.query or '').casefold()
        skills=[s for s in skills if q in json.dumps(s,ensure_ascii=False).casefold()]
    elif args.command=='info':
        skills=[s for s in skills if s['name']==args.query]
        if not skills:parser.exit(2,'Unknown skill\n')
    if args.json or args.command=='info':print(json.dumps(skills,ensure_ascii=False,indent=2))
    else:
        for s in skills:print(f"{s['name']:<36} {s['category']:<12} {s['title']}")
    return 0


if __name__=='__main__':sys.exit(main())

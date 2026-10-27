"""Regenerate worked helper outputs deliberately; independent assertions live in tests/."""
import argparse
import json
import subprocess
import sys
from repo import ROOT, catalog


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Replace reviewed worked-output files')
    args=parser.parse_args();changed=[]
    for s in catalog():
        if not s.get('tools'):
            continue
        base=ROOT/s['path'];script=base/s['tools'][0]
        p=subprocess.run([sys.executable,str(script),'--input',str(base/'assets/example-input.json')],capture_output=True,text=True,check=True,timeout=20)
        result=json.loads(p.stdout)
        text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
        dest=base/'assets/expected-output.json'
        if not dest.exists() or dest.read_text(encoding='utf-8')!=text:
            changed.append(s['name'])
            if args.write:dest.write_text(text,encoding='utf-8',newline='\n')
    print(json.dumps({'changed_examples':changed,'written':args.write}))
    return int(bool(changed) and not args.write)


if __name__=='__main__':sys.exit(main())

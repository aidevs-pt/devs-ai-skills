"""Create reproducible ZIPs with real files for individual skills, bundles, and the repository."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import zipfile
from repo import ROOT,catalog,identity,read_json

SKIP_PARTS={'.git','__pycache__','.pytest_cache','node_modules','.venv','dist','work','private-data','website'}


def excluded(path):
    return (bool(set(path.parts)&SKIP_PARTS) or any(re.fullmatch(r'tmp[a-z0-9_]{8}',p) for p in path.parts)
            or path.suffix in {'.pyc','.pyo','.log'}
            or path.name=='.env' or path.name.startswith('.env.'))


def archive(destination, entries):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
        for name,path in sorted(entries):
            if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Unsafe archive name')
            if path.is_symlink():raise ValueError('Distribution cannot contain symlinks')
            info=zipfile.ZipInfo(name,date_time=(2026,10,27,0,0,0))
            info.create_system=3;info.external_attr=(0o100755 if path.suffix in {'.py','.mjs','.sh'} else 0o100644)<<16
            out.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def files(base,prefix):
    base=Path(base);result=[]
    for directory,dirs,names in os.walk(base,followlinks=False):
        directory=Path(directory)
        dirs[:]=sorted(d for d in dirs if not excluded((directory/d).relative_to(base)))
        for name in dirs:
            if (directory/name).is_symlink():raise ValueError('Distribution cannot contain symlink directories')
        for name in sorted(names):
            path=directory/name;relative=path.relative_to(base)
            if not excluded(relative):result.append((prefix+'/'+relative.as_posix(),path))
    return result


def package(output):
    output=Path(output).resolve();skills=catalog();release={}
    if output==ROOT or ROOT.is_relative_to(output):
        raise ValueError('Output directory must not be the repository or its ancestor')
    downloads=ROOT/'downloads'
    for s in skills:
        path=downloads/'skills'/(s['name']+'.zip')
        release[path.relative_to(ROOT).as_posix()]=archive(path,files(ROOT/s['path'],s['name']))
    by_name={s['name']:s for s in skills}
    for bundle,members in read_json(ROOT/'bundles.json').items():
        entries=[]
        for name in members:entries.extend(files(ROOT/by_name[name]['path'],name))
        path=downloads/'bundles'/(bundle+'.zip')
        release[path.relative_to(ROOT).as_posix()]=archive(path,entries)
    downloads.mkdir(parents=True,exist_ok=True)
    (downloads/'checksums.json').write_text(json.dumps(release,indent=2,sort_keys=True)+'\n')
    output.mkdir(parents=True,exist_ok=True)
    name=identity()['name']
    entries=files(ROOT,name)
    entries=[(n,p) for n,p in entries if p.resolve()!=output and not p.resolve().is_relative_to(output)]
    dest=output/(name+'.zip');checksum=archive(dest,entries)
    result={'repository_zip':dest.name,'sha256':checksum,'file_count':len(entries),'skills':len(skills),
            'individual_skill_zips':len(skills),'bundle_zips':len(read_json(ROOT/'bundles.json'))}
    (output/'release.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'dist');a=p.parse_args()
    from validate import validate
    errors=validate()
    if errors:p.exit(1,'Resolve validation failures before packaging:\n'+'\n'.join(errors)+'\n')
    print(json.dumps(package(a.output_dir),indent=2))


if __name__=='__main__':main()

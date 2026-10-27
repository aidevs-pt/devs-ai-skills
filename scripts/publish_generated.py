"""Publish generated text after trusted CI validation; never rebase or force-push."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

from build_manifest import outputs
from repo import ROOT, write
from validate import validate

GENERATED_FILES = {
    'registry.json', 'skills.json', 'cli/skills.json',
    '.codex/skills-index.json', '.gemini/skills-index.json',
    '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
    '.codex-plugin/plugin.json', 'docs/skills-reference.md',
}
GENERATED_DIRECTORIES = {'docs/domains'}


def is_generated(name):
    path = Path(name)
    return name in GENERATED_FILES or (
        path.parent.as_posix() in GENERATED_DIRECTORIES and path.suffix == '.md'
    )


def git(root, *args, check=True):
    return subprocess.run(['git', *args], cwd=root, check=check, capture_output=True, text=True)


def remote_tip(root):
    git(root, 'fetch', '--no-tags', 'origin', 'refs/heads/master')
    return git(root, 'rev-parse', 'FETCH_HEAD').stdout.strip()


def publish(source_sha, root=ROOT):
    root = Path(root)
    if not re.fullmatch(r'[0-9a-f]{40}', source_sha):
        raise ValueError('Expected a full validated commit SHA')
    if git(root, 'rev-parse', 'HEAD').stdout.strip() != source_sha:
        raise ValueError('Checkout does not match the validated commit')
    if git(root, 'status', '--porcelain', '--untracked-files=all').stdout:
        raise ValueError('Publishing requires a clean checkout')
    if remote_tip(root) != source_sha:
        return 'Skipped: master has advanced beyond the validated commit.'

    generated = outputs(root)
    if not generated or any(not is_generated(name) for name in generated):
        raise ValueError('Generator output is outside the approved text paths')
    tracked = git(root, 'ls-files', '-z').stdout.split('\0')
    obsolete = {name for name in tracked if is_generated(name)} - generated.keys()
    for name in obsolete:
        (root / name).unlink()
    for name, text in generated.items():
        write(root / name, text)
    errors = validate(root)
    if errors:
        raise ValueError('Generated content failed validation:\n' + '\n'.join(errors))

    git(root, 'add', '--all', '--', *sorted(generated.keys() | obsolete))
    staged = git(root, 'diff', '--cached', '--name-only', '-z').stdout.split('\0')
    if any(name and not is_generated(name) for name in staged):
        raise ValueError('Refusing to publish changes outside generated text paths')
    if not any(staged):
        return 'No generated changes to publish.'
    if remote_tip(root) != source_sha:
        return 'Skipped: master advanced while generating content.'

    git(root, '-c', 'user.name=github-actions[bot]',
        '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '-m', 'chore: refresh generated catalogs and docs',
        '-m', f'Generated from validated commit {source_sha}.')
    pushed = git(root, 'push', 'origin', 'HEAD:refs/heads/master', check=False)
    if pushed.returncode:
        if remote_tip(root) != source_sha:
            return 'Skipped: master advanced before the push; nothing was overwritten.'
        raise RuntimeError('Push rejected; check Actions permissions and branch rules:\n' + pushed.stderr)
    return 'Published generated text as a follow-up commit on master.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-sha', required=True, help='Validated master commit; CI use only')
    args = parser.parse_args()
    try:
        print(publish(args.source_sha))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, str(exc) + '\n' + getattr(exc, 'stderr', ''))


if __name__ == '__main__':
    sys.exit(main())

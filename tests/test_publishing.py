"""Exercise publication against local Git remotes, never the hosted repository."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import publish_generated as publisher
from build_manifest import outputs


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'checkout'
        self.root.mkdir()
        self.remote = self.base / 'remote.git'
        self.git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'master')
        self.configure_git(self.root)
        self.write('README.md', 'Source documentation\n')
        self.write('.gitignore', '.env\n*.zip\ndownloads/\nwebsite/\n')
        self.write('registry.json', '{"old": true}\n')
        self.write('docs/domains/obsolete.md', 'Obsolete generated page\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Source fixture')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'HEAD:refs/heads/master')
        self.source = self.git('rev-parse', 'HEAD')
        self.generated = {'registry.json': '{"new": true}\n', 'docs/skills-reference.md': '# Skills\n'}
        generator_patch = patch.object(publisher, 'outputs', return_value=self.generated)
        validator_patch = patch.object(publisher, 'validate', return_value=[])
        self.generator = generator_patch.start()
        self.addCleanup(generator_patch.stop)
        self.validator = validator_patch.start()
        self.addCleanup(validator_patch.stop)

    def git(self, *args, cwd=None):
        result = subprocess.run(['git', *args], cwd=cwd or self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def configure_git(self, root):
        self.git('config', 'user.name', 'Test fixture', cwd=root)
        self.git('config', 'user.email', 'fixture@example.invalid', cwd=root)
        self.git('config', 'commit.gpgsign', 'false', cwd=root)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def remote_head(self):
        return self.git('--git-dir', str(self.remote), 'rev-parse', 'refs/heads/master')

    def advance_remote(self):
        other = self.base / 'other'
        self.git('clone', '--branch', 'master', str(self.remote), str(other))
        self.configure_git(other)
        (other / 'new-source.txt').write_text('New source commit\n')
        self.git('add', 'new-source.txt', cwd=other)
        self.git('commit', '-m', 'New source fixture', cwd=other)
        self.git('push', 'origin', 'HEAD:refs/heads/master', cwd=other)
        return self.remote_head()

    def test_real_generator_outputs_are_all_allowlisted(self):
        self.assertTrue(all(publisher.is_generated(name) for name in outputs()))
        self.assertFalse(any(name.startswith('website/') for name in outputs()))
        for name in ['.github/workflows/job.yml', 'downloads/skill.zip', '.env',
                     'docs/architecture.md', 'docs/domains/nested/private.md',
                     'website/content/index.md', 'website/content/skills/example.md',
                     'website/content/skills/../../private.md', 'registry.json.bak']:
            with self.subTest(name=name):
                self.assertFalse(publisher.is_generated(name))

    def test_publishes_only_generated_changes_with_source_provenance(self):
        self.write('.env', 'PRIVATE_FIXTURE=true\n')
        self.write('downloads/private.zip', 'Not a release artifact\n')
        self.write('website/content/index.md', 'Local-only content\n')
        result = publisher.publish(self.source, self.root)
        self.assertIn('Published', result)
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertEqual(self.git('rev-parse', 'HEAD^'), self.source)
        changed = set(self.git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines())
        self.assertEqual(changed, set(self.generated) | {'docs/domains/obsolete.md'})
        self.assertFalse((self.root / 'docs/domains/obsolete.md').exists())
        message = self.git('log', '-1', '--format=%B')
        self.assertIn(self.source, message)
        self.assertIn('Co-authored-by: Copilot', message)
        self.assertEqual(self.git('log', '-1', '--format=%an'), 'github-actions[bot]')
        self.assertEqual((self.root / 'README.md').read_text(), 'Source documentation\n')
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_unchanged_outputs_do_not_create_another_commit(self):
        publisher.publish(self.source, self.root)
        head = self.remote_head()
        result = publisher.publish(head, self.root)
        self.assertIn('No generated changes', result)
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_stale_validation_is_skipped_before_generating(self):
        newer = self.advance_remote()
        self.assertIn('Skipped', publisher.publish(self.source, self.root))
        self.generator.assert_not_called()
        self.assertEqual(self.remote_head(), newer)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source)

    def test_branch_advance_during_generation_prevents_commit(self):
        def validate_and_advance(root):
            self.advance_remote()
            return []
        self.validator.side_effect = validate_and_advance
        self.assertIn('Skipped', publisher.publish(self.source, self.root))
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source)
        self.assertNotEqual(self.remote_head(), self.source)

    def test_push_race_never_overwrites_new_source(self):
        real_git = publisher.git
        newer = []
        def racing_git(root, *args, **kwargs):
            if args[0] == 'push':
                newer.append(self.advance_remote())
            return real_git(root, *args, **kwargs)
        with patch.object(publisher, 'git', side_effect=racing_git):
            self.assertIn('Skipped', publisher.publish(self.source, self.root))
        self.assertEqual(self.remote_head(), newer[0])
        self.assertNotEqual(self.git('rev-parse', 'HEAD'), newer[0])

    def test_permission_rejection_is_not_reported_as_success(self):
        real_git = publisher.git
        def rejected_push(root, *args, **kwargs):
            if args[0] == 'push':
                return subprocess.CompletedProcess(args, 1, '', 'Protected branch rejects bot')
            return real_git(root, *args, **kwargs)
        with patch.object(publisher, 'git', side_effect=rejected_push):
            with self.assertRaisesRegex(RuntimeError, 'Push rejected'):
                publisher.publish(self.source, self.root)
        self.assertEqual(self.remote_head(), self.source)

    def test_invalid_generated_content_is_not_committed(self):
        self.validator.return_value = ['Invalid source metadata']
        with self.assertRaisesRegex(ValueError, 'failed validation'):
            publisher.publish(self.source, self.root)
        self.assertEqual(self.remote_head(), self.source)
        self.assertEqual(self.git('diff', '--cached', '--name-only'), '')

    def test_unapproved_generated_path_is_rejected(self):
        self.generator.return_value = {'.github/workflows/unexpected.yml': 'Not generated documentation'}
        with self.assertRaisesRegex(ValueError, 'outside the approved'):
            publisher.publish(self.source, self.root)
        self.assertFalse((self.root / '.github/workflows/unexpected.yml').exists())
        self.assertEqual(self.remote_head(), self.source)

    def test_dirty_checkout_is_not_published(self):
        self.write('README.md', 'Uncommitted source changes\n')
        self.git('add', 'README.md')
        with self.assertRaisesRegex(ValueError, 'clean checkout'):
            publisher.publish(self.source, self.root)
        self.assertEqual(self.remote_head(), self.source)
        self.generator.assert_not_called()

    def test_untracked_file_is_not_silently_committed(self):
        self.write('private-notes.txt', 'Private fixture\n')
        with self.assertRaisesRegex(ValueError, 'clean checkout'):
            publisher.publish(self.source, self.root)
        self.assertEqual(self.remote_head(), self.source)

    def test_invalid_or_mismatched_source_sha_is_rejected(self):
        for sha in ['master', 'a' * 40]:
            with self.subTest(sha=sha), self.assertRaises(ValueError):
                publisher.publish(sha, self.root)
        self.assertEqual(self.remote_head(), self.source)
        self.generator.assert_not_called()


if __name__ == '__main__':
    unittest.main()

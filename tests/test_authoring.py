"""Exercise the authoring entry points in isolated repositories."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package import excluded,package


class AuthoringTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.root=Path(self.temp.name)/'repository'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','*.pyc','downloads','dist','tmp????????'))
    def tearDown(self):self.temp.cleanup()
    def run_script(self,name,*args):
        return subprocess.run([sys.executable,str(self.root/'scripts'/name),*args],cwd=self.root,capture_output=True,text=True)
    def test_scaffold_is_incomplete_and_existing_package_is_preserved(self):
        args=['new-business-job','--title','New Business Job','--category','operations']
        result=self.run_script('create_skill.py',*args)
        self.assertEqual(result.returncode,0,result.stderr)
        skill=self.root/'.agents/skills/new-business-job'
        before=(skill/'SKILL.md').read_bytes()
        self.assertTrue((skill/'SCAFFOLD_NOT_READY').exists())
        check=self.run_script('validate.py')
        self.assertNotEqual(check.returncode,0)
        self.assertIn('scaffold is not ready',check.stderr)
        self.assertNotEqual(self.run_script('create_skill.py',*args).returncode,0)
        self.assertEqual((skill/'SKILL.md').read_bytes(),before)
    def test_configuration_is_local_and_regenerates_valid_metadata(self):
        bad=self.run_script('configure.py','--github','https://github.com/example/test')
        self.assertNotEqual(bad.returncode,0)
        result=self.run_script('configure.py','--github','example/skills-fixture')
        self.assertEqual(result.returncode,0,result.stderr)
        config=json.loads((self.root/'config/repository.json').read_text())
        self.assertEqual(config['github_repository'],'example/skills-fixture')
        self.assertIn('example/skills-fixture',(self.root/'website/content/skills/supplier-catalog-to-store.md').read_text())
        self.assertEqual(self.run_script('validate.py').returncode,0)
    def test_private_work_and_output_ancestor_are_excluded(self):
        for name in ['work/customer.json','private-data/orders.csv','.env','.env.local','test.log','__pycache__/x.pyc']:
            self.assertTrue(excluded(Path(name)),name)
        self.assertFalse(excluded(Path('.github/agents/devs-ai-skill-author.agent.md')))
        with self.assertRaises(ValueError):package(ROOT)
        with self.assertRaises(ValueError):package(ROOT.parent)


if __name__=='__main__':unittest.main()

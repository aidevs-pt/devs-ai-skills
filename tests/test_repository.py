import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import repo
import skill_installer as installer
from build_manifest import outputs
from validate import validate
from package import archive,files


class RepositoryTests(unittest.TestCase):
    def test_static_contract(self):self.assertEqual(validate(),[])
    def test_generation_is_deterministic(self):self.assertEqual(outputs(),outputs())
    def test_catalog_has_all_planned_workflows(self):
        names={s['name'] for s in repo.catalog()}
        for n in ['supplier-catalog-to-store','company-knowledge-qa','sop-to-ai-workflow','rfq-to-quote']:
            self.assertIn(n,names)
        self.assertGreaterEqual(len(names),10)
    def test_generated_outputs_match_source(self):
        for name,text in outputs().items():self.assertEqual((ROOT/name).read_text(encoding='utf-8'),text,name)
    def test_canonical_skill_works_when_copied_alone(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temp:
            for s in repo.catalog():
                base=Path(temp)/s['name'];shutil.copytree(ROOT/s['path'],base,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                for tool in s['tools']:
                    help_run=subprocess.run([sys.executable,str(base/tool),'--help'],cwd=temp,capture_output=True,text=True)
                    self.assertEqual(help_run.returncode,0,help_run.stderr)
                if s['tools']:
                    run=subprocess.run([sys.executable,str(base/s['tools'][0]),'--input',str(base/'assets/example-input.json')],cwd=temp,capture_output=True,text=True)
                    self.assertEqual(run.returncode,0,run.stderr);self.assertIsInstance(json.loads(run.stdout),dict)
    def test_real_file_zip_is_reproducible_and_standalone(self):
        s=repo.catalog()[0];base=ROOT/s['path']
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temp:
            temp=Path(temp);a=temp/'one.zip';b=temp/'two.zip'
            self.assertEqual(archive(a,files(base,s['name'])),archive(b,files(base,s['name'])))
            with zipfile.ZipFile(a) as z:
                self.assertIn(s['name']+'/SKILL.md',z.namelist())
                self.assertIn(s['name']+'/LICENSE.txt',z.namelist())
                self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist()))
                z.extractall(temp/'extracted')
            extracted=temp/'extracted'/s['name']
            p=subprocess.run([sys.executable,str(extracted/s['tools'][0]),'--input',str(extracted/'assets/example-input.json')],cwd=temp,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT.parent);self.project=Path(self.temp.name);self.name='supplier-catalog-to-store'
    def tearDown(self):self.temp.cleanup()
    def target(self,agent='copilot'):return installer.destination(agent,'project',self.project)
    def test_all_agent_paths_and_user_scope(self):
        expected={'claude':'.claude/skills','codex':'.agents/skills','cursor':'.cursor/skills','copilot':'.github/skills','gemini':'.gemini/skills','universal':'.agents/skills'}
        for agent,path in expected.items():self.assertEqual(self.target(agent),self.project/path)
        self.assertEqual(installer.destination('copilot','user',self.project,self.project/'user'),self.project/'user/.copilot/skills')
    def test_dry_run_creates_no_directories(self):
        plan=installer.install([self.name],self.target(),True)
        self.assertEqual(plan[0]['action'],'install');self.assertFalse(self.target().exists())
    def test_install_update_and_remove_owned_unchanged(self):
        target=self.target();installer.install([self.name],target)
        self.assertTrue((target/self.name/'SKILL.md').exists());self.assertEqual(installer.install([self.name],target)[0]['action'],'update')
        installer.remove([self.name],target);self.assertFalse((target/self.name).exists())
    def test_unmanaged_conflict_is_preserved(self):
        dest=self.target()/self.name;dest.mkdir(parents=True);(dest/'notes.txt').write_text('keep')
        with self.assertRaises(ValueError):installer.install([self.name],self.target())
        self.assertEqual((dest/'notes.txt').read_text(),'keep')
    def test_modified_installed_package_is_not_overwritten_or_removed(self):
        target=self.target();installer.install([self.name],target);p=target/self.name/'notes.txt';p.write_text('my changes')
        with self.assertRaises(ValueError):installer.install([self.name],target)
        with self.assertRaises(ValueError):installer.remove([self.name],target)
        self.assertEqual(p.read_text(),'my changes')
    def test_multi_install_preflights_before_first_write(self):
        other='company-knowledge-qa';(self.target()/other).mkdir(parents=True)
        with self.assertRaises(ValueError):installer.install([self.name,other],self.target())
        self.assertFalse((self.target()/self.name).exists())
    def test_traversal_names_rejected(self):
        for name in ['../escape','/outside','x/../../bad']:
            with self.assertRaises(ValueError):installer.install([name],self.target())
    def test_lock_traversal_is_rejected_before_status_access(self):
        target=self.target();target.mkdir(parents=True)
        (target/installer.LOCK).write_text(json.dumps({'schema_version':1,'installed':{'../outside':{}}}))
        with self.assertRaises(ValueError):installer.load_lock(target)
    def test_canonical_source_is_never_removable(self):
        from unittest.mock import patch
        target=ROOT/'.agents/skills'
        record={'schema_version':1,'installed':{self.name:{'sha256':repo.tree_hash(target/self.name)}}}
        with patch.object(installer,'load_lock',return_value=record):
            with self.assertRaises(ValueError):installer.remove([self.name],target,True)
    @unittest.skipIf(sys.platform=='win32','Symlink creation requires machine-specific Windows privileges')
    def test_symlink_destination_rejected(self):
        target=self.target();target.mkdir(parents=True);outside=self.project/'outside';outside.mkdir()
        (target/self.name).symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):installer.install([self.name],target)


if __name__=='__main__':unittest.main()

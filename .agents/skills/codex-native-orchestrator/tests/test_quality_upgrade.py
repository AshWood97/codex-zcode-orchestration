import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import codex_native_orchestrator as c


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()


def commit(repo, text):
    (repo / 'value.txt').write_text(text)
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', text)
    return git(repo, 'rev-parse', 'HEAD')


def repo_at(root):
    repo=root/'repo';repo.mkdir()
    git(repo, 'init', '-q');git(repo,'config','user.name','Test');git(repo,'config','user.email','test@local')
    commit(repo,'baseline')
    return repo


def check(output='passed'):
    return {'command':'python3 -m unittest', 'exit_code':0, 'output_hash':c.sha256_bytes(output.encode()), 'artifact_hashes':{}}


def verdict(value):
    return {'final':{'Verdict':value,'Important findings':[] if value=='approve' else ['Wrong value'], 'Required changes':[],'Residual risks':[]}}


def planned():
    return {'final':{'outcome':'ready','summary':'Ready','plan_steps':['Implement and verify'],'residual_risks':[]}}


def task_result(kwargs, outcome='succeeded', checks=None):
    packet=json.loads(kwargs['prompt'])
    data=dict(packet['result_contract'], outcome=outcome, summary='Verified', commit_sha=None,
              modified_files=[], test_evidence=[check()] if checks is None else checks)
    spec=c.DEFAULT_ROLE_SPECS[kwargs['role']]
    data['requested']={'model':spec['model'],'effort':spec['reasoning_effort'],'sandbox':'read-only' if kwargs['read_only'] else 'workspace-write'}
    data['observed']={'model':'unknown','effort':'unknown','sandbox':'unknown'}
    return {'final':data}


class QualityUpgradeTests(unittest.TestCase):
    def _tester_context(self, root):
        repo=repo_at(root)
        o=c.Orchestrator(repo,root/'home')
        plan=c.validate_plan({'plan_id':'verify','objective':'Verify source', 'tasks':[{'task_id':'verify','role':'tester','objective':'Verify without changing source'}]},o.manifest)
        run=o.store.create(plan,c.repo_snapshot(repo),o.manifest,'verify')
        state,plan=o.store.load(run)
        context=o._prepare_task(state,plan,plan['tasks'][0])
        return repo,o,state,context

    def test_disposable_outputs_are_not_integrated(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,o,state,context=self._tester_context(Path(temp))
            def invoke(**kwargs):
                self.assertFalse(kwargs['read_only'])
                cwd=Path(kwargs['cwd']);self.assertNotEqual(cwd,repo)
                subprocess.run([sys.executable,'-c',"from pathlib import Path; assert Path('value.txt').read_text() == 'baseline'; Path('cache').write_text('generated')"],cwd=cwd,check=True)
                return task_result(kwargs)
            with mock.patch.object(o.runner,'invoke',side_effect=invoke):
                result=o._run_task_process(state,context)
            self.assertTrue(result['evidence']['verification_environment']['tracked_files_unchanged'])
            self.assertEqual(result['evidence']['verification_environment']['discarded_outputs'],['cache'])
            self.assertFalse((repo/'cache').exists())
            self.assertEqual(git(repo,'status','--porcelain'),'')
            self.assertEqual(list((o.store.run_path('verify')/'worktrees').iterdir()),[])

    def test_verifier_source_mutation_rejects_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,o,state,context=self._tester_context(Path(temp))
            def invoke(**kwargs):
                (Path(kwargs['cwd'])/'value.txt').write_text('weakened test or source')
                return task_result(kwargs)
            with mock.patch.object(o.runner,'invoke',side_effect=invoke):
                with self.assertRaisesRegex(c.ValidationError,'verification modified'):
                    o._run_task_process(state,context)
            self.assertEqual((repo/'value.txt').read_text(),'baseline')

    def test_disposable_verification_uses_store_workspace_location(self):
        with tempfile.TemporaryDirectory() as temp:
            _,o,state,context=self._tester_context(Path(temp))
            workspace=Path(temp).resolve()/'accessible-workspaces'/'verify'
            def invoke(**kwargs):
                self.assertTrue(Path(kwargs['cwd']).is_relative_to(workspace))
                packet=json.loads(kwargs['prompt'])
                self.assertEqual(packet['result_contract']['requested']['sandbox'],'workspace-write')
                return task_result(kwargs)
            with mock.patch.object(o.store,'worktrees_path',return_value=workspace), mock.patch.object(o.runner,'invoke',side_effect=invoke):
                o._run_task_process(state,context)
            self.assertEqual(list(workspace.iterdir()),[])

    def test_no_test_or_failed_check_is_not_success(self):
        for checks in ([],[dict(check(),exit_code=1)]):
            with self.subTest(checks=checks),tempfile.TemporaryDirectory() as temp:
                _,o,state,context=self._tester_context(Path(temp))
                with mock.patch.object(o.runner,'invoke',side_effect=lambda **kw:task_result(kw,checks=checks)):
                    with self.assertRaisesRegex(c.ValidationError,'successful tester requires'):
                        o._run_task_process(state,context)

    def test_global_readonly_disables_disposable_writes(self):
        m=c.load_manifest(Path.cwd())
        raw={'plan_id':'ro','objective':'Inspect', 'read_only':True,'tasks':[{'task_id':'v','role':'tester','objective':'Verify'}]}
        self.assertEqual(c.validate_plan(raw,m)['tasks'][0]['verification_workspace'],'read-only')
        raw['tasks'][0]['verification_workspace']='disposable'
        with self.assertRaisesRegex(c.ValidationError,'ceiling'):
            c.validate_plan(raw,m)

    def test_alternative_candidates_cannot_enter_additive_dag(self):
        for field in ('candidate_id','candidate_group'):
            with self.subTest(field=field),self.assertRaisesRegex(c.ValidationError,'separate native checkouts'):
                c.validate_plan({'plan_id':'alt','objective':'Choose', 'tasks':[{'task_id':'a','role':'explorer','objective':'Inspect',field:'A'}]},c.load_manifest(Path.cwd()))

    def test_test_author_paths_are_exclusive_from_worker(self):
        tasks=[{'task_id':'tests','role':'test_author','objective':'Write acceptance','owned_paths':['tests']},
               {'task_id':'impl','role':'worker','objective':'Implement','owned_paths':['tests/test_a.py']},
               {'task_id':'verify','role':'tester','objective':'Verify','depends_on':['tests','impl']}]
        with self.assertRaisesRegex(c.ValidationError,'overlap'):
            c.validate_plan({'plan_id':'ownership','objective':'Implement','tasks':tasks},c.load_manifest(Path.cwd()))

    def test_new_roles_reach_actual_runner_packets(self):
        m=c.load_manifest(Path.cwd())
        for role in ('design_critic','finding_validator','debugger'):
            with self.subTest(role=role),tempfile.TemporaryDirectory() as temp:
                repo=repo_at(Path(temp));o=c.Orchestrator(repo,Path(temp)/'home')
                plan=c.validate_plan({'plan_id':role,'objective':'Inspect','tasks':[{'task_id':'task','role':role,'objective':'Inspect evidence'}]},m)
                run=o.store.create(plan,c.repo_snapshot(repo),m)
                state,plan=o.store.load(run);context=o._prepare_task(state,plan,plan['tasks'][0])
                def invoke(**kwargs):
                    self.assertEqual(json.loads(kwargs['prompt'])['role_instructions'],c.role_instructions(role))
                    self.assertTrue(kwargs['read_only'])
                    return task_result(kwargs)
                with mock.patch.object(o.runner,'invoke',side_effect=invoke):o._run_task_process(state,context)

    def test_profile_only_edit_invalidates_package_evidence(self):
        o=c.Orchestrator(Path.cwd(),Path(tempfile.gettempdir())/'quality-unused-home')
        state={'manifest_hash':c.sha256_json({k:v for k,v in o.manifest.items() if k!='manifest_path'})}
        self.assertTrue(o._manifest_matches_run(state))
        original=c.sha256_file
        with mock.patch.object(c,'sha256_file',side_effect=lambda p:'f'*64 if Path(p).name=='worker.toml' else original(p)):
            self.assertFalse(o._manifest_matches_run(state))

    def test_native_revision_rechecks_and_archives_without_second_conductor(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');calls=[];gate_calls=0
            def invoke(**kwargs):
                nonlocal gate_calls
                calls.append(kwargs['role'])
                if kwargs['role']=='conductor':return planned()
                if kwargs['role']=='guardian':
                    gate_calls+=1
                    return verdict('revise' if gate_calls==1 else 'approve')
                return verdict('approve')
            path=root/'receipt.json'
            with mock.patch.object(o,'_require_installed_topology'),mock.patch.object(o.runner,'invoke',side_effect=invoke),mock.patch.object(c,'validate_guardian_runtime'):
                o.native_begin('native','Fix value');first=commit(repo,'candidate one')
                receipt={'objective':'Fix value','changes':True,'delivery_commit':first,'test_evidence':[check()]}
                path.write_text(json.dumps(receipt));result=o.native_gate(path,'native')
                self.assertFalse(result['ok']);self.assertEqual(result['gate']['status'],'revise')
                o.native_gate(path,'native');self.assertEqual(gate_calls,1)
                receipt['result']='wording only';path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(c.ControllerError,'changed, previously unreviewed'):
                    o.native_gate(path,'native')
                second=commit(repo,'candidate two')
                receipt.update(delivery_commit=second,repair={'reason':'Correct value','issue_id':'value','addressed_findings':['Wrong value'],'verification_head':second})
                path.write_text(json.dumps(receipt));result=o.native_gate(path,'native')
                self.assertTrue(result['ok']);self.assertEqual(calls,['conductor','reviewer','guardian','reviewer','guardian'])
                state,_=o.store.load('native')
                self.assertEqual(state['evidence_revision'],2)
                self.assertEqual(state['revision_history'][0]['gate']['status'],'revise')
                self.assertTrue((o.store.run_path('native')/'evidence/revision-1/results-guardian.json').is_file())

    def test_revision_cannot_reuse_old_head_test_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home')
            previous=c.repo_snapshot(repo);new=commit(repo,'repair')
            state={'run_id':'x','gate':{'status':'revise'},'review':{'verdict':'approve'},'native_final_snapshot':previous}
            receipt={'test_evidence':[check()],'repair':{'reason':'fix','issue_id':'x','addressed_findings':['x'],'verification_head':previous['head']}}
            with self.assertRaisesRegex(c.ValidationError,'verification_head'):
                o._begin_native_revision(state,receipt,c.repo_snapshot(repo))

    def test_five_repair_waves_is_hard_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            o=c.Orchestrator(Path(temp),Path(temp)/'home')
            with self.assertRaisesRegex(c.ControllerError,'five repair waves'):
                o._begin_native_revision({'gate':{'status':'revise'},'repair_waves':5},{},{})

    def test_two_failed_fixes_require_debugger_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');previous=c.repo_snapshot(repo);new=commit(repo,'repair')
            state={'run_id':'x','gate':{'status':'revise'},'native_final_snapshot':previous,'revision_history':[{'repair':{'issue_id':'x'}},{'repair':{'issue_id':'x'}}]}
            receipt={'test_evidence':[check()],'repair':{'reason':'fix','issue_id':'x','addressed_findings':['x'],'verification_head':new}}
            with self.assertRaisesRegex(c.ValidationError,'debugger_evidence'):
                o._begin_native_revision(state,receipt,c.repo_snapshot(repo))

    def test_runner_repair_reverifies_integrated_tree_and_can_apply(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');calls=[];gates=0
            raw={'plan_id':'runner','objective':'Fix value','tasks':[{'task_id':'impl','role':'worker','objective':'Change value','owned_paths':['value.txt']},{'task_id':'verify','role':'tester','objective':'Verify','depends_on':['impl']}]}
            plan_path=root/'plan.json';plan_path.write_text(json.dumps(raw))
            def invoke(**kwargs):
                nonlocal gates
                role=kwargs['role'];calls.append(role)
                if role=='conductor':return planned()
                if role=='guardian':
                    gates+=1;return verdict('revise' if gates==1 else 'approve')
                if role=='reviewer':return verdict('approve')
                if role=='worker':
                    (Path(kwargs['cwd'])/'value.txt').write_text('first implementation')
                    result=task_result(kwargs);result['final']['modified_files']=['value.txt'];return result
                self.assertEqual((Path(kwargs['cwd'])/'value.txt').read_text(),'first implementation' if gates==0 else 'repaired implementation')
                return task_result(kwargs)
            with mock.patch.object(o,'_require_installed_topology'),mock.patch.object(o.runner,'invoke',side_effect=invoke),mock.patch.object(c,'validate_guardian_runtime'):
                result=o.run(plan_path,run_id='runner');self.assertEqual(result['state'],'needs_input')
                state,_=o.store.load('runner');integration=Path(state['integration']['path']);head=commit(integration,'repaired implementation')
                receipt={'objective':'Fix value','test_evidence':[check()],'repair':{'reason':'real repair','issue_id':'value','addressed_findings':['Wrong value'],'verification_head':head}}
                receipt_path=root/'repair.json';receipt_path.write_text(json.dumps(receipt))
                result=o.revise_run(receipt_path,'runner')
                self.assertEqual(result['state'],'completed')
                self.assertEqual(calls,['conductor','worker','tester','reviewer','guardian','tester','reviewer','guardian'])
                self.assertEqual((repo/'value.txt').read_text(),'baseline')
                o.apply('runner')
                self.assertEqual((repo/'value.txt').read_text(),'repaired implementation')

if __name__=='__main__':unittest.main()

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import codex_native_orchestrator as c
from test_quality_upgrade import repo_at,task_result,check,planned,verdict


class LunaRoutingTests(unittest.TestCase):
    def _plan(self,tasks,read_only=False):
        return c.validate_plan({'plan_id':'luna','objective':'Bounded work','read_only':read_only,'tasks':tasks},c.load_manifest(Path.cwd()))

    def _checker(self):
        return {'task_id':'checks','role':'check_runner','objective':'Run specified checks','check_commands':['python3 -m unittest']}

    def _mechanic(self):
        return {'task_id':'edit','role':'mechanic','objective':'Replace exact value','owned_paths':['value.txt'],'change_recipe':['Replace literal baseline with changed in value.txt'],'acceptance_criteria':['value.txt contains changed']}

    def test_execution_roles_require_concrete_contracts(self):
        for field in ('change_recipe','acceptance_criteria'):
            role=self._mechanic();role.pop(field)
            with self.subTest(field=field),self.assertRaisesRegex(c.ValidationError,'mechanic requires'):
                self._plan([role])
        checker=self._checker();checker.pop('check_commands')
        with self.assertRaisesRegex(c.ValidationError,'predetermined check_commands'):
            self._plan([checker])

    def test_luna_check_does_not_replace_sol_final_verification(self):
        mechanic=self._mechanic();checker=dict(self._checker(),depends_on=['edit'])
        with self.assertRaisesRegex(c.ValidationError,'read-only tester downstream'):
            self._plan([mechanic,checker])
        p=self._plan([mechanic,checker,{'task_id':'final-check','role':'tester','objective':'Verify acceptance','depends_on':['checks']}])
        self.assertTrue(p['tasks'][0]['writes'])
        self.assertFalse(p['tasks'][1]['writes'])
        self.assertEqual(p['tasks'][1]['verification_workspace'],'disposable')

    def test_luna_checker_respects_readonly_and_cannot_deliver_writes(self):
        task=self._checker()
        self.assertEqual(self._plan([task],read_only=True)['tasks'][0]['verification_workspace'],'read-only')
        with self.assertRaisesRegex(c.ValidationError,'ceiling'):
            self._plan([dict(task,verification_workspace='disposable')],read_only=True)
        with self.assertRaisesRegex(c.ValidationError,'read-only for deliverables'):
            self._plan([dict(task,read_only=False,writes=True,owned_paths=['tmp'])])
        with self.assertRaisesRegex(c.ValidationError,'read-only and cannot'):
            self._plan([{'task_id':'s','role':'scout','objective':'Find value','read_only':False,'writes':True,'owned_paths':['value.txt']}])

    def test_luna_evidence_cannot_reorder_omit_or_add_checks(self):
        task=self._plan([dict(self._checker(),check_commands=['first','second'])])['tasks'][0]
        state={'run_id':'luna','plan_hash':'0'*64,'manifest_hash':'1'*64,'tasks':{}}
        packet=c._task_input_packet({'tasks':[task]},state,task,'head')
        kw={'prompt':json.dumps(packet),'role':'check_runner','read_only':False}
        for commands in (['first'],['second','first'],['first','second','extra']):
            data=task_result(kw)['final'];data['commands']=commands;data['test_evidence']=[dict(check(),command=cmd) for cmd in commands]
            with self.subTest(commands=commands),self.assertRaises(c.ValidationError):c.validate_task_result(data,'luna',task)
        data=task_result(kw)['final'];data.update(outcome='needs_input',commands=['first'],test_evidence=[dict(check(),command='first',exit_code=1)])
        self.assertEqual(c.validate_task_result(data,'luna',task)['outcome'],'needs_input')
        data.update(commands=['first','second'],test_evidence=[dict(check(),command='first',exit_code=1),dict(check(),command='second')])
        with self.assertRaisesRegex(c.ValidationError,'stop after'):c.validate_task_result(data,'luna',task)

    def test_luna_execution_uses_disposable_clone_and_preserves_source(self):
        for mutate in (False,True):
            with self.subTest(mutate=mutate),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');plan=self._plan([self._checker()])
                run=o.store.create(plan,c.repo_snapshot(repo),o.manifest,'luna');state,plan=o.store.load(run);ctx=o._prepare_task(state,plan,plan['tasks'][0])
                def invoke(**kw):
                    packet=json.loads(kw['prompt']);self.assertEqual(packet['escalation_role'],'tester');self.assertEqual(packet['check_commands'],['python3 -m unittest'])
                    self.assertFalse(kw['read_only']);self.assertNotEqual(Path(kw['cwd']),repo)
                    (Path(kw['cwd'])/'generated.cache').write_text('cache')
                    if mutate:(Path(kw['cwd'])/'value.txt').write_text('bad edit')
                    result=task_result(kw);result['final']['commands']=['python3 -m unittest'];return result
                with mock.patch.object(o.runner,'invoke',side_effect=invoke):
                    if mutate:
                        with self.assertRaisesRegex(c.ValidationError,'verification modified'):o._run_task_process(state,ctx)
                    else:
                        result=o._run_task_process(state,ctx);self.assertEqual(result['record']['requested_runtime']['model'],'gpt-6-luna');self.assertEqual(result['record']['requested_runtime']['reasoning_effort'],'max')
                self.assertEqual((repo/'value.txt').read_text(),'baseline');self.assertFalse((repo/'generated.cache').exists())

    def test_luna_failed_check_hands_off_without_repeated_guessing(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');plan_path=root/'plan.json';plan_path.write_text(json.dumps(self._plan([self._checker()])));calls=[]
            def invoke(**kw):
                calls.append(kw['role'])
                if kw['role']=='conductor':return planned()
                self.assertEqual(kw['role'],'check_runner')
                result=task_result(kw,outcome='needs_input',checks=[dict(check(),exit_code=1)])
                result['final']['commands']=['python3 -m unittest'];return result
            with mock.patch.object(o,'_require_installed_topology'),mock.patch.object(o.runner,'invoke',side_effect=invoke):
                result=o.run(plan_path,run_id='luna')
            self.assertEqual(result['state'],'needs_input');self.assertEqual(calls,['conductor','check_runner'])

    def test_mechanic_uses_existing_commit_and_ownership_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=repo_at(root);o=c.Orchestrator(repo,root/'home');tasks=[self._mechanic(),{'task_id':'verify','role':'tester','objective':'Verify changed value','depends_on':['edit']}]
            path=root/'plan.json';path.write_text(json.dumps(self._plan(tasks)));calls=[]
            def invoke(**kw):
                role=kw['role'];calls.append(role)
                if role=='conductor':return planned()
                if role in ('reviewer','guardian'):return verdict('approve')
                if role=='mechanic':
                    packet=json.loads(kw['prompt']);self.assertEqual(packet['escalation_role'],'worker');self.assertEqual(packet['change_recipe'],self._mechanic()['change_recipe'])
                    (Path(kw['cwd'])/'value.txt').write_text('changed');result=task_result(kw);result['final']['modified_files']=['value.txt'];return result
                return task_result(kw)
            with mock.patch.object(o,'_require_installed_topology'),mock.patch.object(o.runner,'invoke',side_effect=invoke),mock.patch.object(c,'validate_guardian_runtime'):
                result=o.run(path,run_id='luna');self.assertEqual(result['state'],'completed');o.apply('luna')
            self.assertEqual(calls,['conductor','mechanic','tester','reviewer','guardian']);self.assertEqual((repo/'value.txt').read_text(),'changed')
            state,_=o.store.load('luna');self.assertEqual(state['tasks']['edit']['evidence']['commit_owner'],'controller')

if __name__=='__main__':unittest.main()

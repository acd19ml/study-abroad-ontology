"""Model contract tests: synthetic predicates, broken-source rejection, graph paths.

These do not claim command effects, live tools, or full Agent execution work.
"""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('model_checks',ROOT/'tools/checks/validate_model.py')
checks=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class ModelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest,cls.schema,cls.docs=checks.load_model(ROOT)
        cls.index={e['id']:e for _,doc in cls.docs for e in doc['elements']}

    def altered(self):return copy.deepcopy(self.docs)

    def element(self,docs,id):
        return next(e for _,doc in docs for e in doc['elements'] if e['id']==id)

    def result(self,docs=None,**kwargs):
        return checks.validate(ROOT,self.manifest,self.schema,self.docs if docs is None else docs,**kwargs)

    def assertRejected(self,docs,category):
        self.assertTrue(any(e.startswith(category+':') for e in self.result(docs)['errors']),self.result(docs))

    def test_current_source_is_structurally_valid(self):
        result=self.result()
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['checks']['mapping_coverage'],'deferred_until_phase_4')

    def test_unresolved_reference_is_rejected(self):
        docs=self.altered()
        self.element(docs,'rel.ps.task_student')['to']='obj.ps.nonexistent'
        self.assertRejected(docs,'references')

    def test_duplicate_ids_are_rejected(self):
        docs=self.altered()
        docs[0][1]['elements'].append(copy.deepcopy(docs[0][1]['elements'][0]))
        self.assertRejected(docs,'references')

    def test_composition_cannot_cross_aggregate(self):
        docs=self.altered()
        self.element(docs,'rel.ps.task_student')['kind']='composition'
        self.assertRejected(docs,'aggregate_encapsulation')

    def test_member_cannot_own_a_command(self):
        docs=self.altered()
        self.element(docs,'cmd.ps.prepare_chinese')['root']='obj.ps.draft'
        self.assertRejected(docs,'aggregate_encapsulation')

    def test_orphan_state_is_rejected(self):
        docs=self.altered()
        self.element(docs,'obj.ps.task')['lifecycle']['states'].append('orphan_state')
        self.assertRejected(docs,'state_closure')

    def test_state_labels_must_cover_declared_states(self):
        docs=self.altered()
        self.element(docs,'obj.ps.task')['lifecycle']['labels'].pop()
        self.assertRejected(docs,'state_closure')

    def test_duplicate_or_empty_state_label_is_rejected(self):
        for mutation in ('duplicate','empty'):
            with self.subTest(mutation=mutation):
                docs=self.altered()
                labels=self.element(docs,'obj.ps.task')['lifecycle']['labels']
                if mutation=='duplicate':labels[1]['value']=labels[0]['value']
                else:labels[0]['name']=' '
                self.assertRejected(docs,'state_closure')

    def test_transition_without_matching_command_is_rejected(self):
        docs=self.altered()
        self.element(docs,'obj.ps.task')['lifecycle']['transitions'].pop()
        self.assertRejected(docs,'state_closure')

    def test_rule_cannot_reference_undeclared_business_attribute(self):
        docs=self.altered()
        self.element(docs,'rule.ps.generic_draft_optional')['condition']['args'][0]['attribute']='sql_column_that_is_not_a_concept'
        self.assertRejected(docs,'concept_references')

    def test_invalid_rule_action_is_rejected(self):
        docs=self.altered()
        self.element(docs,'rule.ps.generic_draft_optional')['action']='run_arbitrary_code'
        self.assertRejected(docs,'schema')

    def test_unknown_fields_are_rejected(self):
        docs=self.altered()
        self.element(docs,'obj.ps.task')['unregistered_label']='业务特性'
        self.assertRejected(docs,'schema')

    def test_role_must_explicitly_cover_command(self):
        docs=self.altered()
        self.element(docs,'role.ps.agent')['commands'].remove('cmd.ps.generate_english')
        self.assertRejected(docs,'role_coverage')

    def test_source_is_required_for_rule(self):
        docs=self.altered()
        self.element(docs,'rule.ps.unknown_requirement')['refs']=[]
        self.assertRejected(docs,'rule_completeness')

    def test_escalation_has_a_human_decision_point(self):
        docs=self.altered()
        self.element(docs,'hdp.ps.missing_requirements')['at']='cmd.ps.resolve_issue'
        self.assertRejected(docs,'rule_completeness')

    def test_metric_must_measure_existing_model_concepts(self):
        docs=self.altered()
        self.element(docs,'metric.ps.manual_context_categories')['inputs']=['obj.ps.context_packet.fake_counter']
        self.assertRejected(docs,'concept_references')

    def test_phase_four_does_require_implementation_mappings(self):
        result=self.result(phase=4)
        self.assertTrue(any(e.startswith('mapping_coverage:') for e in result['errors']))

    def test_draft_and_open_gates_cannot_be_released(self):
        result=self.result(release=True)
        self.assertTrue(any(e.startswith('release:') for e in result['errors']))

    def test_unsupported_schema_keyword_even_in_unused_definition_fails(self):
        schema=copy.deepcopy(self.schema)
        schema['$defs']['unused']={'type':'string','unsupported_validation':True}
        with self.assertRaises(ValueError):checks.check_schema_contract(schema)

    def test_anyof_does_not_bypass_sibling_constraint(self):
        schema={'anyOf':[{'type':'string'}],'enum':['allowed']}
        self.assertTrue(checks.schema_check('other',schema,schema))

    def test_reference_does_not_bypass_sibling_constraint(self):
        schema={'$defs':{'text':{'type':'string'}},'$ref':'#/$defs/text','enum':['allowed']}
        self.assertTrue(checks.schema_check('other',schema,schema))

    def test_duplicate_yaml_keys_do_not_silently_override(self):
        with self.assertRaises(ValueError):
            checks.yaml.load('state: confirmed\nstate: unknown\n',Loader=checks.UniqueLoader)

    def test_core_context_dependencies_have_declared_paths(self):
        edges=[e for e in self.index.values() if e['type']=='relation']
        reached={'obj.ps.task'}
        while True:
            more={e['to'] for e in edges if e['from'] in reached}-reached
            if not more:break
            reached.update(more)
        self.assertTrue({'obj.ps.student_context','obj.ps.program_knowledge','obj.ps.course',
                         'obj.ps.requirement','obj.ps.background_fact','obj.ps.background_material',
                         'obj.ps.draft','obj.ps.confirmation'}<=reached)

    def test_synthetic_business_predicates(self):
        cases=checks.read_yaml(ROOT/'tests/model/scenarios.yaml')['cases']
        for case in cases:
            with self.subTest(case=case['name']):
                rule=self.index[case['rule']]
                result=checks.evaluate(rule['condition'],case['facts'])
                if case['matched']=='unknown':self.assertIs(result,checks.UNKNOWN)
                else:self.assertIs(result,case['matched'])
                if case.get('action'):self.assertEqual(rule['action'],case['action'])

    def test_incomparable_length_is_unknown_not_compliant(self):
        rule=self.index['rule.ps.ps_length_limit']
        facts={'obj.ps.requirement':[{'kind':'ps_length','finding':'known','value':500,'unit':'words'}],
               'obj.ps.check_report':{'known_requirements_passed':True,'measured_length':None,'length_unit':'words'}}
        self.assertIs(checks.evaluate(rule['condition'],facts),checks.UNKNOWN)

    def test_unbound_concept_is_rejected(self):
        docs=self.altered()
        del self.element(docs,'rule.ps.confirm_current_chinese')['bindings']
        self.assertRejected(docs,'concept_references')

    def test_binding_path_must_start_from_bound_object(self):
        docs=self.altered()
        self.element(docs,'rule.ps.unknown_requirement')['condition']['bind']['via']=['rel.ps.knowledge_requirements']
        self.assertRejected(docs,'concept_references')

    def test_collection_cannot_be_bound_as_single_record(self):
        docs=self.altered()
        rule=self.element(docs,'rule.ps.final_known_requirements')
        rule['bindings']=[{'concept':'obj.ps.check_report','via':['rel.ps.task_checks']}]
        rule['condition']=rule['condition']['args'][0]
        self.assertRejected(docs,'concept_references')

    def test_quantifier_requires_bind(self):
        docs=self.altered()
        del self.element(docs,'rule.ps.official_source')['condition']['bind']
        self.assertRejected(docs,'concept_references')

    def test_escalation_cannot_target_human_executed_command(self):
        docs=self.altered()
        rule=self.element(docs,'rule.ps.unknown_requirements_human_review')
        rule['applies_to']=['cmd.ps.confirm_final']
        rule['bindings']=[{'concept':'obj.ps.check_report','via':['rel.ps.task_checks']}]
        self.assertRejected(docs,'rule_completeness')

    def test_quantified_facts_must_be_a_list(self):
        rule=self.index['rule.ps.official_source']
        with self.assertRaises(ValueError):
            checks.evaluate(rule['condition'],{'obj.ps.requirement':{'source_kind':'official_website'}})

    def test_requirement_records_keep_their_own_source(self):
        names=lambda id:{a['name'] for a in self.index[id]['attributes']}
        self.assertIn('source_kind',names('obj.ps.requirement'))
        self.assertNotIn('source_kind',names('obj.ps.program_knowledge'))

    def test_consultant_records_without_required_evidence(self):
        for oid,attr in [('obj.ps.background_fact','verification_ref'),('obj.ps.continuation_decision','customer_evidence_ref')]:
            self.assertTrue(next(a for a in self.index[oid]['attributes'] if a['name']==attr)['nullable'])
        required=[e['id'] for e in self.index.values() if e['type']=='rule' and any(
            t.get('attribute') in {'verification_ref','customer_evidence_ref','evidence_ref'} for t in checks.terms(e['condition']))]
        self.assertEqual(required,[])

    def commands_on(self,root):
        return [e for e in self.index.values() if e['type']=='command' and e['root']==root]

    def transitions(self,command):
        return {(t['from'],t['to']) for t in self.index['obj.ps.task']['lifecycle']['transitions'] if t['by']==command}

    def test_withdrawn_task_only_records_reminders_and_human_actions(self):
        ai=[c['id'] for c in self.commands_on('obj.ps.task') if c['role']=='role.ps.agent' and 'withdrawn' in c['allowed_in']]
        self.assertEqual(ai,['cmd.ps.record_change_impact'])

    def test_restore_returns_to_any_state_before_withdrawal(self):
        before=set(self.index['cmd.ps.record_withdrawal']['allowed_in'])
        self.assertEqual({t for f,t in self.transitions('cmd.ps.restore_application')},before)

    def test_submitted_is_terminal_and_stops_reminders(self):
        self.assertFalse([t for t in self.index['obj.ps.task']['lifecycle']['transitions'] if t['from']=='submitted'])
        allowed=self.index['cmd.ps.record_change_impact']['allowed_in']
        self.assertNotIn('submitted',allowed)
        self.assertIn('consultant_confirmed',allowed);self.assertIn('withdrawn',allowed)
        self.assertEqual(self.index['cmd.ps.record_submission']['allowed_in'],['consultant_confirmed'])

    def test_english_wording_revision_stays_on_confirmed_chinese(self):
        self.assertEqual(self.transitions('cmd.ps.revise_english_wording'),
                         {(s,'english_prepared') for s in ['english_prepared','checked','consultant_confirmed']})
        self.assertIn('cmd.ps.check_english',self.index['rule.ps.english_matches_chinese']['applies_to'])

    def test_direction_drafts_belong_to_student_not_project_task(self):
        self.assertEqual(self.index['obj.ps.direction_draft']['aggregate'],'agg.ps.student_context')
        attributes={a['name']:a for a in self.index['obj.ps.draft']['attributes']}
        self.assertNotIn('purpose',attributes);self.assertFalse(attributes['program_ref']['nullable'])

    def test_every_change_source_reminds_unsubmitted_tasks(self):
        policies=[e for e in self.index.values() if e['type']=='policy']
        reminders={p['on'] for p in policies if p['then']=='cmd.ps.record_change_impact'}
        self.assertEqual(reminders,{'evt.ps.official_knowledge_refreshed','evt.ps.portal_feedback_recorded','evt.ps.student_context_refreshed'})
        sync=[p for p in policies if 'schedule' in p]
        self.assertEqual([p['then'] for p in sync],['cmd.ps.refresh_official_knowledge'])
        self.assertEqual(self.index['cmd.ps.refresh_official_knowledge']['execution_level'],'自动执行')

    def test_policy_needs_exactly_one_trigger(self):
        docs=self.altered()
        self.element(docs,'pol.ps.monthly_official_sync')['on']='evt.ps.student_context_refreshed'
        self.assertRejected(docs,'references')

    def test_eval_question_evidence_exists_in_model(self):
        import sys
        sys.path.insert(0,str(ROOT/'tools/checks'))
        import check_eval_set
        result=check_eval_set.check()
        self.assertEqual(result['errors'],[])
        self.assertEqual(len(result['supported'])+len(result['gaps']),result['total'])

    def test_student_confirmation_is_recorded_by_consultant(self):
        self.assertEqual(self.index['cmd.ps.confirm_chinese']['role'],'role.ps.consultant')
        evidence=next(a for a in self.index['obj.ps.confirmation']['attributes'] if a['name']=='evidence_ref')
        self.assertTrue(evidence['nullable'])


if __name__=='__main__':unittest.main()

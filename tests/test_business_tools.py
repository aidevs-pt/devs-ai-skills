"""Independent assertions for material business rules, not only golden-file equality."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILLS=ROOT/'.agents/skills'


def example(name):
    return json.loads((SKILLS/name/'assets/example-input.json').read_text(encoding='utf-8'))


def tool(name,filename):
    p=SKILLS/name/'scripts'/filename
    sys.path.insert(0,str(p.parent))
    try:
        spec=importlib.util.spec_from_file_location('devs_'+name.replace('-','_')+'_'+p.stem,p)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module
    finally:sys.path.pop(0)


class CatalogTests(unittest.TestCase):
    def setUp(self):self.mod=tool('supplier-catalog-to-store','prepare_catalog.py');self.data=example('supplier-catalog-to-store')
    def test_preserves_variant_quantities_and_unapproved_rows(self):
        r=self.mod.process(self.data)
        self.assertIn('250 ml',r['records'][0]['draft_description'])
        self.assertNotIn('500 ml',r['records'][0]['draft_description'])
        self.assertEqual(r['records'][2]['status'],'needs_review')
        self.assertEqual(len(r['records']),3)
    def test_duplicate_skus_are_both_flagged(self):
        self.data['products'].append(copy.deepcopy(self.data['products'][0]))
        r=self.mod.process(self.data)
        self.assertEqual(sum(x['code']=='duplicate_sku' for x in r['issues']),2)
    def test_active_csv_formula_is_escaped(self):
        self.data['products'][0]['title']='=HYPERLINK("https://example.invalid","x")'
        r=self.mod.process(self.data)
        self.assertIn("'=HYPERLINK",r['import_csv'])
    def test_nan_quantity_never_becomes_ready(self):
        self.data['products'][0]['quantity']='NaN'
        r=self.mod.process(self.data)
        self.assertIn('invalid_quantity',[x['code'] for x in r['issues']])


class SupportTests(unittest.TestCase):
    def setUp(self):self.mod=tool('ecommerce-support-copilot','prepare_replies.py');self.data=example('ecommerce-support-copilot')
    def test_partial_order_is_not_promised_as_delivered(self):
        r=self.mod.process(self.data)
        self.assertIn('partially shipped',r['tickets'][0]['draft'])
        self.assertNotIn('tomorrow',r['tickets'][0]['draft'])
        self.assertFalse(r['sent']);self.assertFalse(r['refunds_issued'])
    def test_identity_mismatch_discloses_no_order_facts(self):
        r=self.mod.process(self.data)['tickets'][1]
        self.assertIsNone(r['draft']);self.assertEqual(r['facts'],{});self.assertEqual(r['sources'],[])
    def test_wrong_region_does_not_use_policy(self):
        self.data['policies'][0]['region']='DE'
        r=self.mod.process(self.data)['tickets'][2]
        self.assertIsNone(r['draft']);self.assertIn('resolve_policy_region_mismatch',r['actions'])
    def test_duplicate_ticket_id_is_invalid(self):
        self.data['tickets'].append(self.data['tickets'][0])
        with self.assertRaises(ValueError):self.mod.process(self.data)


class KnowledgeTests(unittest.TestCase):
    def setUp(self):self.mod=tool('company-knowledge-qa','resolve_sources.py');self.data=example('company-knowledge-qa')
    def test_expired_source_excluded_and_conflict_preserved(self):
        r=self.mod.process(self.data)
        self.assertEqual(r['conflicts'][0]['topic'],'subscriptions')
        ids=[x['source_id'] for x in r['questions'][0]['evidence']]
        self.assertIn('RET-CURRENT',ids);self.assertNotIn('RET-OLD',ids)
    def test_unanswerable_question_keeps_insufficient_evidence(self):
        self.assertEqual(self.mod.process(self.data)['questions'][2]['answer_status'],'insufficient_evidence')
    def test_out_of_scope_and_future_documents_are_not_evidence(self):
        self.data['scope']='DE'
        self.assertTrue(all(not x['eligible'] for x in self.mod.process(self.data)['source_manifest']))
        self.data['scope']='PT';self.data['as_of']='2025-01-01'
        self.assertEqual(self.mod.process(self.data)['questions'][0]['evidence'],[])


class PurchaseOrderTests(unittest.TestCase):
    def setUp(self):self.mod=tool('purchase-order-intake','match_orders.py');self.data=example('purchase-order-intake')
    def test_explicit_pack_conversion_and_ambiguous_alias(self):
        r=self.mod.process(self.data)
        self.assertEqual(r['orders'][0]['lines'][0]['quantity'],'24')
        self.assertEqual(len(r['orders'][0]['lines']),1)
        self.assertIn('ambiguous_product',[x['code'] for x in r['orders'][0]['exceptions']])
        self.assertEqual(r['orders'][0]['status'],'draft_incomplete');self.assertFalse(r['submitted'])
    def test_unknown_pack_size_is_not_guessed(self):
        self.data['orders'][0]['lines'][0]['unit']='carton'
        self.assertIn('unknown_unit_conversion',[x['code'] for x in self.mod.process(self.data)['orders'][0]['exceptions']])
    def test_aliases_string_is_rejected(self):
        self.data['catalog'][0]['aliases']='OLD-CUP'
        with self.assertRaises(ValueError):self.mod.process(self.data)


class FinderTests(unittest.TestCase):
    def setUp(self):self.mod=tool('product-finder-builder','build_finder.py');self.data=example('product-finder-builder')
    def test_html_contains_no_external_library_or_model_call(self):
        r=self.mod.process(self.data)
        self.assertEqual(r['runtime'],'local_rule_based');self.assertFalse(r['live_inventory'])
        self.assertNotIn('<script src=',r['html']);self.assertNotIn('fetch(',r['html'])
        self.assertIn('p.available',r['html']);self.assertIn('No matching products',r['html'])
    def test_catalog_script_close_is_escaped(self):
        self.data['products'][0]['name']='</script><script>alert(1)</script>'
        r=self.mod.process(self.data)
        payload=r['html'].split('id="finder-data">',1)[1].split('</script>',1)[0]
        self.assertNotIn('<',payload)
        self.assertEqual(json.loads(payload)['products'][0]['name'],self.data['products'][0]['name'])
    def test_javascript_product_link_is_rejected(self):
        self.data['products'][0]['url']='javascript:alert(1)'
        with self.assertRaises(ValueError):self.mod.process(self.data)
    def test_mixed_currency_and_unknown_constraints_rejected(self):
        self.data['products'][0]['currency']='USD'
        with self.assertRaises(ValueError):self.mod.process(self.data)
        self.data=example('product-finder-builder');self.data['questions'][0]['options'][0]['where']={'invented':True}
        with self.assertRaises(ValueError):self.mod.process(self.data)


class WorkflowTests(unittest.TestCase):
    def setUp(self):self.mod=tool('sop-to-ai-workflow','check_workflow.py');self.data=example('sop-to-ai-workflow')
    def test_good_contract_does_not_claim_execution(self):
        r=self.mod.process(self.data);self.assertTrue(r['contract_valid']);self.assertFalse(r['executed_workflow'])
    def test_cycle_missing_inputs_and_missing_review_detected(self):
        self.data['steps'][0]['depends_on']=['update']
        self.assertIn('dependency_cycle',[x['code'] for x in self.mod.process(self.data)['issues']])
        self.data=example('sop-to-ai-workflow');self.data['steps'][-1]['inputs']=[];self.data['steps'][-1]['depends_on']=[]
        self.assertIn('external_action_without_review',[x['code'] for x in self.mod.process(self.data)['issues']])
        self.data['steps'][0]['inputs'].append('missing_file')
        self.assertIn('missing_input',[x['code'] for x in self.mod.process(self.data)['issues']])
    def test_supplied_price_example_completes_real_work(self):
        m=tool('sop-to-ai-workflow','compare_prices.py')
        d=json.loads((SKILLS/'sop-to-ai-workflow/assets/price-update-input.json').read_text())
        r=m.process(d);self.assertEqual(r['changes'][0]['change_percent'],'20.00')
        self.assertEqual(r['exceptions'][0]['code'],'unknown_sku');self.assertFalse(r['live_prices_changed'])


class QuoteTests(unittest.TestCase):
    def setUp(self):self.mod=tool('rfq-to-quote','build_quote.py');self.data=example('rfq-to-quote')
    def test_decimal_line_rounding_and_tax(self):
        r=self.mod.process(self.data)
        self.assertEqual(r['lines'][0]['line_total'],'0.30')
        self.assertEqual(r['lines'][1]['line_total'],'24.69')
        self.assertEqual(r['confirmed_lines_subtotal'],'24.99')
        self.assertEqual(r['tax'],'5.75');self.assertEqual(r['total'],'30.74');self.assertFalse(r['sent'])
    def test_unmatched_line_blocks_complete_total(self):
        self.data['request'].append({'id':'L3','sku':'UNKNOWN','quantity':'1'})
        r=self.mod.process(self.data);self.assertIsNone(r['total']);self.assertEqual(r['status'],'draft_incomplete')
    def test_no_invented_tax_or_unsourced_price(self):
        del self.data['tax_rate'];r=self.mod.process(self.data);self.assertIsNone(r['tax']);self.assertIsNone(r['total'])
        self.data=example('rfq-to-quote');del self.data['catalog'][0]['price_source']
        self.assertEqual(self.mod.process(self.data)['exceptions'][0]['code'],'unapproved_or_unsourced_price')
    def test_tax_needs_supplied_rule_source(self):
        del self.data['tax_rule_source']
        with self.assertRaises(ValueError):self.mod.process(self.data)


class LocalizationTests(unittest.TestCase):
    def setUp(self):self.mod=tool('multilingual-catalog-launch','check_localization.py');self.data=example('multilingual-catalog-launch')
    def test_stale_revision_and_native_review_are_visible(self):
        r=self.mod.process(self.data)
        self.assertIn({'sku':'B250','code':'stale_source_revision'},r['issues'])
        self.assertTrue(r['native_review_required']);self.assertEqual(r['semantic_quality'],'not_measured')
    def test_changed_facts_placeholders_and_missing_translation_detected(self):
        self.data['localized'][0]['facts']['capacity_ml']=500
        self.data['localized'][0]['description']='Uma garrafa.'
        self.data['localized'].pop()
        codes=[x['code'] for x in self.mod.process(self.data)['issues']]
        for code in ['protected_facts_changed','protected_spans_changed','missing_translation']:self.assertIn(code,codes)


class FeedbackTests(unittest.TestCase):
    def setUp(self):self.mod=tool('customer-feedback-to-fixes','group_feedback.py');self.data=example('customer-feedback-to-fixes')
    def test_proven_duplicates_and_unknown_customer_counts(self):
        r=self.mod.process(self.data);group=r['groups'][0]
        self.assertEqual(group['record_count'],3);self.assertEqual(group['known_unique_customers'],2)
        self.assertIsNone(group['total_unique_customers']);self.assertEqual(len(r['duplicates']),1)
        self.assertEqual(r['unclassified'],['F5'])
    def test_same_customer_text_on_different_product_is_not_duplicate(self):
        extra=copy.deepcopy(self.data['items'][0]);extra['id']='F6';extra['product']='SHOES';self.data['items'].append(extra)
        r=self.mod.process(self.data);self.assertEqual(len(r['groups']),2);self.assertEqual(len(r['duplicates']),1)
    def test_identical_anonymous_records_are_preserved(self):
        self.data['items']=[{'id':'1','text':'Wrong size','theme':'fit'},{'id':'2','text':'Wrong size','theme':'fit'}]
        r=self.mod.process(self.data);self.assertEqual(r['groups'][0]['record_count'],2);self.assertEqual(r['duplicates'],[])


class OpportunityTests(unittest.TestCase):
    def setUp(self):self.mod=tool('ai-automation-opportunity-finder','rank_opportunities.py');self.data=example('ai-automation-opportunity-finder')
    def test_review_cost_negative_savings_and_unknowns_preserved(self):
        r=self.mod.process(self.data)
        self.assertEqual(r['ranked_scenarios'][0]['scenario_hours_saved'],'6.33')
        self.assertLess(float(r['ranked_scenarios'][1]['scenario_hours_saved']),0)
        self.assertEqual(r['needs_more_information'][0]['id'],'unknown-volume')
        self.assertTrue(all(x['net_roi'] is None for x in r['ranked_scenarios']))
    def test_fraction_above_one_rejected(self):
        self.data['tasks'][0]['automatable_fraction']='1.1'
        with self.assertRaises(ValueError):self.mod.process(self.data)


class SharedInputTests(unittest.TestCase):
    def test_duplicate_json_key_and_nan_rejected(self):
        script=SKILLS/'rfq-to-quote/scripts/build_quote.py'
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temp:
            f=Path(temp)/'bad.json'
            for text in ['{"currency":"EUR","currency":"USD"}','{"tasks":NaN}']:
                f.write_text(text)
                p=subprocess.run([sys.executable,str(script),'--input',str(f)],capture_output=True,text=True)
                self.assertEqual(p.returncode,2)
    def test_output_does_not_overwrite_existing_file(self):
        script=SKILLS/'rfq-to-quote/scripts/build_quote.py'
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as temp:
            dest=Path(temp)/'output.json';dest.write_text('my work')
            p=subprocess.run([sys.executable,str(script),'--input',str(SKILLS/'rfq-to-quote/assets/example-input.json'),'--output',str(dest)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertEqual(dest.read_text(),'my work')


if __name__=='__main__':unittest.main()

"""Projection provenance and synchronization tests; no real browser required."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('model_projection',ROOT/'tools/generator/render_model.py')
projection=importlib.util.module_from_spec(spec);spec.loader.exec_module(projection)


class FirstPaint(HTMLParser):
    """Observe actual HTML markup; intentionally do not execute JavaScript."""
    def __init__(self):
        super().__init__();self.nodes=[];self.script=False;self.text=[]

    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='script':self.script=True
        if not self.script and 'data-node-id' in values:self.nodes.append(values['data-node-id'])

    def handle_endtag(self,tag):
        if tag=='script':self.script=False

    def handle_data(self,data):
        if not self.script:self.text.append(data)


class ProjectionTests(unittest.TestCase):
    def test_first_paint_has_model_data_before_javascript_initializes(self):
        page=FirstPaint();page.feed((ROOT/projection.OUTPUT).read_text())
        expected=[e['id'] for e in projection.build_payload()['elements'] if e['type']=='object']
        self.assertEqual(set(page.nodes),set(expected),'Opening the HTML must show source-derived graph data before JS initializes')
        self.assertIn('项目 PS 准备任务',''.join(page.text))
        self.assertIn(projection.build_payload()['meta']['generator_hash'][:12],''.join(page.text),'The updated HTML build must be recognizable even before JS runs')

    def test_all_source_elements_and_properties_are_preserved(self):
        payload=projection.build_payload()
        _,_,docs=projection.load_model()
        source=[e for _,doc in docs for e in doc['elements']]
        self.assertEqual([e['id'] for e in payload['elements']],[e['id'] for e in source])
        for expected,actual in zip(source,payload['elements']):
            self.assertEqual(expected,{k:v for k,v in actual.items() if k!='_source'})

    def test_every_explicit_relation_is_projected_exactly(self):
        payload=projection.build_payload()
        relations={e['id']:e for e in payload['elements'] if e['type']=='relation'}
        edges={e['id']:e for e in payload['edges'] if e['projection']=='explicit_relation'}
        self.assertEqual(set(relations),set(edges))
        for id,relation in relations.items():
            self.assertEqual((edges[id]['source'],edges[id]['target'],edges[id]['label']),
                             (relation['from'],relation['to'],relation['name']))

    def test_lifecycle_labels_and_commands_come_from_source(self):
        payload=projection.build_payload();records={e['id']:e for e in payload['elements']}
        for life in payload['lifecycles']:
            source=records[life['object']]['lifecycle']
            self.assertEqual(len(life['edges']),len(source['transitions']))
            labels={x['value']:x['name'] for x in source['labels']}
            for n in life['nodes']:
                if n['value'] is not None:self.assertEqual(n['name'],labels[n['value']])
            for e in life['edges']:self.assertEqual(e['label'],records[e['command']]['name'])

    def test_output_is_deterministic_and_payload_is_parseable(self):
        first=projection.render();self.assertEqual(first,projection.render())
        data=json.loads(re.search(r'<script id="model-data" type="application/json">(.*?)</script>',first,re.S).group(1))
        self.assertEqual(len(data['meta']['source_hash']),64)
        self.assertEqual(data['meta']['version'],projection.load_model()[0]['version'])
        self.assertNotRegex(first,r'@@[A-Z][A-Z_0-9]*@@')

    def copy_fixture(self,destination):
        shutil.copytree(ROOT/'model',destination/'model')
        (destination/'tools/generator/templates').mkdir(parents=True)
        shutil.copy2(ROOT/'tools/generator/render_model.py',destination/'tools/generator/render_model.py')
        shutil.copy2(ROOT/projection.TEMPLATE,destination/projection.TEMPLATE)
        for _,doc in projection.load_model()[2]:
            for e in doc['elements']:
                for source in e['refs']:
                    target=destination/source;target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(ROOT/source,target)

    def test_source_change_requires_regeneration_and_manual_edit_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.copy_fixture(root)
            projection.write_or_check(root)
            original=(root/projection.OUTPUT).read_text()
            path=root/'model/contexts/ps/objects.yaml'
            path.write_text(path.read_text().replace('name: 项目 PS 准备任务','name: 项目 PS 准备任务（测试改名）',1))
            with self.assertRaises(ValueError):projection.write_or_check(root,check=True)
            projection.write_or_check(root)
            updated=(root/projection.OUTPUT).read_text()
            self.assertNotEqual(original,updated);self.assertIn('项目 PS 准备任务（测试改名）',updated)
            projection.write_or_check(root,check=True)
            (root/projection.OUTPUT).write_text(updated+'\n<!-- manual edit -->')
            with self.assertRaises(ValueError):projection.write_or_check(root,check=True)

    def test_invalid_source_does_not_overwrite_last_valid_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.copy_fixture(root);projection.write_or_check(root)
            original=(root/projection.OUTPUT).read_text()
            path=root/'model/contexts/ps/rules.yaml'
            path.write_text(path.read_text().replace('action: deny','action: invalid_action',1))
            with self.assertRaises(ValueError):projection.write_or_check(root)
            self.assertEqual((root/projection.OUTPUT).read_text(),original)

    def test_unexpanded_template_slot_cannot_be_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.copy_fixture(root)
            projection.write_or_check(root)
            original=(root/projection.OUTPUT).read_text()
            path=root/projection.TEMPLATE
            path.write_text(path.read_text().replace('</body>','<p>@@UNEXPANDED_SLOT@@</p></body>'))
            with self.assertRaises(ValueError):projection.write_or_check(root)
            self.assertEqual((root/projection.OUTPUT).read_text(),original)

    def test_html_like_model_text_round_trips_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.copy_fixture(root)
            path=root/'model/contexts/ps/value.yaml'
            value=projection.yaml.safe_load(path.read_text())
            sample='测试 <条件> </script> 与 & 文本'
            goal=next(e for e in value['elements'] if e['type']=='goal')
            goal['description']=sample
            path.write_text(projection.yaml.safe_dump(value,allow_unicode=True,sort_keys=False))
            html=projection.render(root)
            match=re.search(r'<script id="model-data" type="application/json">(.*?)</script>',html,re.S)
            payload=json.loads(match.group(1))
            self.assertEqual(next(e for e in payload['elements'] if e['type']=='goal')['description'],sample)

    @unittest.skipUnless(shutil.which('node'),'Node.js is optional and required for DOM simulation')
    def test_real_inline_script_interactions_under_dom_simulation(self):
        result=subprocess.run([shutil.which('node'),str(ROOT/'tests/generator/dom_smoke.cjs'),str(ROOT/projection.OUTPUT)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('assertions passed',result.stdout)

    @unittest.skipUnless(shutil.which('node'),'Node.js is required for template-entry simulation')
    def test_opening_internal_template_explains_correct_entry(self):
        result=subprocess.run([shutil.which('node'),str(ROOT/'tests/generator/dom_smoke.cjs'),str(ROOT/projection.TEMPLATE),'--template'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('without a JSON parse crash',result.stdout)


if __name__=='__main__':unittest.main()

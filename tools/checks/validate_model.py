#!/usr/bin/env python3
"""Validate the draft model source; no application writes or external calls.

The structural checker implements exactly the JSON Schema keywords used by the
repository schema. Unsupported keywords fail rather than being silently ignored.
Rule evaluation is a small, three-valued business-predicate evaluator for model
walkthroughs, not the runtime command/authorization implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from pathlib import Path
import re
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[2]
ID_RE = re.compile(r"^(goal|metric|ctx|obj|rel|agg|cmd|evt|rule|pol|role|hdp|map)\.[a-z0-9_]+\.[a-z0-9_]+$")
PREFIX = {"context":"ctx", "object":"obj", "relation":"rel", "aggregate":"agg",
          "command":"cmd", "event":"evt", "policy":"pol", "human_decision_point":"hdp", "mapping":"map"}
SECTIONS = {
    "value": {"context", "goal", "metric"}, "objects": {"object", "relation"},
    "aggregates": {"aggregate", "command", "event"}, "rules": {"rule", "human_decision_point"},
    "policies": {"policy"}, "roles": {"role"}, "mappings": {"mapping"},
}
CHECKS = ["schema", "references", "aggregate_encapsulation", "state_closure",
          "rule_completeness", "concept_references", "metric_computability", "role_coverage", "mapping_coverage"]


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path):
    return yaml.load(path.read_text(), Loader=UniqueLoader)


def schema_check(value, spec, schema, path="$", check_keywords=True):
    allowed = {"$schema", "$id", "$defs", "$ref", "title", "type", "enum", "pattern", "anyOf",
               "properties", "required", "additionalProperties", "items", "minItems"}
    if check_keywords and set(spec) - allowed:
        raise ValueError(f"Unsupported schema keywords: {sorted(set(spec)-allowed)}")
    errors = []
    if "$ref" in spec:
        ref = spec["$ref"]
        if not ref.startswith("#/$defs/"):
            raise ValueError(f"Unsupported schema reference: {ref}")
        errors.extend(schema_check(value, schema["$defs"][ref.split("/")[-1]], schema, path))
    if "anyOf" in spec:
        for branch in spec["anyOf"]:
            if not schema_check(value, branch, schema, path):
                break
        else:
            errors.append(f"{path}: does not match any allowed schema variant")
    types = {
        "object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str), "boolean": lambda v: isinstance(v, bool),
        "number": lambda v: isinstance(v, (int,float)) and not isinstance(v,bool),
        "null": lambda v: v is None,
    }
    if "type" in spec:
        if spec["type"] not in types:
            raise ValueError(f"Unsupported schema type: {spec['type']}")
        if not types[spec["type"]](value):
            return errors + [f"{path}: expected {spec['type']}"]
    if "enum" in spec and not any(type(value) is type(v) and value == v for v in spec["enum"]):
        errors.append(f"{path}: value outside enum")
    if "pattern" in spec and isinstance(value,str) and not re.search(spec["pattern"],value):
        errors.append(f"{path}: invalid pattern")
    if isinstance(value,dict):
        props=spec.get("properties",{})
        for key in spec.get("required",[]):
            if key not in value: errors.append(f"{path}: missing {key}")
        if spec.get("additionalProperties") is False:
            for key in value.keys()-props.keys(): errors.append(f"{path}: unexpected {key}")
        for key in value.keys() & props.keys():
            errors.extend(schema_check(value[key],props[key],schema,f"{path}.{key}"))
    if isinstance(value,list):
        if len(value)<spec.get("minItems",0): errors.append(f"{path}: too few items")
        for i,item in enumerate(value):
            errors.extend(schema_check(item,spec.get("items",{}),schema,f"{path}[{i}]"))
    return errors


def check_schema_contract(schema, root_schema=None):
    """Check all branches, including definitions not reached by current data."""
    root_schema=root_schema or schema
    allowed={"$schema", "$id", "$defs", "$ref", "title", "type", "enum", "pattern", "anyOf",
             "properties", "required", "additionalProperties", "items", "minItems"}
    if set(schema)-allowed:raise ValueError(f'Unsupported schema keywords: {sorted(set(schema)-allowed)}')
    if '$ref' in schema:
        ref=schema['$ref']
        if not ref.startswith('#/$defs/') or ref.split('/')[-1] not in root_schema.get('$defs',{}):
            raise ValueError(f'Unsupported/missing schema reference: {ref}')
    for branch in schema.get('anyOf',[]):check_schema_contract(branch,root_schema)
    for child in schema.get('properties',{}).values():check_schema_contract(child,root_schema)
    for child in schema.get('$defs',{}).values():check_schema_contract(child,root_schema)
    if 'items' in schema:check_schema_contract(schema['items'],root_schema)


def load_model(root=ROOT):
    manifest=read_yaml(root/'model/model.yaml')
    schema=json.loads((root/manifest['schema']).read_text())
    docs=[]
    for relative in manifest['files']:
        path=(root/relative).resolve()
        if not path.is_relative_to((root/'model/contexts').resolve()):
            raise ValueError(f"Model document outside contexts: {relative}")
        docs.append((relative,read_yaml(path)))
    return manifest, schema, docs


def all_values(value):
    if isinstance(value,dict):
        for child in value.values(): yield from all_values(child)
    elif isinstance(value,list):
        for child in value: yield from all_values(child)
    else: yield value


def terms(condition):
    if isinstance(condition,dict):
        if 'concept' in condition: yield condition
        for child in condition.get('args',[]): yield from terms(child)


def validate(root, manifest, schema, docs, phase=2, release=False):
    result={'version':manifest['version'],'mode':'release' if release else 'draft',
            'checks':{k:'not_run' for k in CHECKS},'errors':[],'warnings':[], 'counts':{}}
    errors=result['errors']
    def error(check,message): errors.append(f"{check}: {message}")
    check_schema_contract(schema)
    for filename,doc in docs:
        for message in schema_check(doc,schema,schema,filename): error('schema',message)
        if isinstance(doc,dict) and doc.get('model_version')!=manifest['version']:
            error('schema',f'{filename}: model version differs from manifest')
        for e in doc.get('elements',[]) if isinstance(doc,dict) else []:
            if isinstance(e,dict) and e.get('type') not in SECTIONS.get(Path(filename).stem,set()):
                error('schema',f'{filename}: wrong element type {e.get("type")}')
    actual={str(p.relative_to(root)) for p in (root/'model/contexts').rglob('*.yaml')}
    if actual!=set(manifest['files']): error('schema','Manifest must list exactly the context YAML files')
    result['checks']['schema']='failed' if errors else 'passed'
    if errors: return result
    elements=[e for _,doc in docs for e in doc['elements']]
    index={e['id']:e for e in elements}
    result['counts']=dict(sorted(Counter(e['type'] for e in elements).items()))
    if len(index)!=len(elements): error('references','Duplicate element IDs')

    def typed(ref,allowed,where):
        target=index.get(ref)
        if target is None or target['type'] not in allowed:
            error('references',f'{where}: {ref} must reference {sorted(allowed)}')
        return target

    def attribute_ref(value,where):
        parts=value.rsplit('.',1)
        target=index.get(parts[0]) if len(parts)==2 else None
        if not target or target['type']!='object' or not any(a['name']==parts[1] for a in target['attributes']):
            error('concept_references',f'{where}: invalid business attribute {value}')

    for e in elements:
        if e['id'].split('.')[0]!=PREFIX.get(e['type'],e['type']):
            error('references',f"{e['id']}: prefix does not match type")
        if e['id'].split('.')[1]!=e['context'].split('.')[1]:
            error('references',f"{e['id']}: ID namespace differs from context")
        typed(e['owner'],{'role'},e['id']+'.owner')
        typed(e['context'],{'context'},e['id']+'.context')
        for value in all_values(e):
            if isinstance(value,str) and ID_RE.fullmatch(value):
                if value not in index: error('references',f"{e['id']}: missing {value}")
                elif index[value]['status']=='deprecated': error('references',f"{e['id']}: references deprecated {value}")
        for source in e['refs']:
            path=(root/unquote(source.split('#')[0])).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                error('references',f"{e['id']}: missing source {source}")
            elif path.suffix=='.md' and e['id'] not in path.read_text():
                error('references',f"{e['id']}: source lacks model backlink: {source}")
        if e['type']=='object':
            typed(e['aggregate'],{'aggregate'},e['id'])
            names=[a['name'] for a in e['attributes']]
            if len(names)!=len(set(names)): error('concept_references',f"{e['id']}: duplicate attribute")
            for a in e['attributes']:
                if a['type']=='enum' and not a.get('values'): error('schema',f"{e['id']}.{a['name']}: enum values required")
        if e['type']=='relation':
            left=typed(e['from'],{'object'},e['id']); right=typed(e['to'],{'object'},e['id'])
            if left and right and e['kind']=='composition' and left['aggregate']!=right['aggregate']:
                error('aggregate_encapsulation',f"{e['id']}: composition crosses aggregates")
        if e['type']=='aggregate':
            root_obj=typed(e['root'],{'object'},e['id'])
            if e['root'] in e['members'] or len(e['members'])!=len(set(e['members'])):
                error('aggregate_encapsulation',f"{e['id']}: repeated root/member")
            for oid in [e['root']]+e['members']:
                member=typed(oid,{'object'},e['id'])
                if member and member['aggregate']!=e['id']: error('aggregate_encapsulation',f'{oid}: ownership mismatch')
            for rid in e['invariants']:
                invariant=typed(rid,{'rule'},e['id'])
                if invariant:
                    if invariant['strength']!='normative': error('aggregate_encapsulation',f'{rid}: invariant must be normative')
                    for cid in invariant['applies_to']:
                        command=index.get(cid,{})
                        if command.get('aggregate')!=e['id']: error('aggregate_encapsulation',f'{rid}: invariant targets another aggregate')
            if root_obj and not root_obj['lifecycle']: error('state_closure',f"{e['root']}: aggregate root has no lifecycle")
        if e['type']=='command':
            aggregate=typed(e['aggregate'],{'aggregate'},e['id'])
            typed(e['root'],{'object'},e['id']); typed(e['role'],{'role'},e['id'])
            if aggregate and aggregate['root']!=e['root']: error('aggregate_encapsulation',f"{e['id']}: member cannot own command")
            role=index.get(e['role'],{})
            if e['id'] not in role.get('commands',[]): error('role_coverage',f"{e['id']}: role omits command")
            for eid in e['emits']:
                event=typed(eid,{'event'},e['id'])
                if event and event['produced_by']!=e['id']: error('references',f'{eid}: event producer mismatch')
            for path in e['preserves']: attribute_ref(path,e['id'])
        if e['type']=='event':
            command=typed(e['produced_by'],{'command'},e['id'])
            if command and e['id'] not in command['emits']: error('references',f"{e['id']}: event not emitted by producer")
        if e['type']=='role':
            for cid in e['commands']:
                command=typed(cid,{'command'},e['id'])
                if command and command['role']!=e['id']: error('role_coverage',f"{e['id']}: wrong command actor")
        if e['type']=='rule':
            if not e['refs']: error('rule_completeness',f"{e['id']}: rule lacks source")
            for target in e['applies_to']: typed(target,{'command','object'},e['id'])
            for t in terms(e['condition']): attribute_ref(t['concept']+'.'+t['attribute'],e['id'])
            def check_arity(node):
                if 'op' not in node:return
                arity=len(node['args']); op=node['op']
                if (op in {'not','is_null'} and arity!=1) or (op in {'eq','ne','gt'} and arity!=2):
                    error('concept_references',f"{e['id']}: invalid operator arity")
                for child in node['args']: check_arity(child)
            check_arity(e['condition'])
            if e['action']=='escalate' and not any(h['type']=='human_decision_point' and h['at']==e['id'] for h in elements):
                error('rule_completeness',f"{e['id']}: escalation lacks a human decision point")
        if e['type']=='human_decision_point':
            typed(e['at'],{'command','rule'},e['id'])
            if index.get(e['owner'],{}).get('kind')!='human': error('rule_completeness',f"{e['id']}: decision owner must be human")
        if e['type']=='policy':
            typed(e['on'],{'event'},e['id']);typed(e['then'],{'command'},e['id'])
        if e['type']=='metric':
            typed(e['measures'],{'object','event'},e['id']);typed(e['goal'],{'goal'},e['id'])
            for value in e['inputs']: attribute_ref(value,e['id'])
            if e['baseline'] is None: result['warnings'].append(f"{e['id']}: baseline pending; not stage-0 accepted")
        if e['type']=='mapping': typed(e['element'],{'object','command'},e['id'])

    for o in [e for e in elements if e['type']=='object']:
        aggregate=index.get(o['aggregate'],{})
        if o['id'] not in [aggregate.get('root')]+aggregate.get('members',[]):
            error('aggregate_encapsulation',f"{o['id']}: not owned by declared aggregate")
        life=o['lifecycle']
        if not life: continue
        states=set(life['states'])
        if 'labels' in life:
            values=[label['value'] for label in life['labels']]
            if set(values)!=states or len(values)!=len(set(values)) or any(not label['name'].strip() for label in life['labels']):
                error('state_closure',f"{o['id']}: lifecycle labels must name each state exactly once")
        if len(states)!=len(life['states']) or life['initial'] not in states:
            error('state_closure',f"{o['id']}: invalid initial/duplicate state")
        actual_transitions=set()
        for t in life['transitions']:
            if t['to'] not in states or (t['from'] is not None and t['from'] not in states):
                error('state_closure',f"{o['id']}: transition outside states")
            typed(t['by'],{'command'},o['id'])
            key=(t['from'],t['to'],t['by'])
            if key in actual_transitions:error('state_closure',f"{o['id']}: duplicate transition")
            actual_transitions.add(key)
        expected=set()
        for c in [e for e in elements if e['type']=='command' and e['root']==o['id']]:
            if c['transition']['creates']:
                if c['allowed_in']: error('state_closure',f"{c['id']}: creation cannot have an existing pre-state")
                starts=[None]
            else:
                starts=c['allowed_in']
                if not starts or not set(starts)<=states:error('state_closure',f"{c['id']}: invalid pre-states")
            for start in starts:
                target=start if c['transition']['to']=='same' else c['transition']['to']
                expected.add((start,target,c['id']))
                if c['transition']['creates'] and target!=life['initial']:
                    error('state_closure',f"{c['id']}: creation must enter initial state")
        if actual_transitions!=expected:error('state_closure',f"{o['id']}: lifecycle and commands differ")
        reached={life['initial']}; queue=deque(reached)
        while queue:
            source=queue.popleft()
            for start,target,_ in actual_transitions:
                if start==source and target not in reached: reached.add(target);queue.append(target)
        if states-reached:error('state_closure',f"{o['id']}: unreachable states {sorted(states-reached)}")

    if phase>=4:
        mapped={e['element'] for e in elements if e['type']=='mapping'}
        missing=[e['id'] for e in elements if e['type'] in {'object','command'} and e['id'] not in mapped]
        if missing:error('mapping_coverage',f'{len(missing)} objects/commands have no implementation mapping')
    else: result['checks']['mapping_coverage']='deferred_until_phase_4'
    if release:
        if any(e['status']!='active' for e in elements):error('release','Draft elements cannot be released')
        if any(e['type']=='metric' and (e['baseline'] is None or e['measurement_status']!='measured') for e in elements):
            error('release','Metric baselines/review are incomplete')
        for gate in ('stage_0','stage_1','stage_2'):
            if manifest['stage_gates'].get(gate)!='passed': error('release',f'{gate} has not passed')
        if not (root/'.git').exists():error('release','No Git repository/history; model is not merged or released')
    for check in CHECKS:
        if result['checks'][check]=='not_run':result['checks'][check]='failed' if any(e.startswith(check+':') for e in errors) else 'passed'
    if any(e['status']=='draft' for e in elements):result['warnings'].append('Source contains review drafts; structural validity is not business approval or runtime validation')
    result['warnings'].extend(manifest.get('pending',[]))
    return result


UNKNOWN=object()


def evaluate(condition, facts):
    """Return True/False/UNKNOWN. Missing or incomparable input never means pass."""
    if 'literal' in condition:return condition['literal']
    if 'concept' in condition:return facts.get(condition['concept'],{}).get(condition['attribute'],UNKNOWN)
    op=condition['op']; values=[evaluate(a,facts) for a in condition['args']]
    if op=='all':
        if any(v is False for v in values):return False
        return UNKNOWN if any(v is UNKNOWN for v in values) else all(values)
    if op=='any':
        if any(v is True for v in values):return True
        return UNKNOWN if any(v is UNKNOWN for v in values) else any(values)
    if any(v is UNKNOWN for v in values):return UNKNOWN
    if op=='not':return not values[0]
    if op=='is_null':return values[0] is None
    if op=='eq':return type(values[0]) is type(values[1]) and values[0]==values[1]
    if op=='ne':return not (type(values[0]) is type(values[1]) and values[0]==values[1])
    if op=='gt':
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) for v in values):return UNKNOWN
        return values[0]>values[1]
    raise ValueError(f'Unsupported condition operator: {op}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',type=int,choices=[2,4],default=2)
    parser.add_argument('--release',action='store_true')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    try:
        manifest,schema,docs=load_model()
        result=validate(ROOT,manifest,schema,docs,args.phase,args.release)
    except (ValueError,KeyError,OSError,yaml.YAMLError) as exc:
        result={'errors':[str(exc)],'warnings':[],'checks':{}}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f"Model {result.get('version','unloaded')}: {sum(result.get('counts',{}).values())} elements; {len(result['errors'])} errors")
    for check,status in result['checks'].items():print(f'  {check}: {status}')
    for err in result['errors']:print('ERROR:',err)
    for warning in result['warnings']:print('NOTE:',warning)
    return 1 if result['errors'] else 0


if __name__=='__main__':raise SystemExit(main())

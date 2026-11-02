#!/usr/bin/env python3
"""Generate the read-only, self-contained model explorer from validated sources."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html as html_lib
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/checks'))
from validate_model import load_model, terms, validate, yaml

TEMPLATE=Path('tools/generator/templates/model-explorer.html.tpl')
OUTPUT=Path('generated/ps-model-explorer.html')
ALIASES=(Path('generated/ps-model.html'),)


def digest_files(root, paths):
    digest=hashlib.sha256()
    for relative in sorted(set(map(str,paths))):
        digest.update(relative.encode());digest.update(b'\0')
        digest.update((root/relative).read_bytes());digest.update(b'\0')
    return digest.hexdigest()


def build_payload(root=ROOT):
    manifest,schema,docs=load_model(root)
    report=validate(root,manifest,schema,docs)
    if report['errors']:raise ValueError('Model validation failed:\n'+'\n'.join(report['errors']))
    elements=[]
    for relative,doc in docs:
        lines={}
        for number,line in enumerate((root/relative).read_text().splitlines(),1):
            match=re.match(r'^- id: (\S+)$',line)
            if match:lines[match[1]]=number
        for original in doc['elements']:
            element=copy.deepcopy(original)
            element['_source']={'path':relative,'line':lines.get(element['id'])}
            elements.append(element)
    index={e['id']:e for e in elements}
    edges=[]

    def derived(element,field,target,label,extra=None):
        if target not in index:raise ValueError(f'Missing projection target: {target}')
        key=f"derived:{element['id']}:{field}:{target}"
        edges.append(dict(id=key,source=element['id'],target=target,label=label,
                          projection='field_reference',element_ref=element['id'],field=field,
                          details=extra or {}))

    for e in elements:
        kind=e['type']
        if kind=='relation':
            edges.append(dict(id=e['id'],source=e['from'],target=e['to'],label=e['name'],
                              projection='explicit_relation',element_ref=e['id'],field=None,
                              details={'kind':e['kind'],'semantic':e['semantic'],'cardinality':e['cardinality']}))
        if kind=='aggregate':
            derived(e,'root',e['root'],'根对象')
            for member in e['members']:derived(e,'members',member,'成员对象')
            for invariant in e['invariants']:derived(e,'invariants',invariant,'不变量')
        if kind=='command':
            for field,label in [('aggregate','属于聚合'),('root','作用于根对象'),('role','执行角色')]:
                derived(e,field,e[field],label)
            for event in e['emits']:derived(e,'emits',event,'产生事件')
        if kind=='rule':
            for target in e['applies_to']:derived(e,'applies_to',target,'作用于')
            concepts={}
            for term in terms(e['condition']):concepts.setdefault(term['concept'],set()).add(term['attribute'])
            for target,attributes in concepts.items():
                derived(e,'condition',target,'条件引用',{'attributes':sorted(attributes)})
        if kind=='human_decision_point':derived(e,'at',e['at'],'介入位置')
        if kind=='event':derived(e,'produced_by',e['produced_by'],'由命令产生')
        if kind=='metric':
            derived(e,'goal',e['goal'],'衡量目标');derived(e,'measures',e['measures'],'统计对象')
        if kind=='policy':
            derived(e,'on',e['on'],'触发事件');derived(e,'then',e['then'],'目标命令')
        if kind=='mapping':derived(e,'element',e['element'],'实现对应')

    types=[]
    for key,spec in schema['$defs'].items():
        if 'type' not in spec.get('properties',{}):continue
        types.append(dict(id='meta:'+key,type=key,name=spec.get('title',key),
                          schema=spec,source={'path':manifest['schema'],'pointer':'/$defs/'+key}))
    lifecycles=[]
    for e in elements:
        if e['type']!='object' or not e.get('lifecycle'):continue
        life=e['lifecycle'];labels={x['value']:x['name'] for x in life.get('labels',[])}
        nodes=[dict(id='state:'+e['id']+':'+s,name=labels.get(s,s),value=s,object=e['id'],
                    type='state_projection',initial=s==life['initial']) for s in life['states']]
        has_creation=any(t['from'] is None for t in life['transitions'])
        if has_creation:
            nodes.insert(0,dict(id='state:'+e['id']+':__creation',name='创建起点',value=None,
                               object=e['id'],type='creation_projection',initial=False))
        transitions=[]
        for i,t in enumerate(life['transitions']):
            transitions.append(dict(id=f"transition:{e['id']}:{i}",
              source='state:'+e['id']+':'+(t['from'] if t['from'] is not None else '__creation'),
              target='state:'+e['id']+':'+t['to'],label=index[t['by']]['name'],
              command=t['by'],object=e['id'],projection='state_transition',field=f'lifecycle.transitions[{i}]'))
        lifecycles.append(dict(object=e['id'],name=e['name'],nodes=nodes,edges=transitions))
    source_hash=digest_files(root,['model/model.yaml',manifest['schema'],*manifest['files']])
    generator_hash=digest_files(root,['tools/generator/render_model.py',TEMPLATE])
    return dict(meta=dict(version=manifest['version'],status=manifest['status'],
                         source_hash=source_hash,generator_hash=generator_hash,
                         context=manifest['context'],stage_gates=manifest['stage_gates'],
                         pending=manifest['pending'],empty_sections=manifest['empty_sections'],
                         validation=report['checks']),
                elements=elements,edges=edges,types=types,lifecycles=lifecycles)


def first_paint(payload):
    """Generate real first-paint markup. JS enhances it after successful boot."""
    escape=lambda value:html_lib.escape(str(value),quote=True)
    elements=payload['elements']; index={e['id']:e for e in elements}
    objects=[dict(e) for e in elements if e['type']=='object']
    by_id={e['id']:e for e in objects};types={t['type']:t['name'] for t in payload['types']}
    aggregates=[e for e in elements if e['type']=='aggregate']
    if len(aggregates)==3:aggregates=[aggregates[1],aggregates[0],aggregates[2]]
    nodes=[];groups=[]
    for col,aggregate in enumerate(aggregates):
        groups.append(f'<text x="{40+col*310}" y="25" class="group-label">{escape(aggregate["name"])}</text>')
        for row,id in enumerate([aggregate['root'],*aggregate['members']]):
            if id in by_id:
                node=dict(by_id[id],x=160+col*310,y=95+row*112);by_id[id]=node;nodes.append(node)
    selected=objects[0]
    explicit=[e for e in payload['edges'] if e['projection']=='explicit_relation']
    markup=list(groups)
    for edge in explicit:
        a=by_id[edge['source']];b=by_id[edge['target']]
        dx=b['x']-a['x'];dy=b['y']-a['y']
        t=1/max(abs(dx)/115,abs(dy)/38)
        start=(a['x']+dx*t,a['y']+dy*t);end=(b['x']-dx*t,b['y']-dy*t)
        active=selected['id'] in (edge['source'],edge['target'])
        markup.append(f'<g class="edge{" active" if active else ""}" data-edge-id="{escape(edge["id"])}"><path class="line" d="M {start[0]:.2f} {start[1]:.2f} L {end[0]:.2f} {end[1]:.2f}"></path><title>{escape(edge["label"])}</title></g>')
    for node in nodes:
        name=node['name'];lines=[name[:12],name[12:]] if len(name)>12 else [name]
        texts=''.join(f'<text x="0" y="{14 if len(lines)==1 else 8+i*22}" text-anchor="middle" class="node-name">{escape(line)}</text>' for i,line in enumerate(lines))
        markup.append(f'<g class="node{" selected" if node["id"]==selected["id"] else ""}" data-node-id="{escape(node["id"])}" transform="translate({node["x"]},{node["y"]})"><rect x="-115" y="-38" width="230" height="76"></rect><text x="0" y="-16" text-anchor="middle" class="node-caption">{escape(types.get(node["type"],node["type"]))}</text>{texts}<title>{escape(node["id"])}</title></g>')
    x1=min(n['x'] for n in nodes)-160;y1=min(n['y'] for n in nodes)-75
    x2=max(n['x'] for n in nodes)+160;y2=max(n['y'] for n in nodes)+85
    inspector=f'<span class="badge">{escape(types[selected["type"]])}</span><h2>{escape(selected["name"])}</h2><div class="element-id">{escape(selected["id"])}</div>'
    inspector+='<p>模型源数据已载入页面；交互启动后可点击其他节点或边查看详情。</p><section class="detail-section"><h3>内部属性</h3>'
    for attribute in selected.get('attributes',[]):
        inspector+=f'<div class="attr"><strong>{escape(attribute["name"])}</strong><p>{escape(attribute["meaning"])}</p><small>{escape(attribute["type"])}</small></div>'
    source=selected['_source']['path']
    inspector+='</section><section class="detail-section"><h3>模型来源</h3>'
    inspector+=f'<a class="source-link" href="../{quote(source)}">{escape(source)}</a></section>'
    counts=''.join(f'<span><strong>{value}</strong><small>{name}</small></span>' for name,value in [
        ('模型元素',len(elements)),('业务对象',len(objects)),('显式关系',len(explicit)),('业务规则',sum(e['type']=='rule' for e in elements))])
    stamp=f'<div>{escape(payload["meta"]["version"])}</div><div>源指纹 {payload["meta"]["source_hash"][:12]}</div><div>展示指纹 {payload["meta"]["generator_hash"][:12]}</div>'
    return {'INITIAL_GRAPH':''.join(markup),'INITIAL_VIEWBOX':f'{x1} {y1} {x2-x1} {y2-y1}',
            'INITIAL_INSPECTOR':inspector,'INITIAL_COUNTS':counts,'INITIAL_STAMP':stamp,
            'INITIAL_VIEW_COUNT':f'{len(objects)} 点 / {len(explicit)} 边'}


def render(root=ROOT):
    payload=build_payload(root)
    template=(root/TEMPLATE).read_text()
    values=first_paint(payload)
    values['MODEL_PAYLOAD']=None
    for key in values:
        if template.count('@@'+key+'@@')!=1:raise ValueError(f'Template requires exactly one {key} slot')
    encoded=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
    encoded=encoded.replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    values['MODEL_PAYLOAD']=encoded
    for key,value in values.items():template=template.replace('@@'+key+'@@',value)
    unresolved=re.findall(r'@@[A-Z][A-Z_0-9]*@@',template)
    if unresolved:raise ValueError(f'Unexpanded template placeholders: {sorted(set(unresolved))}')
    match=re.search(r'<script id="model-data" type="application/json">(.*?)</script>',template,re.S)
    if not match:raise ValueError('Generated HTML is missing the model payload script')
    try:embedded=json.loads(match.group(1))
    except json.JSONDecodeError as exc:raise ValueError(f'Generated HTML payload is invalid JSON: {exc}') from exc
    if embedded!=payload:raise ValueError('Generated HTML payload differs from the validated model data')
    return template


def write_or_check(root=ROOT,check=False):
    html=render(root)
    if check:
        for relative in (OUTPUT,*ALIASES):
            output=root/relative
            if not output.exists() or output.read_text()!=html:
                raise ValueError(f'{relative}: HTML is missing/stale/edited. Change model or template, then regenerate.')
        print('Generated HTML is synchronized with model and generator sources.')
    else:
        for relative in (OUTPUT,*ALIASES):
            output=root/relative
            output.parent.mkdir(parents=True,exist_ok=True);output.write_text(html)
        print(f'Generated {OUTPUT} ({len(html.encode()):,} bytes)')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Fail if generated HTML differs from current sources')
    parser.add_argument('--watch',action='store_true',help='Regenerate when model/schema/template changes; refresh the browser afterward')
    args=parser.parse_args()
    if args.check and args.watch:parser.error('--check and --watch cannot be combined')
    if args.watch:
        last=None
        try:
            while True:
                try:
                    html=render();signature=hashlib.sha256(html.encode()).hexdigest()
                    if signature!=last:
                        for relative in (OUTPUT,*ALIASES):
                            (ROOT/relative).parent.mkdir(parents=True,exist_ok=True)
                            (ROOT/relative).write_text(html)
                        last=signature
                        print(f'Updated {OUTPUT}; refresh the browser.',flush=True)
                except (ValueError,OSError,KeyError,yaml.YAMLError) as exc:
                    message=str(exc)
                    if message!=last:print('Not regenerated:',message,flush=True);last=message
                time.sleep(0.8)
        except KeyboardInterrupt:return 0
    else:
        try:write_or_check(check=args.check)
        except (ValueError,OSError,KeyError,yaml.YAMLError) as exc:print(str(exc),file=sys.stderr);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Check the model Q&A evaluation set and report how much of it the model can support.

Static check only: it confirms each question names existing model evidence or a
declared gap. It does not run an agent or judge any answer.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

from validate_model import ROOT, load_model, read_yaml

DEFAULT=ROOT/'evals/model-qa/questions.yaml'
EXPECTED={'answer','decline_runtime','decline_action','out_of_scope','model_gap'}
REQUIRED=['id','category','question','expected','key_points','must_not','evidence','source']


def check(path=DEFAULT, root=ROOT):
    _,_,docs=load_model(root)
    index={e['id']:e for _,doc in docs for e in doc['elements']}
    data=read_yaml(path)
    errors=[]; supported=[]; gaps=[]
    ids=[q.get('id') for q in data['questions']]
    for duplicate in [i for i,n in Counter(ids).items() if n>1]:errors.append(f'{duplicate}: duplicate id')
    for q in data['questions']:
        where=q.get('id','?')
        missing=[k for k in REQUIRED if k not in q]
        if missing:errors.append(f'{where}: missing {missing}');continue
        if q['expected'] not in EXPECTED:errors.append(f"{where}: unknown expected {q['expected']}")
        if not q['key_points']:errors.append(f'{where}: key_points required')
        if not (root/q['source']).is_file():errors.append(f"{where}: missing source {q['source']}")
        for ref in q['evidence']:
            if ref not in index:errors.append(f'{where}: unknown model element {ref}')
            elif index[ref]['status']=='deprecated':errors.append(f'{where}: deprecated model element {ref}')
        if q['expected']=='model_gap' and not q.get('known_gap'):errors.append(f'{where}: model_gap needs known_gap')
        if q.get('known_gap'):gaps.append(where)
        elif not q['evidence']:errors.append(f'{where}: evidence required unless known_gap is declared')
        else:supported.append(where)
    return dict(total=len(data['questions']),supported=supported,gaps=gaps,errors=errors,
                categories=dict(Counter(q.get('category') for q in data['questions'])))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',nargs='?',type=Path,default=DEFAULT)
    args=parser.parse_args()
    result=check(args.path)
    rate=len(result['supported'])/result['total'] if result['total'] else 0
    print(f"Questions: {result['total']}  categories: {result['categories']}")
    print(f"Model-supported: {len(result['supported'])}/{result['total']} = {rate:.1%}")
    if result['gaps']:print('Declared model gaps:',', '.join(result['gaps']))
    for error in result['errors']:print('ERROR:',error)
    return 1 if result['errors'] else 0


if __name__=='__main__':sys.exit(main())

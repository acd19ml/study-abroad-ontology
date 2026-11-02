#!/usr/bin/env python3
"""Synchronize only marked model-ID backlinks in referenced Markdown documents."""
import argparse
from collections import defaultdict
import re
from urllib.parse import unquote

from validate_model import ROOT, load_model

START='<!-- MODEL-REFS:START -->'
END='<!-- MODEL-REFS:END -->'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Write the marked backlink block; default only checks')
    args=parser.parse_args()
    _,_,docs=load_model()
    backlinks=defaultdict(set)
    for _,doc in docs:
        for e in doc['elements']:
            for source in e['refs']:
                p=(ROOT/unquote(source.split('#')[0])).resolve()
                if p.suffix!='.md' or not p.is_relative_to((ROOT/'docs').resolve()):
                    raise ValueError(f'Only referenced docs/*.md may be updated: {source}')
                backlinks[p].add(e['id'])
    changed=[]
    for p,ids in sorted(backlinks.items()):
        original=p.read_text()
        block=START+'\n## 模型关联索引\n\n此段由 `tools/checks/sync_model_refs.py` 根据模型源的 `refs` 同步，仅用于双向定位。\n\n'
        block+='\n'.join('- `'+i+'`' for i in sorted(ids))+'\n'+END
        if START in original:
            if END not in original:raise ValueError(f'Unclosed model backlink marker: {p}')
            updated=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:block,original,flags=re.S)
        else:updated=original.rstrip()+'\n\n'+block+'\n'
        if updated!=original:
            changed.append(str(p.relative_to(ROOT)))
            if args.write:p.write_text(updated)
    print(('Updated' if args.write else 'Outdated')+f' model backlink blocks: {len(changed)}')
    for path in changed:print(' ',path)
    return 0 if args.write or not changed else 1


if __name__=='__main__':raise SystemExit(main())

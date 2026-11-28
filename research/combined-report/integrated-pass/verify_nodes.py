import re, json, sys
sys.path.insert(0, '.')
from nodes import N
def norm(s):
    s = s.replace('**', '').replace('`', '').replace('*', '')
    s = s.replace('\u202f', ' ').replace('\u00a0', ' ')
    return re.sub(r'\s+', ' ', s)
cache = {}
bad = []
for nd in N:
    txt = ''
    for p in nd['src'].split('|'):
        if p not in cache: cache[p] = norm(open(p, encoding='utf-8').read())
        txt += cache[p]
    for v in nd['vals']:
        if norm(v) not in txt: bad.append((nd['id'], v))
print(len(N), 'nodes;', len(bad), 'unverified')
for b in bad: print(' ', b)
# numeric guard on page text: every number token in text must occur in its sources
num = re.compile(r'(?<![\w.])[−-]?\d+(?:,\d{3})*(?:\.\d+)?')
miss = []
for nd in N:
    txt = ''.join(cache[p] for p in nd['src'].split('|'))
    for tok in num.findall(nd['text']):
        t = tok.replace('−', '').replace('-', '')
        if t not in txt: miss.append((nd['id'], tok))
print(len(miss), 'text numbers not found in source')
for m in miss: print(' ', m)

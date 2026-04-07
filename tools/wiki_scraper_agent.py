#!/usr/bin/env python3
'''5QLN wiki builder -- L1/D1/C1 aligned.'''
import sys, os, json, re, hashlib
from pathlib import Path
from datetime import datetime as dt

# PATHS
WD   = Path('/home/workspace/5qln-wiki')
WIKI = WD / 'wiki'
WRAW = WD / 'raw' / 'documents'
WLOG = WIKI / 'log.md'
WCON = WIKI / 'concepts'
WSRC = WIKI / 'sources'
PRC  = WRAW / '.processed.json'
SKP  = WRAW / '.skip.json'
DB   = Path('/home/workspace/Datasets/5qln-com/data.duckdb')

# STATE
def lset(p): return set(json.loads(p.read_text())) if p.exists() else set()
def sset(p,s): p.write_text(json.dumps(sorted(s),ensure_ascii=False),encoding='utf-8')
PROCESSED = lset(PRC)
SKIP      = lset(SKP)
def mark_done(u): PROCESSED.update(u); sset(PRC, PROCESSED)
def mark_skp(u):  SKIP.update(u);     sset(SKP,  SKIP)

# UTILS
def parse_fm(c):
    fm={}
    if c.startswith('---'):
        e=c.find('---',3)
        if e!=-1:
            for ln in c[3:e].strip().split('\n'):
                if ':' in ln: k,v=ln.split(':',1); fm[k.strip()]=v.strip()
    return fm

def strip_fm(c): return re.sub(r'^---.*?---\n','',c,flags=re.DOTALL)

def title(c):
    m=re.search(r'^#\s+(.+)$',c,re.MULTILINE)
    return m.group(1).strip() if m else 'untitled'

def slug(url):
    h=hashlib.md5(url.encode()).hexdigest()[:8]
    p=url.replace('https://www.5qln.com/','').replace('https://5qln.com/','').strip('/').replace('/','_')or'home'
    p=''.join(c if c.isalnum() or c in '-_' else '_' for c in p)[:60]
    return f'{p}_{h}'

def load_pages():
    pages={}
    for md in WIKI.rglob('*.md'):
        co=md.read_text(encoding='utf-8'); fm=parse_fm(co)
        pages[md.stem]={'title':title(co),'phase':fm.get('phase',''),'type':fm.get('type','')}
    return pages
WIKI_PAGES=load_pages()

# ALPHAS (L1)
ALPHAS={
 'infinite-zero':'Infinity-Zero -- Fertile stillness Not-Knowing',
 'authentic-question':'Authentic-Question -- Question arising from Infinity-Zero',
 'core-essence':'Core-Essence -- Unchanging identity at center of growth',
 'self-similar-expressions':'Self-Similar-Expressions -- Fractal manifestations of Core-Essence',
 'self-nature':'Self-Nature -- What inquirer authentically brings',
 'universal-potential':'Universal-Potential -- Larger context cosmic field',
 'natural-intersection':'Natural-Intersection -- Click where Self-Nature meets Universal-Potential',
 'natural-gradient':'Natural-Gradient -- Path of least resistance',
 'local-actualization':'Local-Actualization -- Tangible immediate result',
 'global-propagation':'Global-Propagation -- What propagates beyond the local',
 'fractal-seed':'Fractal-Seed -- Artifact carrying Core-Essence faithfully',
 'enriched-return':'Enriched-Return -- Return to Infinity-Zero carrying the question',
 'mirror-truth':'Mirror-Truth -- Human=Infinity-Zero | AI=Known',
 'corruption-patterns':'Corruption-Patterns -- L1 L2 L3 L4 and V-deletion failure modes',
 'sacred-asymmetry':'Sacred-Asymmetry -- The membrane ontological difference',
}

# PHASES
CONST=(
 '> **H = Infinity-Zero | A = Known** -- Human rests in Not-Knowing; AI operates in the Known.\n'
 '> **S -> G -> Q -> P -> V** -- The five-phase constitutional cycle.\n'
 '> **No V without Infinity-Zero-prime** -- Every cycle returns carrying a new question.'
)

def phase_s(raw,url,title):
    sents=re.split(r'[.\n]+',raw)
    qs=[x.strip() for x in sents if '?' in x and len(x.strip())>15]
    x=qs[0] if qs else (title or 'What is the essence of this?')
    kws=re.findall(r'\b[A-Z][a-z]{3,}\b',raw)
    tags=list(dict.fromkeys(t for t in kws))[:12]
    return{'x':x[:200],'url':url,'title':title,'tags':tags,'sents':sents,'raw':raw}

def phase_g(s,pgs):
    url,title,raw=s['url'],s['title'],s['raw']
    tl=raw.lower()
    matched=alpha_val=None
    for k,v in ALPHAS.items():
        kw=k.replace('-',' ')
        if kw in tl or k in tl.replace(' ',''):
            if not matched: matched=k; alpha_val=v
    if not alpha_val:
        for k,v in ALPHAS.items():
            if any(w in tl for w in k.split('-')[:2]):
                if not matched: matched=k; alpha_val=v; break
    if not alpha_val:
        matched='unknown-pattern'; alpha_val=f'Pattern from {title[:40]}'
    ph=next((v for k,v in {'start':'S','growth':'G','quality':'Q','power':'P','value':'V'}.items() if k in url.lower()),'G')
    echoes=[(x.strip()[:120],'self-similar') for x in s['sents'] if len(x.strip())>40][:4]
    return{'alpha':alpha_val,'y':f'5QLN {matched.replace("-"," ")}','echoes':echoes,'phase':ph,'mk':matched}

def phase_q(s,g):
    res=len(g['echoes'])*2+(3 if g['mk']!='unknown-pattern' else 0)
    return{'phase':g['phase'],'z':f'Phase-{g["phase"]} resonance with {g["alpha"][:30]}','res':res}

def phase_p(s,g,q):
    eng=len(s.get('raw',''))
    return{'grad':'high' if eng>2000 else 'medium','a':f"Flow at {q['phase']}-phase"}

def phase_v(s,g,q,p):
    global WIKI_PAGES
    res=q['res']; ph=q['phase']; url=s['url']; title=s['title']; raw=s['raw']
    sk=slug(url); fm=parse_fm(raw); matched=g['mk']; echoes=g['echoes']; z=q['z']; x=s['x']
    skips=['/tag/','/category/','/author/','facebook','twitter','youtube','instagram','linkedin']
    if any(sk in url for sk in skips): return{'page_type':'skip','nav':'skip'},'skip'
    pt='concept' if (res>=5 or matched) and matched!='unknown-pattern' else 'source'
    if matched and matched!='unknown-pattern' and res>=5: pt='concept'
    elif ph in 'SGQPV': pt='source'
    else: pt='source'
    nav=f'{pt} | {g["y"][:50]}'

    if pt=='concept':
        wl=(f'\n\nSee also: [[five-phase-cycle]], [[mirror-truth]], [[{matched}]]' if matched!='unknown-pattern' else '')
        out=WCON/(sk+'.md')
        body=(f'---\ntitle: {g["y"]}\ntype: concept\nphase: {fm.get("phase",ph)}\n'
              f'tags: [{matched or "5qln"}]\nsources: [raw/documents/{sk}.md]\n'
              f'created: {dt.now().strftime("%Y-%m-%d")}\nupdated: {dt.now().strftime("%Y-%m-%d")}\n---\n'
              f'# {g["y"]}\n\n{CONST}\n\n## Core Essence\n\n**alpha:** {g["alpha"]}\n\n'
              f'## Validated Spark\n\n> {x}\n\n## Key Properties\n\n'
              f'- **Phase:** {ph.upper()} -- {z}\n- **Natural intersection:** {g["alpha"]}{wl}\n\n## Notes\n\n{strip_fm(raw)[:2000]}\n\n**Source:** [{url}]({url})\n')
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(body,encoding='utf-8')
        la=f'concept | {g["y"]} -- phase-{ph} {len(echoes)} echoes'
    else:
        out=WSRC/(sk+'.md')
        body=(f'---\ntitle: "{title.replace(chr(34),chr(92)+chr(34))}"\ntype: source\n'
              f'phase: {fm.get("phase",ph)}\nsource: {url}\n'
              f'created: {dt.now().strftime("%Y-%m-%d")}\nupdated: {dt.now().strftime("%Y-%m-%d")}\n---\n'
              f'# {title}\n\n{CONST}\n\n{strip_fm(raw)[:3000]}\n\n**Source:** [{url}]({url})\n')
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(body,encoding='utf-8')
        la=f'source | {title[:50]} -- phase-{ph}'
    log=(
     f'\n## [{dt.now().strftime("%Y-%m-%d")}] auto | {la}\n'
     f'- Source: [{url}]({url})\n- Phase: {ph} | Alpha: {g["alpha"][:60]}\n'
     f'- Echoes: {len(echoes)}\n- Action: {la}\n'
    )
    if WLOG.exists(): existing=WLOG.read_text(encoding='utf-8')
    else: existing='# 5QLN Wiki -- Log\n\n> Chronological, append-only record.\n\n'
    WLOG.write_text(existing+log,encoding='utf-8')
    mark_done([url])
    return out,la

def main():
    global WIKI_PAGES
    import argparse,duckdb
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int,default=20)
    parser.add_argument('--full-run',action='store_true')
    a=parser.parse_args()
    limit=9999 if a.full_run else a.limit
    try:
        con=duckdb.connect(str(DB),read_only=True)
        rows=con.execute("SELECT url, title, content FROM pages WHERE content IS NOT NULL AND length(content)>500 AND url NOT LIKE '%/tag/%' AND url NOT LIKE '%/category/%' AND url NOT LIKE '%facebook%' AND url NOT LIKE '%twitter%' AND url NOT LIKE '%youtube%' ORDER BY depth ASC, length(content) DESC").fetchall()
        con.close()
    except Exception as e:
        print(f'DuckDB: {e}'); rows=[(r.stem,r.stem,r.read_text(encoding='utf-8')) for r in WRAW.glob('*.md')]
    pending=[(u,t,c) for u,t,c in rows if u not in PROCESSED and u not in SKIP][:limit]
    print(f'\n5QLN Wiki -- {len(pending)} pages\n')
    print(f"{'URL':<55} {'TYPE':<10} {'PHASE':<6} {'ALPHA'}")
    print('-'*120)
    results=[]
    for url,title,raw in pending:
        try:
            s=phase_s(raw,url,title); g=phase_g(s,WIKI_PAGES)
            q=phase_q(s,g); pv=phase_p(s,g,q); v,la=phase_v(s,g,q,pv)
            pt=v['page_type'] if isinstance(v,dict) else 'source'; ph=q['phase']
            print(f'{url:<55} {pt:<10} {ph:<6} {g["alpha"][:50]}')
            results.append({'url':url,'type':pt,'phase':ph,'action':la,'artifact':str(v)})
            WIKI_PAGES=load_pages()
        except Exception as e:
            print(f'ERROR {url}: {e}')
    done=[r for r in results if r['type']!='skip']
    print(f'\nProcessed: {len(results)} | Created: {len(done)}')
    Path('/tmp/wiki_agent_summary.json').write_text(json.dumps({'ts':dt.now().isoformat(),'done':len(done),'results':results},indent=2))
    print('Summary: /tmp/wiki_agent_summary.json')

if __name__=='__main__': main()

"""Local lexical retrieval and exact source windows; no embeddings or model calls.

Windows never combine resources/security scopes. Offsets count Python Unicode
characters, and the ID identifies a canonical window of one immutable version.
"""
import re
import math
from collections import Counter

STOP = set('what which the a an of is are was were to in on and or from with can we i me you your my do does it for all today latest current including caused use show details just'.split())
# Small, explicit lexical aliases, not a claim of general semantic retrieval.
ALIASES = {'outage': 'incident', 'outages': 'incident', 'incidents': 'incident',
           'retracted': 'withdrawn', 'retract': 'withdrawn',
           'remediation': 'fix', 'fixes': 'fix', 'runbooks': 'runbook'}
WHOLE_LIMIT = 4000
WINDOW = 2400
OVERLAP = 400


def tokens(text):
    words = set(re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', text.lower()))
    # Preserve exact compounds, and match ordinary words inside alphabetic
    # compounds. Numeric entity identifiers (PAY-103) remain intact.
    for word in list(words):
        parts = word.split('-')
        if len(parts) > 1 and all(part.isalpha() for part in parts):
            words.update(parts)
    return {ALIASES.get(t, t) for t in words if t not in STOP}



def ranking_terms(query_tokens, strategy='none'):
    """Optional lexical action vocabulary for ranking, never topic or access filtering."""
    if strategy not in ('none','action-terms-v1'):raise ValueError('Unsupported query expansion')
    result=set(query_tokens)
    if strategy=='action-terms-v1' and result & {'mitigation','mitigations'}:
        result.update({'procedure','workaround','safeguard','protective'})
    return result

def spans(text):
    if len(text) <= WHOLE_LIMIT:
        return [(0, len(text))]
    result = []
    start = 0
    while start < len(text):
        end = min(start + WINDOW, len(text))
        result.append((start, end))
        if end == len(text): break
        start = end - OVERLAP
    return result


def ranked_windows(resource, query_tokens, *, supplementary=False):
    """Return at most three matching windows; exact text, deterministic tie order."""
    text = resource['text']
    title_score = len(query_tokens & tokens(resource['title']))
    matches = []
    for start, end in spans(text):
        body_score = len(query_tokens & tokens(text[start:end]))
        if body_score or title_score:
            matches.append((body_score * 2 + title_score, start, end))
    if not matches and supplementary:
        matches = [(0, *spans(text)[0])]
    return sorted(matches, key=lambda item: (-item[0], item[1]))[:3]


def window_evidence(resource, start, end):
    text = resource['text']
    eid = resource['id'] + '@' + str(resource['version'])
    locator = dict(resource['locator'])
    if len(text) > WHOLE_LIMIT:
        eid += '#' + str(start) + ':' + str(end)
        locator['text_window'] = {'start': start, 'end': end, 'unit': 'unicode_characters',
                                  'strategy': 'fixed-2400-overlap-400-v1'}
    return eid, locator, text[start:end]


def resolve_window(resource, eid):
    """Reject forged/noncanonical slices and legacy aliases of long documents."""
    for start, end in spans(resource['text']):
        candidate, locator, text = window_evidence(resource, start, end)
        if candidate == eid: return locator, text
    raise ValueError('Invalid evidence window')


def bm25_windows(resources, query_tokens):
    """Local experimental BM25 over exact windows of prefiltered resources.

    No extra source/model calls and no edited citation text. Aliases/compound
    handling are identical to lexical baseline, isolating the scoring change.
    """
    documents=[]
    for resource in resources:
        for start,end in spans(resource['text']):
            terms=tokens(resource['title']) | tokens(resource['text'][start:end])
            documents.append((resource['id'],start,end,terms))
    count=len(documents)
    if not count:return {}
    frequencies=Counter(t for _,_,_,terms in documents for t in terms)
    average=sum(len(terms) for _,_,_,terms in documents)/count or 1
    result={r['id']:[] for r in resources}
    for rid,start,end,terms in documents:
        score=0.0
        for term in query_tokens & terms:
            # Binary TF preserves current set-tokenization; this experiment
            # changes inverse-document frequency and length normalization.
            idf=math.log(1+(count-frequencies[term]+0.5)/(frequencies[term]+0.5))
            score+=idf*2.2/(1+1.2*(0.25+0.75*len(terms)/average))
        if score:result[rid].append((score,start,end))
    return {rid:sorted(windows,key=lambda w:(-w[0],w[1]))[:3]
            for rid,windows in result.items()}

# Decision/state vocabulary alone does not establish a shared subject. This is
# query-relative local candidate relevance, never source access authorization.
SUBJECT_NEUTRAL=set('approved approval general customer customers code fix complete completion preventive progress remains work status owner done current latest release decision scope date confirmed which why how whether only no not beyond all any supports supported support'.split())


def subject_related(resources, query_tokens):
    """Require a topic match when a question names a subject.

    The engine may expand source-authored IDs only after authorizing each seed.
    No title/probe-name rules, rewritten text or model call.
    A question containing only generic state words retains the existing ranking.
    """
    anchors=query_tokens-SUBJECT_NEUTRAL
    if not anchors:return resources
    terms={r['id']:tokens(r['title'])|tokens(r['text']) for r in resources}
    direct={rid for rid,value in terms.items() if value&anchors}
    return [r for r in resources if r['id'] in direct]


def source_identifiers(resource):
    return {term for term in tokens(resource['title'])|tokens(resource['text'])
            if re.fullmatch(r'[a-z][a-z0-9]{1,15}-[0-9]+',term)}

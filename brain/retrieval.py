"""Local lexical retrieval and exact source windows; no embeddings or model calls.

Windows never combine resources/security scopes. Offsets count Python Unicode
characters, and the ID identifies a canonical window of one immutable version.
"""
import re

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

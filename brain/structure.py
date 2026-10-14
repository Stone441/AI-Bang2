"""Exact structural spans. No rewritten text, cross-resource merge or model IO."""
import re

HEADING = re.compile(r'^ {0,3}(#{1,6})\s+\S')
LIST = re.compile(r'^\s*(?:[-*+]\s|\d+[.)]\s)')
CONTINUATION = re.compile(r'^\s*(?:however\b|but\b|except\b|unless\b|only\b|provided\b|note\b|warning\b|do not\b|notwithstanding\b)', re.I)


def lines(text):
    offset=0
    for line in text.splitlines(keepends=True):
        yield offset,offset+len(line),line
        offset+=len(line)


def structural_spans(text, whole_limit=4000):
    """Short documents stay whole. Long documents use intact prose/record units.

    Tables and lists are indivisible even when large. A long unbroken paragraph
    remains intact; the existing evidence budget may reject it rather than clip
    away unknown qualifications. This is syntax-aware, not semantic parsing.
    """
    if len(text)<=whole_limit:return [(0,len(text))]
    rows=list(lines(text));result=[];start=None;kind=None;previous=''
    def flush(end):
        nonlocal start,kind,previous
        if start is not None and end>start:
            result.append((start,end))
        start=None;kind=None;previous=''
    for index,(a,b,line) in enumerate(rows):
        stripped=line.strip()
        heading=bool(HEADING.match(line))
        table='\t' in line or (stripped.startswith('|') and stripped.endswith('|'))
        listing=bool(LIST.match(line))
        if heading:
            if start is not None and kind!='heading':flush(a)
            if start is None:start=a
            kind='heading';previous=line;continue
        if not stripped:
            # Keep blank lines inside a table/list with the same next structure.
            following=next((r[2] for r in rows[index+1:] if r[2].strip()),'')
            following_collection=('\t' in following or following.strip().startswith('|') or bool(LIST.match(following)))
            same=((kind in ('table','list') and following and not HEADING.match(following))
                  or kind=='prose' and following_collection
                  or bool(CONTINUATION.match(following)))
            if start is not None and not same and kind!='heading':flush(b)
            continue
        new_kind='table' if table else 'list' if listing else 'prose'
        if start is None:start=a;kind=new_kind
        elif kind=='heading':kind=new_kind
        elif kind in ('table_note','list_note'):
            pass  # Keep the adjacent qualification paragraph intact.
        elif kind in ('table','list') and new_kind!=kind:
            kind += '_note'
        elif new_kind in ('table','list') and kind=='prose':
            kind=new_kind  # Keep the immediately preceding scope/introduction.
        elif (new_kind!=kind and not CONTINUATION.match(line)) or (
                kind=='prose' and re.search(r'[.!?。！？][\s]*$',previous)
                and not CONTINUATION.match(line)):
            flush(a);start=a;kind=new_kind
        previous=line
    flush(len(text))
    # Tiny standalone labels cannot satisfy the existing exact-quote contract.
    # Attach them to an adjacent contiguous block, without deleting bytes.
    merged=[]
    for a,b in result:
        if merged and (len(text[a:b].strip())<12 or len(text[merged[-1][0]:merged[-1][1]].strip())<12):
            merged[-1]=(merged[-1][0],b)
        else:merged.append((a,b))
    return merged or [(0,len(text))]


def section_context(text,start):
    """Source-authored heading ancestry with exact offsets, not invented facts."""
    stack=[]
    for a,b,line in lines(text):
        if a>start:break
        match=HEADING.match(line)
        if not match:continue
        level=len(match.group(1))
        stack=[item for item in stack if item['level']<level]
        stack.append({'level':level,'start':a,'end':b,'text':line})
    return stack


def quote_parts(text,limit=600):
    """Preserve every character while preferring complete lines and sentences."""
    result=[];start=0
    while len(text)-start>limit:
        upper=start+limit
        boundaries=[m.end() for m in re.finditer(r'\n|[.!?。！？](?:[ \t]+|$)',text[start:upper])
                    if m.end()>=12]
        if not boundaries:
            boundaries=[m.end() for m in re.finditer(r'\s+',text[start:upper]) if m.end()>=12]
        end=start+(boundaries[-1] if boundaries else limit)
        if len(text[end:].strip())<12:
            # Keep a small trailing qualifier intact in a balanced final pair.
            target=(len(text)-start)//2
            breaks=[m.end() for m in re.finditer(r'\s+',text[start:upper])
                    if 12<=m.end()<=limit and len(text[start+m.end():].strip())>=12]
            end=start+(min(breaks,key=lambda n:abs(n-target)) if breaks else target)
        result.append(text[start:end]);start=end
    if start<len(text):result.append(text[start:])
    if ''.join(result)!=text or any(len(p)>limit or len(p.strip())<12 for p in result):
        raise ValueError('Cannot construct bounded complete source quotes')
    return result

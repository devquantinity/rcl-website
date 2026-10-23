"""Find the translatable text in a page and swap in translations.

A "segment" is the text of one block (a paragraph, heading, list item, link,
label...) taken as it appears in the HTML, inline tags included, so a sentence
with a link or <strong> in it is translated as one piece. Attributes people
read (alt, title, placeholder, aria-label, button values) are translated too.
Scripts, styles and comments are left alone.
"""
import html
import re

TOKEN = re.compile(
    r'(?P<comment><!--.*?-->)'
    r'|(?P<raw><(?P<rawtag>script|style)\b(?:[^>"\']|"[^"]*"|\'[^\']*\')*>.*?</(?P=rawtag)\s*>)'
    r'|(?P<tag></?[A-Za-z][^\s/>]*(?:[^>"\']|"[^"]*"|\'[^\']*\')*>)'
    r'|(?P<text>[^<]+)'
    r'|(?P<lt><)',
    re.S | re.I)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
INLINE = {'a', 'abbr', 'b', 'br', 'cite', 'code', 'em', 'i', 'img', 'input', 'label', 'mark', 'q', 'small',
          'span', 'strong', 'sub', 'sup', 'time', 'u'}
ATTRS = ('alt', 'title', 'placeholder', 'aria-label')
WBR = re.compile(r'<wbr\s*/?>', re.I)  # line-break hint a translation may add
ATTR_RE = re.compile(r'(\s)([a-zA-Z_:][-a-zA-Z0-9_:.]*)(\s*=\s*)("([^"]*)"|\'([^\']*)\')')


def norm(s):
    """Key used to look a string up: entities decoded, whitespace collapsed."""
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


class Node:
    __slots__ = ('tag', 'start', 'open_end', 'close_start', 'end', 'children', 'is_text', 'parent')

    def __init__(self, tag, start, open_end, is_text=False, parent=None):
        self.tag, self.start, self.open_end, self.is_text, self.parent = tag, start, open_end, is_text, parent
        self.close_start = self.end = open_end
        self.children = []


def parse(doc):
    root = Node('#root', 0, 0)
    stack = [root]
    for m in TOKEN.finditer(doc):
        if m.group('text') is not None or m.group('lt') is not None:
            stack[-1].children.append(Node('#text', m.start(), m.end(), True, stack[-1]))
        elif m.group('tag'):
            t = m.group('tag')
            name = re.match(r'</?([A-Za-z][^\s/>]*)', t).group(1).lower()
            if t.startswith('</'):
                for i in range(len(stack) - 1, 0, -1):
                    if stack[i].tag == name:
                        for n in stack[i:]:
                            n.close_start, n.end = m.start(), m.end()
                        del stack[i:]
                        break
            else:
                node = Node(name, m.start(), m.end(), parent=stack[-1])
                stack[-1].children.append(node)
                if name not in VOID and not t.endswith('/>'):
                    stack.append(node)
        else:  # comment, script or style: opaque
            stack[-1].children.append(Node('#opaque', m.start(), m.end(), parent=stack[-1]))
    for n in stack[1:]:
        n.close_start = n.end = len(doc)
    root.close_start = root.end = len(doc)
    return root


def inline_only(node):
    return all(c.is_text or (c.tag in INLINE and inline_only(c)) for c in node.children)


def has_text(node, doc):
    return any((c.is_text and doc[c.start:c.end].strip()) or (not c.is_text and c.tag != '#opaque' and has_text(c, doc))
               for c in node.children)


def core(children, doc):
    """Trim whitespace and void tags at the edges; step into a single wrapper element."""
    kids = list(children)
    while True:
        while kids and ((kids[0].is_text and not doc[kids[0].start:kids[0].end].strip()) or (not kids[0].is_text and kids[0].tag in VOID)):
            kids.pop(0)
        while kids and ((kids[-1].is_text and not doc[kids[-1].start:kids[-1].end].strip()) or (not kids[-1].is_text and kids[-1].tag in VOID)):
            kids.pop()
        if len(kids) == 1 and not kids[0].is_text:
            kids = list(kids[0].children)
            continue
        break
    if not kids:
        return None
    start, end = kids[0].start, kids[-1].end
    raw = doc[start:end]
    # keep the leading/trailing spaces of the outer text nodes outside the segment
    lead = len(raw) - len(raw.lstrip())
    trail = len(raw) - len(raw.rstrip())
    return start + lead, end - trail


def segments(doc):
    """Return [(start, end)] for every translatable text segment, in document order."""
    out = []

    def run_segments(run):
        tops_text = any(c.is_text and doc[c.start:c.end].strip() for c in run)
        if tops_text:
            span = core(run, doc)
            if span:
                out.append(span)
        else:  # siblings separated only by whitespace: one segment each
            for c in run:
                if not c.is_text and c.tag not in VOID and has_text(c, doc):
                    span = core([c], doc)
                    if span:
                        out.append(span)

    def walk(node):
        if node.tag in ('#opaque',) or node.is_text:
            return
        if node.tag != '#root' and node.tag not in INLINE and inline_only(node) and has_text(node, doc):
            run_segments(node.children)
            return
        run = []
        for c in node.children:
            if c.is_text or (c.tag in INLINE and inline_only(c)):
                run.append(c)
            else:
                if run:
                    run_segments(run)
                run = []
                walk(c)
        if run:
            run_segments(run)

    walk(parse(doc))
    # nothing to translate in numbers, phone numbers and other letter-free text
    return sorted({sp for sp in set(out) if re.search(r'[A-Za-z]', html.unescape(re.sub(r'<[^>]*>', '', doc[sp[0]:sp[1]])))})


def tags_in(s):
    return sorted(re.sub(r'\s+', ' ', t) for t in re.findall(r'<(?:[^>"\']|"[^"]*"|\'[^\']*\')*>', s))


def attr_strings(doc):
    """[(start, end, raw_value)] for readable attribute values in start tags outside scripts/styles."""
    found = []
    for m in TOKEN.finditer(doc):
        t = m.group('tag')
        if not t or t.startswith('</'):
            continue
        name = re.match(r'<([A-Za-z][^\s/>]*)', t).group(1).lower()
        is_button = name == 'input' and re.search(r'\stype\s*=\s*["\']?(submit|button)', t, re.I)
        for a in ATTR_RE.finditer(t):
            key = a.group(2).lower()
            if key in ATTRS or (key == 'value' and is_button):
                val = a.group(5) if a.group(5) is not None else a.group(6)
                if val and val.strip():
                    vstart = m.start() + a.start(4) + 1
                    found.append((vstart, vstart + len(val), val))
    return found


def strings(doc):
    """All English strings (normalised) a translation table must cover."""
    keys = [norm(doc[s:e]) for s, e in segments(doc)] + [norm(v) for _, _, v in attr_strings(doc)]
    return [k for k in keys if k]


def translate(doc, table, missing):
    """Swap every segment and readable attribute for its translation (table: norm(English) -> HTML)."""
    edits = []
    for s, e in segments(doc):
        src = doc[s:e]
        key = norm(src)
        if key not in table:
            missing.append(key)
            continue
        dst = table[key]
        # a translation may add <wbr> where a long heading may break; every other tag must match
        if tags_in(WBR.sub('', dst)) != tags_in(src):
            raise ValueError(f'tags differ in translation of: {key[:80]}')
        tag_start = doc.rfind('<', 0, s)
        if doc[tag_start:tag_start + 7].lower() == '<option':
            dst = WBR.sub('', dst)  # an option holds plain text only
            # keep the English option text as the submitted value
            if 'value=' not in doc[tag_start:s]:
                edits.append((tag_start + 7, tag_start + 7, f' value="{html.escape(html.unescape(src), quote=True)}"'))
        edits.append((s, e, dst))
    for s, e, val in attr_strings(doc):
        key = norm(val)
        if key not in table:
            missing.append(key)
            continue
        edits.append((s, e, html.escape(html.unescape(WBR.sub('', table[key])), quote=True)))
    for s, e, dst in sorted(edits, key=lambda x: (x[0], x[1]), reverse=True):
        doc = doc[:s] + dst + doc[e:]
    return doc

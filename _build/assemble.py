# -*- coding: utf-8 -*-
"""
בונה את עמודי האתר מתוך ה-chrome המשותף של index.html (topbar, header, drawer,
sprite, footer, ווידג'ט הנגישות) + קטעי head/main ייעודיים לכל עמוד.

מבנה הכתובות: כל עמוד פנימי נשמר כ-<שם>/index.html, כך שהכתובת באתר היא
/services/ ולא /services.html - בלי צורך בהגדרות שרת מיוחדות.

הנתיבים היחסיים ב-index.html נכתבים מנקודת המבט של שורש האתר; הסקריפט מוסיף
"../" אוטומטית כשהוא בונה עמוד שיושב בתיקייה.

הרצה מתוך התיקייה הזו:
    python assemble.py
"""
import re, sys, io, os

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SP = os.path.dirname(os.path.abspath(__file__))   # _build/
SITE = os.path.dirname(SP)                        # שורש האתר

# name -> (הכתובת בתפריט שתסומן כעמוד פעיל, נתיב הפלט)
PAGES = [
    ('services',      'services/',      'services/index.html'),
    ('about',         'about/',         'about/index.html'),
    ('contact',       'contact/',       'contact/index.html'),
    ('privacy',       'privacy/',       'privacy/index.html'),
    ('accessibility', 'accessibility/', 'accessibility/index.html'),
    ('404',           None,             '404.html'),
    # עמודי הטיפולים - בני של "תחומי עיסוק", ולכן מסמנים אותו בתפריט
    ('checkup',       'services/',      'checkup/index.html'),
    ('emergency',     'services/',      'emergency/index.html'),
    ('extractions',   'services/',      'extractions/index.html'),
    ('sealants',      'services/',      'sealants/index.html'),
    ('root-canal',    'services/',      'root-canal/index.html'),
    ('scaling',       'services/',      'scaling/index.html'),
]

SKIP_PREFIXES = ('#', 'http://', 'https://', '//', '/', 'tel:', 'mailto:',
                 'data:', 'javascript:')


def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def _bump(val, up):
    """מוסיף ../ לנתיב יחסי. מחזיר None אם אין מה לשנות."""
    if val.startswith(SKIP_PREFIXES):
        return None
    if val.startswith('./'):
        val = val[2:]
    return up + val


def rewrite_relative(html, depth):
    """מתאים נתיבים יחסיים לעמוד שיושב depth תיקיות מתחת לשורש."""
    if depth <= 0:
        return html
    up = '../' * depth

    def fix_attr(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        new = _bump(val, up)
        return m.group(0) if new is None else '%s=%s%s%s' % (attr, q, new, q)

    html = re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix_attr, html)

    def fix_srcset(m):
        q, val = m.group(1), m.group(2)
        parts = []
        for part in val.split(','):
            part = part.strip()
            if not part:
                continue
            bits = part.split()
            new = _bump(bits[0], up)
            if new is not None:
                bits[0] = new
            parts.append(' '.join(bits))
        return 'srcset=%s%s%s' % (q, ', '.join(parts), q)

    return re.sub(r'\bsrcset=(["\'])([^"\']*)\1', fix_srcset, html)


index = read(os.path.join(SITE, 'index.html'))
CHROME_TOP = index[index.index('<a class="skip-link"'):index.index('<main id="main">')]
CHROME_BOTTOM = index[index.index('<!-- ===================== footer ====================='):]


def build(name, active, out_rel):
    head = read(os.path.join(SP, name + '.head.html')).strip()
    main = read(os.path.join(SP, name + '.main.html')).strip()

    chrome = CHROME_TOP.replace(' aria-current="page"', '')
    if active:
        chrome = re.sub(r'(<a class="nav__link" href="%s")' % re.escape(active),
                        r'\1 aria-current="page"', chrome)
        chrome = re.sub(r'(<li><a href="%s")' % re.escape(active),
                        r'\1 aria-current="page"', chrome)

    page = ('<!DOCTYPE html>\n<html lang="he" dir="rtl">\n<head>\n'
            + head + '\n</head>\n<body>\n' + chrome + main + '\n\n' + CHROME_BOTTOM)

    depth = out_rel.count('/')
    page = rewrite_relative(page, depth)

    out = os.path.join(SITE, out_rel.replace('/', os.sep))
    write(out, page)
    print('wrote %-26s %6d bytes  (depth %d)' % (out_rel, len(page), depth))


if __name__ == '__main__':
    only = sys.argv[1:]
    for name, active, out_rel in PAGES:
        if only and name not in only:
            continue
        build(name, active, out_rel)

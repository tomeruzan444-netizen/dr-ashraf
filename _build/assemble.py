# -*- coding: utf-8 -*-
"""
בונה את עמודי האתר מתוך ה-chrome המשותף של index.html (topbar, header, drawer,
sprite, footer, ווידג'ט הנגישות) + קטעי head/main ייעודיים לכל עמוד.

הרצה מתוך התיקייה הזו:
    python assemble.py services:services.html about:about.html contact:contact.html \
                       privacy:privacy.html accessibility:accessibility.html 404:404.html

הפורמט הוא  <שם-הקובץ>:<ה-href שיסומן כעמוד הפעיל בתפריט>
"""
import re, sys, io, os

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SP = os.path.dirname(os.path.abspath(__file__))   # _build/
SITE = os.path.dirname(SP)                        # שורש האתר

def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()

def write(p, s):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)

index = read(os.path.join(SITE, 'index.html'))

top_start = index.index('<a class="skip-link"')
top_end = index.index('<main id="main">')
CHROME_TOP = index[top_start:top_end]

bot_start = index.index('<!-- ===================== footer =====================')
CHROME_BOTTOM = index[bot_start:]           # includes </body></html>

def build(name, active):
    head = read(os.path.join(SP, name + '.head.html')).strip()
    main = read(os.path.join(SP, name + '.main.html')).strip()

    chrome = CHROME_TOP.replace(' aria-current="page"', '')
    chrome = re.sub(r'(<a class="nav__link" href="%s")' % re.escape(active),
                    r'\1 aria-current="page"', chrome)
    chrome = re.sub(r'(<li><a href="%s")' % re.escape(active),
                    r'\1 aria-current="page"', chrome)

    page = (
        '<!DOCTYPE html>\n<html lang="he" dir="rtl">\n<head>\n'
        + head + '\n</head>\n<body>\n'
        + chrome
        + main + '\n\n'
        + CHROME_BOTTOM
    )
    out = os.path.join(SITE, name + '.html')
    write(out, page)
    print('wrote %s.html - %d bytes' % (name, len(page)))

if __name__ == '__main__':
    for spec in sys.argv[1:]:
        n, a = spec.split(':')
        build(n, a)

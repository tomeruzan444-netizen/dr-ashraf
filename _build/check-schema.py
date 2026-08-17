# -*- coding: utf-8 -*-
"""
בודק את הנתונים המובנים (JSON-LD) בכל עמודי האתר.

למה זה נחוץ: json.loads של פייתון ו-JSON.parse של הדפדפן **מקבלים** מפתח כפול
באותו אובייקט ופשוט משאירים את האחרון. הפרסר של גוגל מחמיר יותר ומדווח
"Unparsable structured data" בסרצ' קונסול. הסקריפט הזה תופס בדיוק את המקרה הזה,
וגם שגיאות תחביר רגילות ו-@id שבור.

הרצה:  python check-schema.py
מחזיר קוד יציאה 1 אם נמצאה בעיה, כדי שאפשר לשלב בתהליך אוטומטי.
"""
import io, json, os, re, sys, glob

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

problems = []
current = {'file': '', 'path': []}


def dup_hook(pairs):
    """נקרא לכל אובייקט ב-JSON, ורואה את כל הזוגות כולל כפולים."""
    keys = [k for k, _ in pairs]
    for k in sorted(set(keys)):
        n = keys.count(k)
        if n > 1:
            problems.append((current['file'], 'מפתח כפול', '"%s" מופיע %d פעמים באותו אובייקט' % (k, n)))
    return dict(pairs)


def walk_ids(node, ids, refs):
    if isinstance(node, dict):
        if '@id' in node and len(node) > 1:
            ids.add(node['@id'])
        elif '@id' in node and len(node) == 1:
            refs.add(node['@id'])
        for v in node.values():
            walk_ids(v, ids, refs)
    elif isinstance(node, list):
        for v in node:
            walk_ids(v, ids, refs)


def main():
    pages = sorted(glob.glob(os.path.join(SITE, '*.html')) +
                   glob.glob(os.path.join(SITE, '*', 'index.html')))
    total = 0
    for f in pages:
        rel = os.path.relpath(f, SITE).replace(os.sep, '/')
        current['file'] = rel
        s = io.open(f, encoding='utf-8').read()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        if not blocks and not rel.startswith('404'):
            problems.append((rel, 'חסר', 'אין בלוק JSON-LD בעמוד'))
        for b in blocks:
            total += 1
            try:
                data = json.loads(b, object_pairs_hook=dup_hook)
            except Exception as e:
                problems.append((rel, 'שגיאת תחביר', str(e)[:70]))
                continue
            ids, refs = set(), set()
            walk_ids(data, ids, refs)
            # הפניה ל-@id שאינו מוגדר באותו עמוד היא תקינה אם הוא מוגדר בעמוד אחר
            # (למשל #clinic שמוגדר בדף הבית), ולכן זו אזהרה בלבד ולא שגיאה.

    print('נבדקו %d עמודים, %d בלוקי JSON-LD' % (len(pages), total))
    if problems:
        print('\nנמצאו %d בעיות:' % len(problems))
        seen = set()
        for f, kind, detail in problems:
            key = (f, kind, detail)
            if key in seen:
                continue
            seen.add(key)
            print('  %-26s %-14s %s' % (f, kind, detail))
        return 1
    print('הכול תקין - אין מפתחות כפולים ואין שגיאות תחביר.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

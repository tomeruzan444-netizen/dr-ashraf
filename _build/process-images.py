# -*- coding: utf-8 -*-
"""
מכין את תמונות ה"לפני ואחרי" לאתר.

מה זה עושה:
  1. קורא כל קובץ מהתיקייה  assets/img/תמונות לפני ואחרי/
     (כל קובץ = תמונה אחת שמכילה "לפני" בצד שמאל ו"אחרי" בצד ימין, עם קו מפריד לבן)
  2. מזהה אוטומטית את הקו המפריד וחותך את התמונה לשניים
  3. חותך כל חצי ליחס 4:5, מקטין ל-760px רוחב וממיר ל-WebP
  4. שומר ב-  assets/img/results/case-NN-before.webp  /  case-NN-after.webp

דרישות:  pip install pillow numpy
הרצה:    python process-images.py

אחרי ההרצה - צריך לעדכן ידנית את רשימת המקרים והכיתובים ב-index.html
(חפשו  <div class="ba-grid" id="resultsGrid">) וב-_build/services.main.html.
"""
import os, re, sys, glob

# חלון הפקודות של Windows לא תמיד תומך בעברית - מכריחים UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    from PIL import Image
    import numpy as np
except ImportError:
    sys.exit('חסרות ספריות. הריצו:  pip install pillow numpy')

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC = os.path.join(SITE, 'assets', 'img', 'תמונות לפני ואחרי')
OUT = os.path.join(SITE, 'assets', 'img', 'results')

TARGET_RATIO = 4 / 5      # יחס הגובה-רוחב של הכרטיסים באתר
OUT_W = 760               # רוחב הפלט בפיקסלים
QUALITY = 82


def find_divider(im):
    """מאתר את הקו המפריד הלבן סביב מרכז התמונה. מחזיר (start, end)."""
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    w = im.width
    c = w // 2
    win = int(w * 0.06)
    lo_i, hi_i = c - win, c + win
    colmean = a.mean(axis=(0, 2))
    colstd = a.std(axis=(0, 2))
    ok = (colmean[lo_i:hi_i] > 228) & (colstd[lo_i:hi_i] < 30)
    if not ok.any():
        return c, c                       # אין קו מפריד - חותכים בדיוק באמצע
    cand = np.arange(lo_i, hi_i)[ok]
    runs = np.split(cand, np.where(np.diff(cand) != 1)[0] + 1)
    run = max(runs, key=len)
    return int(run[0]), int(run[-1])


def crop_to_ratio(im, ratio):
    w, h = im.size
    if w / h > ratio:
        nw = int(round(h * ratio)); x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(round(w / ratio)); y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def main():
    if not os.path.isdir(SRC):
        sys.exit('לא נמצאה התיקייה: ' + SRC)
    os.makedirs(OUT, exist_ok=True)

    files = [f for f in glob.glob(os.path.join(SRC, '*'))
             if os.path.splitext(f)[1].lower() in ('.png', '.jpg', '.jpeg', '.webp')]
    if not files:
        sys.exit('לא נמצאו תמונות ב: ' + SRC)

    def num(path):
        m = re.findall(r'\d+', os.path.basename(path))
        return int(m[0]) if m else 0

    for f in sorted(files, key=num):
        n = num(f)
        im = Image.open(f).convert('RGB')
        lo, hi = find_divider(im)
        pad = 2
        halves = (
            ('before', im.crop((0, 0, max(1, lo - pad), im.height))),
            ('after',  im.crop((min(im.width - 1, hi + pad + 1), 0, im.width, im.height))),
        )
        for label, part in halves:
            p = crop_to_ratio(part, TARGET_RATIO)
            p = p.resize((OUT_W, int(round(OUT_W / TARGET_RATIO))), Image.LANCZOS)
            name = 'case-%02d-%s.webp' % (n, label)
            path = os.path.join(OUT, name)
            p.save(path, 'WEBP', quality=QUALITY, method=6)
            print('%s  %sx%s  %dKB' % (name, p.width, p.height, os.path.getsize(path) // 1024))

    print('\nסה"כ %d קבצים ב-%s' % (len(os.listdir(OUT)), OUT))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
בונה מחדש את תמונת השיתוף לרשתות (Open Graph) - assets/img/og-image.jpg

זו התמונה שמופיעה בתצוגה המקדימה כששולחים קישור לאתר בוואטסאפ, פייסבוק,
טלגרם, לינקדאין ו-X. היא מכילה את התמונה של ד"ר אשרף, שם, תחום ומספר טלפון.

מתי צריך להריץ מחדש:
  - השתנה מספר הטלפון או הכתובת
  - התחלפה התמונה של ד"ר אשרף (assets/img/dr-asharaf-cutout-720.webp)
  - רוצים לשנות את הכיתוב

דרישות:  pip install pillow pymupdf python-bidi
הרצה:    python make-og-image.py

חשוב: אחרי החלפת התמונה, וואטסאפ ופייסבוק שומרים את התצוגה הישנה במטמון.
כדי לרענן - להשתמש ב-Facebook Sharing Debugger:
https://developers.facebook.com/tools/debug/
"""
import math, os, re, sys, urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import fitz
    from bidi.algorithm import get_display
except ImportError:
    sys.exit('חסרות ספריות. הריצו:  pip install pillow pymupdf python-bidi')

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
IMG = os.path.join(SITE, 'assets', 'img')
FONTS = os.path.join(HERE, '.fonts')

# ------------------------------------------------------- מה כתוב בתמונה
NAME = 'ד״ר אשרף אטמנה'
ROLE = 'רופא שיניים ואסתטיקה'
META = 'מעל 22 שנות ניסיון · רמת החייל, תל אביב'
PHONE = '050-4588554'

W, H = 1200, 630
NAVY, NAVY_HI, SKY = (44, 70, 116), (63, 103, 163), (207, 234, 241)


def get_fonts():
    """מוריד את הגופן Assistant (אותו גופן שבאתר) פעם אחת ל-_build/.fonts"""
    os.makedirs(FONTS, exist_ok=True)
    want = {'ExtraBold': None, 'Bold': None, 'Medium': None, 'Regular': None}
    cached = {}
    for f in os.listdir(FONTS):
        if f.endswith('.ttf'):
            try:
                cached[ImageFont.truetype(os.path.join(FONTS, f), 12).getname()[1]] = os.path.join(FONTS, f)
            except Exception:
                pass
    if all(k in cached for k in want):
        return cached

    req = urllib.request.Request(
        'https://fonts.googleapis.com/css2?family=Assistant:wght@400..800',
        headers={'User-Agent': 'Mozilla/5.0'})
    css = urllib.request.urlopen(req, timeout=30).read().decode()
    for i, url in enumerate(sorted(set(re.findall(r'https://fonts\.gstatic\.com[^)]+', css)))):
        path = os.path.join(FONTS, 'assistant-%d.ttf' % i)
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
        try:
            cached[ImageFont.truetype(path, 12).getname()[1]] = path
        except Exception:
            pass
    missing = [k for k in want if k not in cached]
    if missing:
        sys.exit('לא נמצאו משקלי גופן: ' + ', '.join(missing))
    return cached


def main():
    fonts = get_fonts()
    F = lambda w, s: ImageFont.truetype(fonts[w], s)
    heb = get_display

    # רקע עם גרדיאנט
    img = Image.new('RGB', (W, H), NAVY)
    px = img.load()
    for y in range(H):
        for x in range(0, W, 3):
            t = 1 - min(1.0, math.hypot((x - 980) / 1050.0, (y - 60) / 820.0))
            c = tuple(int(NAVY[i] + (NAVY_HI[i] - NAVY[i]) * t) for i in range(3))
            for k in range(3):
                if x + k < W:
                    px[x + k, y] = c

    # גל המותג בתחתית
    wp = fitz.open(os.path.join(IMG, 'wave.svg'))[0].get_pixmap(
        matrix=fitz.Matrix(W / 540.0, W / 540.0), alpha=True)
    wave = Image.frombytes('RGBA', (wp.width, wp.height), wp.samples).resize((W + 12, 210), Image.LANCZOS)
    wave.putalpha(wave.split()[3].point(lambda v: int(v * 0.16)))
    img.paste(wave, (-6, H - 210), wave)

    # רשת נקודות
    dots = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    for i in range(W - 330, W, 22):
        for j in range(28, 260, 22):
            dd.ellipse([i, j, i + 3, j + 3], fill=(255, 255, 255, 70))
    img.paste(dots, (0, 0), dots)

    # ד"ר אשרף
    cut = Image.open(os.path.join(IMG, 'dr-asharaf-cutout-720.webp')).convert('RGBA')
    ch = 596
    cut = cut.resize((int(round(cut.width * ch / float(cut.height))), ch), Image.LANCZOS)
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    hx, hy = 60 + cut.width // 2, H - ch // 2 + 10
    ImageDraw.Draw(halo).ellipse([hx - 250, hy - 250, hx + 250, hy + 250], fill=SKY + (46,))
    halo = halo.filter(ImageFilter.GaussianBlur(70))
    img.paste(halo, (0, 0), halo)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh.paste(cut, (60, H - ch + 12), cut)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    blk = Image.new('RGBA', (W, H), (6, 20, 44, 255))
    blk.putalpha(sh.split()[3].point(lambda v: int(v * 0.42)))
    img.paste(blk, (0, 0), blk)
    img.paste(cut, (60, H - ch), cut)

    d = ImageDraw.Draw(img)
    RIGHT = W - 74

    def rt(y, text, f, fill):
        s = heb(text)
        d.text((RIGHT - d.textlength(s, font=f), y), s, font=f, fill=fill)

    # סמל הלוגו בלבן
    paths = re.findall(r'<path fill="(#[0-9A-Fa-f]{6})" d="([^"]+)"/>',
                       open(os.path.join(IMG, 'logo-mark.svg'), encoding='utf-8').read())
    recol = {'#108BB9': '#FFFFFF', '#CFECF5': '#CFEAF1'}
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72.86 71.2">%s</svg>' % ''.join(
        '<path fill="%s" d="%s"/>' % (recol[c], p) for c, p in paths)
    tmp = os.path.join(HERE, '_ogmark.svg')
    open(tmp, 'w', encoding='utf-8').write(svg)
    mp = fitz.open(tmp)[0].get_pixmap(matrix=fitz.Matrix(74 / 72.86, 74 / 72.86), alpha=True)
    mark = Image.frombytes('RGBA', (mp.width, mp.height), mp.samples)
    img.paste(mark, (RIGHT - mark.width, 74), mark)
    os.remove(tmp)

    y = 74 + mark.height + 34
    rt(y, NAME, F('ExtraBold', 72), (255, 255, 255));            y += 96
    rt(y, ROLE, F('Medium', 40), SKY);                            y += 66
    d.line([(RIGHT - 300, y + 10), (RIGHT, y + 10)], fill=(255, 255, 255), width=2)
    y += 34
    rt(y, META, F('Regular', 30), (215, 226, 238));               y += 50

    pf = F('Bold', 32)
    pw = d.textlength(PHONE, font=pf)
    box = [RIGHT - pw - 52, y, RIGHT, y + int(pf.size * 1.35) + 13]
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=(255, 255, 255))
    d.text((box[0] + 26, y + 8), PHONE, font=pf, fill=(20, 52, 96))

    out = os.path.join(IMG, 'og-image.jpg')
    img.save(out, quality=88, optimize=True, progressive=True)
    print('נכתב: %s  (%dx%d, %dKB)' % (out, W, H, os.path.getsize(out) // 1024))
    print('זכרו לרענן את המטמון של פייסבוק/וואטסאפ:')
    print('https://developers.facebook.com/tools/debug/')


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Shared machinery for building the treatment-page fragments."""
import io, json, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SITE = os.path.join('c:/', 'd-e-v', '\u05d3\u05e8 \u05d0\u05e9\u05e8\u05e3')
BUILD = os.path.join(SITE, '_build')
BASE = 'https://dr-atamna.co.il'

TITLES = {
    'checkup':     ('בדיקה כללית', 'i-tooth-check'),
    'emergency':   ('טיפולי חירום', 'i-emergency'),
    'extractions': ('עקירות שיניים', 'i-extract'),
    'sealants':    ('איטום חריצים', 'i-sealant'),
    'root-canal':  ('טיפול שורש', 'i-root'),
    'scaling':     ('הסרת אבנית', 'i-scaler'),
}


def head(p):
    faq = ',\n'.join(
        '        {\n'
        '          "@type": "Question",\n'
        '          "name": %s,\n'
        '          "acceptedAnswer": { "@type": "Answer", "text": %s }\n'
        '        }' % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False))
        for q, a in p['faq'])

    url = '%s/%s/' % (BASE, p['slug'])
    label = TITLES[p['slug']][0]

    return '''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#324D7E">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{url}">

<meta property="og:type" content="article">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="ד״ר אשרף אטמנה - רפואת שיניים ואסתטיקה">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{ogdesc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}/assets/img/og-image.jpg">
<meta property="og:image:secure_url" content="{base}/assets/img/og-image.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ד״ר אשרף אטמנה, רופא שיניים ואסתטיקה ברמת החייל, תל אביב">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{base}/assets/img/og-image.jpg">
<meta name="twitter:image:alt" content="ד״ר אשרף אטמנה, רופא שיניים ואסתטיקה ברמת החייל, תל אביב">

<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">

<link rel="preload" href="assets/fonts/assistant-hebrew.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
<noscript><style>.reveal{{opacity:1!important;transform:none!important}}</style></noscript>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "דף הבית", "item": "{base}/" }},
        {{ "@type": "ListItem", "position": 2, "name": "תחומי עיסוק", "item": "{base}/services/" }},
        {{ "@type": "ListItem", "position": 3, "name": "{label}", "item": "{url}" }}
      ]
    }},
    {{
      "@type": "MedicalWebPage",
      "@id": "{url}#page",
      "url": "{url}",
      "name": {jname},
      "description": {jdesc},
      "inLanguage": "he-IL",
      "isPartOf": {{ "@id": "{base}/#website" }},
      "about": {{ "@id": "{url}#procedure" }},
      "provider": {{ "@id": "{base}/#clinic" }},
      "audience": {{ "@type": "Patient" }},
      "reviewedBy": {{ "@id": "{base}/#doctor" }},
      "lastReviewed": "2026-08-12",
      "speakable": {{ "@type": "SpeakableSpecification", "cssSelector": [".page-hero h1", ".lede"] }}
    }},
    {{
      "@type": "MedicalProcedure",
      "@id": "{url}#procedure",
      "name": "{procname}",
      "alternateName": {jalt},
      "description": {jprocdesc},
      "procedureType": "{ptype}",
      "bodyLocation": "{bodyloc}",
      "howPerformed": {jhow},
      "preparation": {jprep},
      "followup": {jfollow},
      "performer": {{ "@id": "{base}/#doctor" }},
      "availableService": {{ "@id": "{base}/#clinic" }}
    }},
    {{
      "@type": "FAQPage",
      "@id": "{url}#faq",
      "inLanguage": "he-IL",
      "mainEntityOfPage": {{ "@id": "{url}#page" }},
      "mainEntity": [
{faq}
      ]
    }}
  ]
}}
</script>'''.format(
        title=p['title'], desc=p['desc'], url=url, base=BASE, label=label,
        ogtitle=p.get('ogtitle', p['title']), ogdesc=p.get('ogdesc', p['desc']),
        jname=json.dumps(p['schema_name'], ensure_ascii=False),
        jdesc=json.dumps(p['desc'], ensure_ascii=False),
        procname=p['procname'],
        jalt=json.dumps(p['procalt'], ensure_ascii=False),
        jprocdesc=json.dumps(p['procdesc'], ensure_ascii=False),
        ptype=p.get('ptype', 'https://schema.org/TherapeuticProcedure'),
        bodyloc=p.get('bodyloc', 'שיניים'),
        jhow=json.dumps(p['how'], ensure_ascii=False),
        jprep=json.dumps(p['prep'], ensure_ascii=False),
        jfollow=json.dumps(p['follow'], ensure_ascii=False),
        faq=faq)


def faq_html(p):
    items = '\n'.join(
        '        <details class="faq__item">\n'
        '          <summary class="faq__q">%s</summary>\n'
        '          <div class="faq__a"><p>%s</p></div>\n'
        '        </details>' % (q, a)
        for q, a in p['faq'])
    return '''
  <section class="section section--tint" id="faq" aria-labelledby="faq-t">
    <div class="wrap wrap--narrow">
      <div class="head head--center">
        <span class="head__ghost" aria-hidden="true">FAQ</span>
        <div class="head__title">
          <span class="head__eyebrow">שאלות נפוצות</span>
          <h2 id="faq-t">%s</h2>
        </div>
      </div>
      <div class="faq">
%s
      </div>
    </div>
  </section>
''' % (p['faq_title'], items)


def related_html(p):
    cards = '\n'.join(
        '          <a href="%s/"><svg><use href="#%s"></use></svg>%s</a>'
        % (s, TITLES[s][1], TITLES[s][0]) for s in p['related'])
    return '''      <div class="related">
        <h2>טיפולים נוספים שכדאי להכיר</h2>
        <div class="related__grid">
%s
          <a href="services/"><svg><use href="#i-clipboard"></use></svg>כל תחומי העיסוק</a>
        </div>
      </div>
''' % cards


def sources_html(p):
    items = '\n'.join(
        '          <li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (u, t)
        for t, u in p['sources'])
    return '''      <div class="sources">
        <h2>מקורות והרחבה</h2>
        <ul>
%s
        </ul>
        <p style="font-size:var(--fs-xs);color:var(--muted);margin-top:.8rem">
          המידע בעמוד זה נכתב על ידי ד״ר אשרף אטמנה ומיועד להיכרות כללית עם הטיפול.
          הוא אינו מהווה ייעוץ רפואי, אבחנה או תחליף לבדיקה קלינית. התאמת הטיפול
          נקבעת בבדיקה אישית במרפאה.
        </p>
      </div>
''' % items


def cta_html(p):
    return '''
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="cta-band reveal">
        <div>
          <h2>%s</h2>
          <p>%s</p>
        </div>
        <div class="btn-row">
          <a class="btn btn--light" href="tel:+97236483477"><svg><use href="#i-phone"></use></svg>03-6483477</a>
          <a class="btn btn--outline-light" href="contact/"><svg><use href="#i-calendar"></use></svg>קביעת תור</a>
        </div>
      </div>
    </div>
  </section>
''' % (p['cta_h'], p['cta_p'])


WAVE = ('    <div class="page-hero__wave" aria-hidden="true">\n'
        '      <svg viewBox="0 0 1440 100" preserveAspectRatio="none">'
        '<path fill="#fff" d="M0 52c160-38 320-48 480-30s320 56 480 58 320-24 480-58v78H0Z"/></svg>\n'
        '    </div>')


def main_html(p):
    return '''<main id="main">

  <section class="page-hero">
    <div class="wrap page-hero__inner">
      <nav class="crumbs" aria-label="מיקומך באתר">
        <ol>
          <li><a href="./">דף הבית</a></li>
          <li><a href="services/">תחומי עיסוק</a></li>
          <li><span aria-current="page">{label}</span></li>
        </ol>
      </nav>
      <h1>{h1}</h1>
      <p class="page-hero__lead">{herolead}</p>
      <div class="btn-row" style="margin-top:1.8rem">
        <a class="btn btn--light" href="contact/"><svg><use href="#i-calendar"></use></svg>קביעת תור</a>
        <a class="btn btn--outline-light" href="tel:+97236483477"><svg><use href="#i-phone"></use></svg>03-6483477</a>
      </div>
    </div>
{wave}
  </section>

  <section class="section">
    <div class="wrap wrap--narrow prose">
{body}
{related}{sources}    </div>
  </section>
{faq}{cta}</main>
'''.format(label=TITLES[p['slug']][0], h1=p['h1'], herolead=p['herolead'], wave=WAVE,
           body=p['body'].rstrip(), related=related_html(p), sources=sources_html(p),
           faq=faq_html(p), cta=cta_html(p))


def write(pages):
    for p in pages:
        for suffix, content in (('head', head(p)), ('main', main_html(p))):
            f = os.path.join(BUILD, '%s.%s.html' % (p['slug'], suffix))
            io.open(f, 'w', encoding='utf-8', newline='\n').write(content)
        words = len(p['body'].split())
        print('  %-14s head+main  (~%d words in body)' % (p['slug'], words))

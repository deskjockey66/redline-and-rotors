from pathlib import Path
from datetime import date, datetime
from html import escape, unescape
import shutil, yaml, os, re, math, hashlib
from html.parser import HTMLParser
try:
 import markdown
 render_md=lambda s: markdown.markdown(s,extensions=["extra","sane_lists"])
except ImportError:
 import mistune
 render_md=mistune.html

ROOT=Path(__file__).parent
OUT=ROOT/'_site'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copy(ROOT/'style.css',OUT/'style.css')
shutil.copy(ROOT/'favicon.svg',OUT/'favicon.svg')
shutil.copy(ROOT/'carousel.js',OUT/'carousel.js')
STYLE_FILE='style.'+hashlib.sha256((ROOT/'style.css').read_bytes()).hexdigest()[:12]+'.css'
CAROUSEL_FILE='carousel.'+hashlib.sha256((ROOT/'carousel.js').read_bytes()).hexdigest()[:12]+'.js'
shutil.copy(ROOT/'style.css',OUT/STYLE_FILE)
shutil.copy(ROOT/'carousel.js',OUT/CAROUSEL_FILE)
(OUT/'media').mkdir(exist_ok=True)
if (ROOT/'media').is_dir():
    shutil.copytree(ROOT/'media',OUT/'media',dirs_exist_ok=True)
(OUT/'.nojekyll').touch()

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
    def handle_data(self,text):
        self.parts.append(text)

def reading_minutes(html):
    parser=PlainText()
    parser.feed(html)
    words=len(re.findall(r"\b[\w’-]+\b",' '.join(parser.parts)))
    return max(1,math.ceil(words/220))

def parse_post(path):
    raw=path.read_text(encoding='utf-8')
    if raw.startswith('---'):
        _,front,body=raw.split('---',2)
        data=yaml.safe_load(front) or {}
    else: data={};body=raw
    data['body']=render_md(body)
    data['reading_minutes']=reading_minutes(data['body'])
    data['slug']=path.stem
    data['date']=str(data.get('date',''))
    return data

def safe(x):return escape(str(x or ''),quote=True)
BASE=os.environ.get('SITE_BASE_PATH','/redline-and-rotors').rstrip('/')
def url(x):
    x=str(x or '')
    if not x or x.startswith(('https://','http://','//','#','mailto:','tel:','data:')):
        return x
    # Accept old Pages CMS paths as well as new domain-neutral media paths.
    legacy='/redline-and-rotors'
    if x == legacy:
        x='/'
    elif x.startswith(legacy+'/') or x.startswith(legacy+'#'):
        x=x[len(legacy):]
    if BASE and (x == BASE or x.startswith(BASE+'/')):
        return x
    return BASE+'/'+x.lstrip('/')

def asset(x):
    x=str(x or '').strip()
    if not x:return ''
    return url(x)

def header():
    return '''<a class="skip" href="#main">Skip to content</a><div class="topline"></div><header><div class="wrap"><div class="utility"><span>Independent automotive & horology journal</span><span>Timepieces. Machines. Miles.</span></div><div class="brand"><a class="brand-name" href="/">REDLINE <span>&</span> ROTORS</a><a class="mark" href="/" aria-label="Home">R/R</a></div><nav><a href="/">Latest</a><a href="/#stories">Stories</a><a href="/about/">About</a></nav></div></header>'''
def page(title,body,description='Timepieces. Machines. Miles.'):
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f1e9"><title>{safe(title)} — Redline & Rotors</title><meta name="description" content="{safe(description)}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/{STYLE_FILE}"></head><body>{header()}{body}<footer><div class="wrap footer-row"><span>© {date.today().year} REDLINE & ROTORS · TIMEPIECES. MACHINES. MILES.</span><span>INDEPENDENT BY DESIGN</span></div><a href="/credits/">Photography credits</a></footer></body></html>'''
    import re
    return re.sub(r'(href|src)="(/[^"]*)"',lambda m:m[1]+'="'+safe(url(unescape(m[2])))+'"',html)

posts=[parse_post(p) for p in (ROOT/'content/posts').glob('*.md')]
posts=[p for p in posts if p.get('published',True)]
posts.sort(key=lambda p:p['date'],reverse=True)
for p in posts:
    dest=OUT/'stories'/p['slug'];dest.mkdir(parents=True,exist_ok=True)
    img=asset(p.get('cover'))
    hero=f'<div class="article-hero {"watch-hero" if p.get("category")=="Timepieces" else ""}"><img src="{safe(img)}" alt="{safe(p["title"])}"></div>' if img else ''
    body=f'''<main id="main" class="article"><div class="eyebrow">{safe(p.get('category','Journal'))} / {safe(p['date'])} / {p['reading_minutes']} MIN READ</div><h1>{safe(p['title'])}</h1><p class="deck">{safe(p.get('summary',''))}</p>{hero}<p class="photo-credit">{safe(p.get('photo_credit',''))} · <a href="/credits/">Image licence</a></p><div class="article-body">{p['body']}</div><div class="note">More from the journal · <a href="/">Back to the homepage →</a></div></main>'''
    (dest/'index.html').write_text(page(p['title'],body,p.get('summary','')),encoding='utf-8')

home=yaml.safe_load((ROOT/'content/homepage.yml').read_text())
# Keep the welcome story in every edition, alongside every published review.
welcome=next((p for p in posts if p['slug']=='start-here'),None)
featured=next((p for p in posts if url('/stories/'+p['slug']+'/')==url(home.get('hero_link'))),None)
ordered=[]
for item in [featured,welcome]+posts:
    if item and not any(p['slug']==item['slug'] for p in ordered):
        ordered.append(item)
slides=[]
dots=[]
for i,p in enumerate(ordered):
    is_featured=p is featured
    image_path=home.get('hero_image') if is_featured else p.get('cover')
    title=home.get('hero_title') if is_featured else p['title']
    description=home.get('hero_description') if is_featured else p.get('summary','')
    kicker=home.get('hero_kicker') if is_featured else ('START HERE / THE JOURNAL' if p is welcome else p.get('category','Journal')+' / '+str(p['reading_minutes'])+' MIN READ')
    visual_class='is-watch' if p.get('category')=='Timepieces' else ('is-portrait' if p['slug']=='audi-rs3' else '')
    loading='fetchpriority="high"' if i==0 else 'loading="lazy"'
    visual=f'<img src="{safe(asset(image_path))}" alt="{safe(p["title"])}" {loading}>' if image_path else ''
    hidden='' if i==0 else ' hidden'
    slides.append(f'''<article class="hero-slide" data-slide data-title="{safe(title)}" role="group" aria-roledescription="slide" aria-label="{i+1} of {len(ordered)}"{hidden}><div class="hero-visual {visual_class}">{visual}</div><div class="hero-info"><div class="eyebrow">{safe(kicker)}</div><h2>{safe(title)}</h2><p>{safe(description)}</p><a class="button" href="/stories/{safe(p['slug'])}/">Read the story ↗<span class="sr-only">: {safe(title)}</span></a></div></article>''')
    dots.append(f'<button type="button" data-slide-to="{i}" aria-label="Show story {i+1}: {safe(title)}" aria-pressed="{str(i==0).lower()}"><span></span></button>')
carousel=f'''<section class="hero hero-carousel" data-carousel role="region" aria-roledescription="carousel" aria-label="Featured stories"><div class="carousel-slides">{''.join(slides)}</div><div class="carousel-controls" data-controls hidden><div class="carousel-dots" role="group" aria-label="Choose a featured story">{''.join(dots)}</div><div class="carousel-actions"><span class="carousel-count" data-count>1 / {len(ordered)}</span><button type="button" data-prev aria-label="Previous story">←</button><button type="button" data-toggle>Pause</button><button type="button" data-next aria-label="Next story">→</button></div></div><p class="sr-only" data-status aria-live="polite" aria-atomic="true"></p></section>'''
cards=''
for p in posts:
    img=asset(p.get('cover'))
    visual_card=f'<img src="{safe(img)}" alt="{safe(p["title"])}" loading="lazy">' if img else ''
    cards+=f'''<a class="card {"watch-card" if p.get("category")=="Timepieces" else ""}" href="/stories/{safe(p['slug'])}/"><div class="thumb {'placeholder' if not img else ''}">{visual_card}</div><div class="eyebrow">{safe(p.get('category','Journal'))} / {safe(p['date'])} / {p['reading_minutes']} MIN READ</div><h3>{safe(p['title'])}</h3><p>{safe(p.get('summary',''))}</p></a>'''
if not cards: cards='<p>First stories are on their way.</p>'
body=f'''<main id="main"><div class="wrap"><section class="mast"><div><div class="eyebrow">THE INDEPENDENT JOURNAL / VOL. 01</div><h1>{safe(home.get('headline'))}</h1></div><p>{safe(home.get('intro'))}</p></section>{carousel}<section id="stories"><div class="section-head"><h2>The reading room</h2><small>MACHINES / TIMEPIECES / CULTURE</small></div><div class="cards">{cards}</div></section></div><section class="feature-band"><div class="wrap"><div><div class="eyebrow">REDLINE & ROTORS</div><h2>Driven by curiosity.</h2></div><p>A journal for people who care about how things feel, how they're made, and where they take us.</p></div></section></main>'''
(OUT/'index.html').write_text(page('Home',body+'<script src="/'+CAROUSEL_FILE+'" defer></script>',home.get('intro','')),encoding='utf-8')
about=parse_post(ROOT/'content/about.md')
about_html=f'''<main class="about"><div class="eyebrow">THE STORY BEHIND THE JOURNAL</div><h1>{safe(about.get('title','About'))}</h1><div class="article-body">{about['body']}</div></main>'''
(OUT/'about').mkdir()
(OUT/'about'/'index.html').write_text(page('About',about_html),encoding='utf-8')
print('Built',len(posts),'stories in',OUT)

credits=parse_post(ROOT/'content/credits.md')
(OUT/'credits').mkdir()
(OUT/'credits/index.html').write_text(page('Photography credits',f'<main class="about"><h1>Photography credits</h1><div class="article-body">{credits["body"]}</div></main>'),encoding='utf-8')

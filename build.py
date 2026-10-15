from pathlib import Path
from datetime import date, datetime
from html import escape
import shutil, yaml, os, re, math
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
    return x if x.startswith(('https://','http://','#')) or (BASE and x.startswith(BASE+'/')) else BASE+'/'+x.lstrip('/')

def asset(x):
    x=str(x or '').strip()
    if not x:return ''
    return url(x)

def header():
    return '''<a class="skip" href="#main">Skip to content</a><div class="topline"></div><header><div class="wrap"><div class="utility"><span>Independent automotive & horology journal</span><span>Timepieces. Machines. Miles.</span></div><div class="brand"><a class="brand-name" href="/">REDLINE <span>&</span> ROTORS</a><a class="mark" href="/" aria-label="Home">R/R</a></div><nav><a href="/">Latest</a><a href="/#stories">Stories</a><a href="/about/">About</a><a href="https://app.pagescms.org/" target="_blank" rel="noopener">Editor ↗</a></nav></div></header>'''
def page(title,body,description='Timepieces. Machines. Miles.'):
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f1e9"><title>{safe(title)} — Redline & Rotors</title><meta name="description" content="{safe(description)}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"></head><body>{header()}{body}<footer><div class="wrap footer-row"><span>© {date.today().year} REDLINE & ROTORS · TIMEPIECES. MACHINES. MILES.</span><span>INDEPENDENT BY DESIGN</span></div><a href="/credits/">Photography credits</a> · <a href="https://app.pagescms.org/">Publish an article ↗</a></footer></body></html>'''
    import re
    return re.sub(r'(href|src)="/(?!redline-and-rotors/)([^"]*)"',lambda m:m[1]+'="'+BASE+'/'+m[2]+'"',html)

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
hi=asset(home.get('hero_image'))
visual=f'<img src="{safe(hi)}" alt="Featured Redline & Rotors photograph">' if hi else ''
feature_link=url(home.get('hero_link')) if home.get('hero_link') else (f'/stories/{posts[0]["slug"]}/' if posts else '/about/')
cards=''
for p in posts:
    img=asset(p.get('cover'))
    visual_card=f'<img src="{safe(img)}" alt="{safe(p["title"])}" loading="lazy">' if img else ''
    cards+=f'''<a class="card {"watch-card" if p.get("category")=="Timepieces" else ""}" href="/stories/{safe(p['slug'])}/"><div class="thumb {'placeholder' if not img else ''}">{visual_card}</div><div class="eyebrow">{safe(p.get('category','Journal'))} / {safe(p['date'])} / {p['reading_minutes']} MIN READ</div><h3>{safe(p['title'])}</h3><p>{safe(p.get('summary',''))}</p></a>'''
if not cards: cards='<p>First stories are on their way.</p>'
body=f'''<main id="main"><div class="wrap"><section class="mast"><div><div class="eyebrow">THE INDEPENDENT JOURNAL / VOL. 01</div><h1>{safe(home.get('headline'))}</h1></div><p>{safe(home.get('intro'))}</p></section><section class="hero"><div class="hero-visual {'placeholder' if not hi else ''}">{visual}</div><div class="hero-info"><div class="eyebrow">{safe(home.get('hero_kicker'))}</div><h2>{safe(home.get('hero_title'))}</h2><p>{safe(home.get('hero_description'))}</p><a class="button" href="{safe(feature_link)}">Read the story ↗</a></div></section><section id="stories"><div class="section-head"><h2>The reading room</h2><small>MACHINES / TIMEPIECES / CULTURE</small></div><div class="cards">{cards}</div></section></div><section class="feature-band"><div class="wrap"><div><div class="eyebrow">REDLINE & ROTORS</div><h2>Driven by curiosity.</h2></div><p>A journal for people who care about how things feel, how they're made, and where they take us.</p></div></section></main>'''
(OUT/'index.html').write_text(page('Home',body,home.get('intro','')),encoding='utf-8')
about=parse_post(ROOT/'content/about.md')
about_html=f'''<main class="about"><div class="eyebrow">THE STORY BEHIND THE JOURNAL</div><h1>{safe(about.get('title','About'))}</h1><div class="article-body">{about['body']}</div></main>'''
(OUT/'about').mkdir()
(OUT/'about'/'index.html').write_text(page('About',about_html),encoding='utf-8')
print('Built',len(posts),'stories in',OUT)

credits=parse_post(ROOT/'content/credits.md')
(OUT/'credits').mkdir()
(OUT/'credits/index.html').write_text(page('Photography credits',f'<main class="about"><h1>Photography credits</h1><div class="article-body">{credits["body"]}</div></main>'),encoding='utf-8')

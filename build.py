from pathlib import Path
from datetime import date
from html import escape, unescape
from html.parser import HTMLParser
import os,re,math,hashlib,shutil,yaml
try:
 import markdown
 render_md=lambda s:markdown.markdown(s,extensions=["extra","sane_lists"])
except ImportError:
 import mistune
 render_md=mistune.html
ROOT=Path(__file__).parent;OUT=ROOT/'_site';BASE=os.getenv('SITE_BASE_PATH','/redline-and-rotors').rstrip('/')
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'media',OUT/'media');shutil.copy(ROOT/'favicon.svg',OUT/'favicon.svg');(OUT/'.nojekyll').touch()
HOME=yaml.safe_load((ROOT/'content/homepage.yml').read_text())
CONTACT=HOME.get('contact','https://www.instagram.com/redlinenrotors/')
JS='journal.'+hashlib.sha256((ROOT/'journal.js').read_bytes()).hexdigest()[:12]+'.js';shutil.copy(ROOT/'journal.js',OUT/JS)
CSS='style.'+hashlib.sha256((ROOT/'style.css').read_bytes()).hexdigest()[:12]+'.css';shutil.copy(ROOT/'style.css',OUT/CSS)
def safe(x):return escape(str(x or ''),quote=True)
def url(x):
 x=str(x or '');legacy='/redline-and-rotors'
 if not x or x.startswith(('https://','http://','//','#','mailto:','tel:','data:')):return x
 if x==legacy:x='/'
 elif x.startswith(legacy+'/'):x=x[len(legacy):]
 if BASE and (x==BASE or x.startswith(BASE+'/')):return x
 return BASE+'/'+x.lstrip('/')
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,d):self.parts.append(d)
def read(p):
 raw=p.read_text();_,front,body=raw.split('---',2);d=yaml.safe_load(front) or {};d['body']=render_md(body);d['slug']=p.stem
 t=Text();t.feed(d['body']);d['words']=len(re.findall(r"\b[\w’'-]+\b",' '.join(t.parts)));d['minutes']=max(1,math.ceil(d['words']/220));return d
posts=[read(p) for p in (ROOT/'content/posts').glob('*.md')];posts=[p for p in posts if p.get('published',False)]
posts.sort(key=lambda p:(str(p.get('date','')),int(p.get('order',0)),p['slug']),reverse=True)
NAV=[('/','Home'),('/cars/','Cars'),('/watches/','Watches'),('/about/','About')]
def page(title,body,description='Michael’s cars and watches. An ownership journal from Brisbane.'):
 nav=''
 for href,label in NAV:
  if label in ('Cars','Watches'):
   links=''.join(f'<a href="/stories/{p["slug"]}/">{safe(p["title"])}</a>' for p in posts if p.get('category')==label)
   nav+=f'<details class="nav-drop"><summary>{label}<span aria-hidden="true">⌄</span></summary><div class="dropdown"><a class="all-link" href="{href}">All {label.lower()} ↗</a>{links}</div></details>'
  else:nav+=f'<a class="nav-link" href="{href}">{label}</a>' 
 doc=f'''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f1e9"><title>{safe(title)} | Redline & Rotors</title><meta name="description" content="{safe(description)}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/{CSS}"><script src="/{JS}" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header><div class="wrap utility"><span>CARS & WATCHES</span><a href="{safe(CONTACT)}">@redlinenrotors ↗</a></div><div class="wrap header"><a class="brand" href="/">REDLINE <span>&</span> ROTORS</a><nav aria-label="Main navigation">{nav}</nav></div></header>{body}<footer><div class="wrap"><p>REDLINE & ROTORS · CARS & WATCHES</p><a href="{safe(CONTACT)}">Say hello on Instagram ↗</a><p class="fine">Photos are mine, taken on my phone. · <a href="/credits/">About the photos</a></p></div></footer></body></html>'''
 return re.sub(r'(href|src)="(/[^\"]*)"',lambda m:m[1]+'="'+safe(url(unescape(m[2])))+'"',doc)
def write(path,title,body,desc='Michael’s cars and watches. An ownership journal from Brisbane.'):
 p=OUT/path/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page(title,body,desc))
def meta(p):
 bits=[p.get('format','Entry')]
 if p.get('ownership'):bits.append(p['ownership'])
 if p.get('format')=='Photo post':bits.append('Photos')
 else:bits.append(f"{p['minutes']} min read")
 if p.get('show_date') and p.get('date'):bits.append(str(p['date']))
 return safe(' · '.join(bits))
def image(p,cls='',priority=False):
 if not p.get('cover'):return ''
 return f'<img class="{cls}" src="{safe(p["cover"])}" alt="{safe(p.get("image_alt",p["title"]))}" {"fetchpriority=high" if priority else "loading=lazy"}>'
def card(p):
 return f'''<article class="entry {'text-entry' if not p.get('cover') else ''}"><a href="/stories/{p['slug']}/">{image(p)}<div class="entry-content"><p class="meta">{meta(p)}</p><h2>{safe(p['title'])}</h2><p>{safe(p.get('summary',''))}</p><span class="read">Read entry ↗</span></div></a></article>'''
for p in posts:
 hero=f'<figure class="article-photo">{image(p,priority=True)}<figcaption>Photos are mine, taken on my phone.</figcaption></figure>' if p.get('cover') else ''
 updated=f'<p class="fine">Updated {safe(p.get("date"))}</p>' if p.get('date') else ''
 content=f'''<main id="main" class="article wrap"><div class="article-heading"><p class="meta">{meta(p)}</p><h1>{safe(p['title'])}</h1><p class="deck">{safe(p.get('summary',''))}</p></div>{hero}<div class="prose">{p['body']}{updated}<p class="back"><a href="/">← Back to the journal</a></p></div></main>'''
 write(Path('stories')/p['slug'],p['title'],content,p.get('summary',''))
h=yaml.safe_load((ROOT/'content/homepage.yml').read_text());latest=posts[0] if posts else None
slides=[];dots=[]
for i,p in enumerate(posts):
 visual=image(p,priority=i==0) if p.get('cover') else '<img src="/media/gtr-rear.jpg" alt="My GT-R photographed from the rear" loading="lazy">'
 slides.append(f'''<article class="hero-slide" data-slide data-title="{safe(p['title'])}" role="group" aria-roledescription="slide" aria-label="{i+1} of {len(posts)}"{'' if i==0 else ' hidden'}><a class="hero-visual" href="/stories/{p['slug']}/">{visual}</a><div class="hero-info"><p class="meta">{safe(p.get('category','Journal'))} / {meta(p)}</p><h2><a href="/stories/{p['slug']}/">{safe(p['title'])}</a></h2><p>{safe(p.get('summary',''))}</p><a class="button" href="/stories/{p['slug']}/">Read the story ↗</a></div></article>''')
 dots.append(f'<button data-slide-to="{i}" aria-label="Show story {i+1}: {safe(p["title"])}" aria-pressed="{str(i==0).lower()}"><span></span></button>')
feature=f'''<section class="hero-carousel" data-carousel role="region" aria-roledescription="carousel" aria-label="Featured stories">{''.join(slides)}<div class="carousel-controls" data-controls hidden><div class="carousel-dots">{''.join(dots)}</div><div class="carousel-actions"><span data-count>1 / {len(posts)}</span><button data-prev aria-label="Previous story">←</button><button data-toggle>Pause</button><button data-next aria-label="Next story">→</button></div></div><p class="sr-only" data-status aria-live="polite"></p></section>'''
body=f'''<main id="main" class="wrap"><section class="mast"><h1>{safe(h['headline'])}</h1><p>{safe(h['intro'])}</p></section>{feature}<section class="entries"><div class="section-head"><h2>From the collection</h2><p><a href="/cars/">Cars ↗</a> <span>/</span> <a href="/watches/">Watches ↗</a></p></div><div class="grid">{''.join(card(p) for p in posts)}</div></section><aside class="next"><h2>Coming up</h2><p>{safe(h.get('next_up',''))}</p><a href="{safe(CONTACT)}">Follow @redlinenrotors ↗</a></aside></main>'''
write(Path(''),'Home',body,h['intro'])
for cat,path,intro in [('Cars','cars','The GT-R I kept and the RS3 I sold. My first JDM car was an R33 GTST.'),('Watches','watches','What I wore, what I sold and what stayed in the box.')]:
 chosen=[p for p in posts if p.get('category')==cat]
 write(Path(path),cat,f'<main id="main" class="wrap listing"><h1>{cat}</h1><p class="deck">{intro}</p><div class="grid">'+''.join(card(p) for p in chosen)+'</div></main>')
for file,title in [('about','About'),('credits','My photographs')]:
 p=read(ROOT/f'content/{file}.md');write(Path(file),title,f'<main id="main" class="wrap about"><h1>{safe(p.get("title",title))}</h1><div class="prose">{p["body"]}</div></main>')
print('Built',len(posts),'entries;',[(p['slug'],p['words'],p['minutes']) for p in posts])

"""Страницы-превью библиотеки: dist/biblioteka/<артикул>.html с og:image (для ссылок в мессенджерах)
и картинки-превью dist/assets/lib/og/<артикул>.jpg 1200×630 на бежевой подложке.
Страница сразу перекидывает в biblioteka.html?art=<артикул>; поисковикам закрыта (noindex).
Запуск: python3 work/build_library.py (нужен Pillow). Данные — const DATA в dist/biblioteka.html."""
import json, os, re, html, urllib.parse
from PIL import Image, ImageChops

ROOT = os.path.join(os.path.dirname(__file__), '..', 'dist')
SITE = 'https://kultkartin.com'
BG = (243, 236, 225)  # #f3ece1, как подложка в крупном просмотре

src = open(os.path.join(ROOT, 'biblioteka.html'), encoding='utf-8').read()
DATA = json.loads(re.search(r'const DATA=(\[.*?\]);', src, re.S).group(1))
os.makedirs(os.path.join(ROOT, 'biblioteka'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'assets', 'lib', 'og'), exist_ok=True)

def og_image(art):
    dst = os.path.join(ROOT, 'assets', 'lib', 'og', art + '.jpg')
    if os.path.exists(dst):
        return
    im = Image.open(os.path.join(ROOT, 'assets', 'lib', art + '.webp')).convert('RGBA')
    k = min(1080 / im.width, 560 / im.height)  # вписываем, в том числе увеличивая маленькие миниатюры
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    paper = Image.new('RGB', im.size, (255, 255, 255))
    paper.paste(im, mask=im.getchannel('A'))
    art_on_bg = ImageChops.multiply(paper, Image.new('RGB', im.size, BG))  # белая бумага → цвет подложки
    canvas = Image.new('RGB', (1200, 630), BG)
    canvas.paste(art_on_bg, ((1200 - im.width) // 2, (630 - im.height) // 2))
    canvas.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)

PAGE = '''<!doctype html>
<html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="robots" content="noindex,follow">
<meta name="description" content="{desc}">
<link rel="canonical" href="{page}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="КУЛЬТКАРТИН">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{page}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{image}">
<link rel="icon" href="../assets/favicon.png" type="image/png">
<script>location.replace('../biblioteka.html?art={art}')</script>
<meta http-equiv="refresh" content="0;url=../biblioteka.html?art={art}">
</head><body style="background:#fbf6ee;font:16px Manrope,Arial,sans-serif"><a href="../biblioteka.html?art={art}">{title}</a></body></html>
'''

for w in DATA:
    art = w['id']
    og_image(art)
    title = f"Арт. {art} — {w['s']} · Библиотека картин КУЛЬТКАРТИН"
    desc = f"{w['t']}, серия «{w['s']}». Напечатаем и оформим в раму на заказ — назовите менеджеру артикул {art}."
    page = f"{SITE}/biblioteka/{art}.html"
    out = PAGE.format(title=html.escape(title), desc=html.escape(desc), page=page,
                      image=f"{SITE}/assets/lib/og/{art}.jpg", art=art)
    open(os.path.join(ROOT, 'biblioteka', art + '.html'), 'w', encoding='utf-8').write(out)
print('ok:', len(DATA), 'страниц-превью')

# Подборки: тип и тема — dist/biblioteka/<slug>.html, превью — три работы подборки рядом
KINDS = {'bot': 'Ботаника', 'fauna': 'Животные и птицы', 'sea': 'Море', 'arch': 'Архитектура и история',
         'kids': 'Детские', 'style': 'Мода и декор'}
TR = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sch','','y','','e','yu','ya']))
def slug(t):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', ''.join(TR.get(c, c) for c in t.lower()))).strip('-')

def collage(name, works):
    dst = os.path.join(ROOT, 'assets', 'lib', 'og', name + '.jpg')
    canvas = Image.new('RGB', (1200, 630), BG)
    picks = works[:3]
    slot = 1200 // len(picks)
    for i, w in enumerate(picks):
        im = Image.open(os.path.join(ROOT, 'assets', 'lib', w['id'] + '.webp')).convert('RGBA')
        k = min((slot - 60) / im.width, 520 / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        paper = Image.new('RGB', im.size, (255, 255, 255)); paper.paste(im, mask=im.getchannel('A'))
        canvas.paste(ImageChops.multiply(paper, Image.new('RGB', im.size, BG)),
                     (i * slot + (slot - im.width) // 2, (630 - im.height) // 2))
    canvas.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)

groups = [(k, None, label) for k, label in KINDS.items()]
seen = []
for w in DATA:
    if w['t'] not in seen:
        seen.append(w['t'])
groups += [(None, t, t) for t in seen]
seen_s = []
for w in DATA:
    if w['s'] not in seen_s:
        seen_s.append(w['s'])
groups += [('s', ser, ser) for ser in seen_s]  # серии: ссылка ?seriya=, ключ 's:<серия>', адрес s-<slug>
links = {}
for kind, tema, label in groups:
    works = [w for w in DATA if (w['s'] == tema if kind == 's' else w['m'] == kind if kind else w['t'] == tema)]
    # для превью — по одной работе из разных серий
    by_series = []
    for w in works:
        if w['s'] not in [x['s'] for x in by_series]:
            by_series.append(w)
    picks = (by_series + [w for w in works if w not in by_series])[:3]
    name = ('s-' if kind == 's' else '') + slug(label)
    collage(name, picks)
    target = ('../biblioteka.html?' + ('seriya=' + urllib.parse.quote(tema) if kind == 's' else
              'type=' + kind if kind else 'tema=' + urllib.parse.quote(tema)))
    n = len(works)
    title = f"{label} — Библиотека картин КУЛЬТКАРТИН"
    desc = f"{n} работ: печатаем и оформляем в раму на заказ. Назовите менеджеру артикул понравившейся."
    out = (PAGE.replace("../biblioteka.html?art={art}", target)
           .format(title=html.escape(title), desc=html.escape(desc), page=f"{SITE}/biblioteka/{name}.html",
                   image=f"{SITE}/assets/lib/og/{name}.jpg", art=''))
    open(os.path.join(ROOT, 'biblioteka', name + '.html'), 'w', encoding='utf-8').write(out)
    links[('s:' + tema) if kind == 's' else (kind or tema)] = name
json.dump(links, open(os.path.join(ROOT, 'biblioteka', 'links.json'), 'w', encoding='utf-8'), ensure_ascii=False)
# адреса подборок — в страницу библиотеки (кнопки «Поделиться»)
lib_path = os.path.join(ROOT, 'biblioteka.html')
lib = open(lib_path, encoding='utf-8').read()
lib = re.sub(r'const SHARE_PAGES=\{.*?\};', lambda m: 'const SHARE_PAGES=' + json.dumps(links, ensure_ascii=False, separators=(',', ':')) + ';', lib, count=1, flags=re.S)
open(lib_path, 'w', encoding='utf-8').write(lib)
print('ok:', len(groups), 'подборок')

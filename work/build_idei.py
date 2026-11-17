"""Раздел «Идеи для интерьера»: статьи-подборки под поисковые запросы (dist/idei/<slug>/index.html).

Страница = шаблон product.html (шапка, подвал, виджет связи, site.js) + статья:
первый экран на фото, цифры-подсказки, «образы» (визуализация + работы из кадра с ценами, как «Shop the look»
у Little Greene), советы со схемой, сетка каталога (site.js, живые цены из таблицы), вопросы, заявка.
Пока статья в черновике (draft=True) — noindex и не попадает в sitemap.
Запуск: python3 work/build_idei.py  (нужен Pillow для визуализаций)
"""
import hashlib, html, json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo as b

DIST = b.DIST
SITE = b.SITE
MOCK = os.path.join(os.path.dirname(b.ROOT), 'мокапы', 'для-GPT')
WA = 'https://wa.me/77071010814?text='

ARTICLES = [{
    'slug': 'kartiny-dlya-spalni',
    'draft': True,
    'title': 'Картины для спальни: как выбрать и повесить над кроватью | КУЛЬТКАРТИН',
    'desc': 'Какие картины повесить в спальне, какой размер выбрать над кроватью и как развесить пару или четыре работы. Подборка спокойных картин и постеров в раме с ценами.',
    'h1': 'Картины для спальни',
    'lead': 'Спокойные сюжеты, правильный размер над кроватью и аккуратная развеска — разбираем на примерах из нашего каталога.',
    'hero': 's7-krovat-dub/J1W1_02B5_4шт/3-расстановка.jpg',
    'wa': 'Здравствуйте! Хочу подобрать картины для спальни.',
    'facts': [('⅔', 'ширины кровати', 'столько должна занимать композиция над изголовьем'),
              ('20–30', 'см', 'от изголовья до нижнего края рамы'),
              ('5–8', 'см', 'между рамами в паре или группе')],
    'intro': ('Какие сюжеты подходят для спальни', [
        'Лучше всего в спальне работают спокойные сюжеты с мягкой палитрой: ботанические иллюстрации, гербарии, туманные пейзажи, тонкая графика. Они не перегружают взгляд перед сном и хорошо сочетаются с текстилем — льном, букле, бархатом.',
        'Яркие абстракции, динамичные сцены и контрастные фотографии оставьте для гостиной и кабинета. Если хочется акцента, выберите одну работу с цветом и поддержите её нейтральной парой.']),
    'looks': [
        ('s5-krovat-temnaya/C2K1_02B4_2шт/3-расстановка.jpg', 'Ботаника на тёмном дереве',
         'Сиреневые цветы на мягком зелёном фоне и золотые рамы с широким паспарту — светлое пятно на тёмной стене. Пара повешена вертикально над серединой изголовья.', [87, 88]),
        ('s5-krovat-temnaya/C2P_34B5_2шт/3-расстановка.jpg', 'Пейзажи в сепии',
         'Тёплые монохромные фотографии повторяют оттенки дерева и постельного белья. Спокойный вариант, который не надоест.', [85, 86]),
        ('s7-krovat-dub/R1_34B4_4шт/3-расстановка.jpg', 'Акварель в светлом дубе',
         'Четыре квадратные работы в тонких рамах, повешенные квадратом, держат широкую стену над кроватью 180 см. Мягкая палитра не спорит с текстилем.', [56, 57, 58, 59]),
    ],
    'size': ('Какой размер выбрать над кроватью', [
        'Ориентируйтесь на ширину изголовья: композиция должна занимать примерно две трети её ширины. Для кровати 160 см это около 100–110 см, для кровати 180 см — около 120 см.',
        'На практике это две вертикальные работы размера X (каждая 54,5 × 64,5 см с рамой) или четыре квадратные размера C (около 48 × 48 см), повешенные квадратом. Одна картина над широкой кроватью смотрится мелко — если хочется одну, берите самый крупный формат.']),
    'hang': ('Как повесить картины над кроватью', [
        'Нижний край рамы — на 20–30 см выше изголовья: так картину не заденешь головой, а композиция не «оторвётся» от кровати.',
        'Расстояние между рамами — 5–8 см, одинаковое по вертикали и горизонтали. Центр композиции совмещайте с центром кровати, а не стены.',
        'Если над кроватью уже есть бра, развеску лучше сделать вертикальной парой — работы встанут между светильниками.']),
    'works': [87, 85, 56, 9, 70, 30, 99, 114, 116, 66, 135, 86],
    'faq': [
        ('Какую картину повесить в спальне?', 'Спокойную по цвету и сюжету: ботаническую иллюстрацию, туманный пейзаж, мягкую графику. Яркие и динамичные работы лучше оставить для гостиной.'),
        ('Какого размера должна быть картина над кроватью?', 'Композиция — примерно две трети ширины изголовья: для кровати 160 см около 100–110 см. Это две вертикальные работы размера X или четыре квадратные размера C.'),
        ('На какой высоте вешать картину над кроватью?', 'Нижний край рамы — на 20–30 см выше изголовья, расстояние между рамами в группе — 5–8 см.'),
        ('Можно ли заказать картину в другом размере?', 'Да. Любую работу из каталога можно сделать в другом размере, раме и с другим паспарту — менеджер подскажет варианты и цену.'),
        ('Можно ли подобрать картину под мою спальню?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
}]

CSS = """<style>
.idea-hero{position:relative;min-height:min(78vh,720px);display:grid;align-items:end;color:#fff;overflow:hidden;background:#2a1f1b}
.idea-hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.idea-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,12,10,.72) 0%,rgba(20,12,10,.35) 45%,rgba(20,12,10,0) 70%)}
.idea-hero-in{position:relative;z-index:1;width:min(1180px,100%);margin:0 auto;padding:0 20px clamp(36px,6vw,72px)}
.idea-crumbs{font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.8;margin-bottom:18px}.idea-crumbs a{text-decoration:underline}
.idea-hero h1{font:500 clamp(46px,7vw,96px)/.95 var(--serif);margin:0 0 18px;max-width:9em}
.idea-hero p{max-width:520px;font-size:clamp(16px,1.5vw,19px);line-height:1.55;margin:0 0 26px;opacity:.92}
.btn-wa{display:inline-block;background:var(--dark);color:#fff;padding:16px 28px;font:600 12.5px/1 var(--sans);letter-spacing:.12em;text-transform:uppercase}
.btn-line{display:inline-block;border:1px solid currentColor;padding:15px 26px;font:600 12.5px/1 var(--sans);letter-spacing:.12em;text-transform:uppercase}
.idea-hero .btn-wa{background:#f7eddd;color:var(--dark)}
.idea-hero .btns{display:flex;gap:10px;flex-wrap:wrap}
.idea-wrap{width:min(1180px,100%);margin:0 auto;padding:0 20px}
.idea-facts{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--line)}
.idea-facts div{padding:clamp(22px,3vw,34px) clamp(14px,2vw,28px);border-right:1px solid var(--line)}.idea-facts div:last-child{border-right:0}
.idea-facts b{display:block;font:500 clamp(40px,5vw,64px)/1 var(--serif);color:var(--dark);font-variant-numeric:lining-nums}
.idea-facts b small{font-size:.4em;margin-left:6px;color:#6f6762}
.idea-facts span{display:block;margin-top:8px;font-size:14px;color:#5d534b;max-width:22ch;line-height:1.45}
.idea-text{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:clamp(24px,5vw,80px);padding:clamp(48px,7vw,96px) 0;border-bottom:1px solid var(--line)}
.idea-text h2,.idea-looks h2,.idea-faq h2,.idea-pick h2{font:500 clamp(32px,4vw,52px)/1.02 var(--serif);margin:0}
.idea-text p{font-size:17px;line-height:1.75;margin:0 0 14px;color:#2c2725;max-width:62ch}
.idea-kicker{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:#8a5a4a;font-weight:600;margin-bottom:12px}
.idea-looks{padding:clamp(48px,7vw,96px) 0;display:grid;gap:clamp(40px,6vw,88px);border-bottom:1px solid var(--line)}
.look{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:clamp(24px,4vw,64px);align-items:center}
.look:nth-child(even of .look){direction:rtl}.look>*{direction:ltr}
.look-img img{width:100%;aspect-ratio:4/5;object-fit:cover;display:block}
.look h3{font:500 clamp(28px,3vw,40px)/1.05 var(--serif);margin:0 0 12px}
.look p{font-size:16px;line-height:1.65;color:#4f4743;margin:0 0 22px;max-width:46ch}
.look-items{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:24px}
.look-items a{display:grid;grid-template-columns:76px minmax(0,1fr);gap:14px;align-items:center;padding:10px;background:#fff;border:1px solid var(--line)}
.look-items img{width:76px;height:76px;object-fit:contain;background:#f4f1ee}
.look-items b{display:block;font:500 18px/1.15 var(--serif)}.look-items span{font-size:13px;color:#6f6762}
.idea-how{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,5vw,80px);padding:clamp(48px,7vw,96px) 0;border-bottom:1px solid var(--line);align-items:start}
.idea-how h2{font:500 clamp(28px,3.2vw,40px)/1.05 var(--serif);margin:0 0 14px}
.idea-how p{font-size:16.5px;line-height:1.7;margin:0 0 12px;color:#2c2725}
.idea-how .block+.block{margin-top:36px}
.idea-scheme{background:#fff;border:1px solid var(--line);padding:clamp(18px,3vw,32px);position:sticky;top:96px}
.idea-scheme svg{width:100%;height:auto;display:block}.idea-scheme figcaption{font-size:13px;color:#6f6762;margin-top:10px}
.idea-pick{padding:clamp(48px,7vw,96px) 0 0}
.idea-pick-head{display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap;margin-bottom:28px}
.idea-pick-head p{margin:10px 0 0;color:#6f6762;max-width:520px}
.idea-pick-head a{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;border-bottom:1px solid}
.idea-pick .catalog{padding:0;max-width:none}
.idea-faq{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:clamp(24px,5vw,80px);padding:clamp(48px,7vw,96px) 0}
.idea-faq details{border-top:1px solid var(--line);padding:22px 0}.idea-faq details:last-child{border-bottom:1px solid var(--line)}
.idea-faq summary{cursor:pointer;font:500 clamp(20px,2vw,26px)/1.25 var(--serif);list-style:none;display:flex;justify-content:space-between;gap:20px}
.idea-faq summary::after{content:"+";font-family:var(--sans);font-weight:300;font-size:26px;line-height:1}.idea-faq details[open] summary::after{content:"−"}
.idea-faq summary::-webkit-details-marker{display:none}
.idea-faq p{margin:12px 0 0;font-size:16.5px;line-height:1.7;color:#4f4743;max-width:62ch}
.idea-cta{background:var(--dark);color:#f3e8e8;text-align:center;padding:clamp(48px,7vw,88px) 20px}
.idea-cta h2{font:500 clamp(32px,4vw,52px)/1.05 var(--serif);margin:0 0 14px;color:#fff}
.idea-cta p{max-width:560px;margin:0 auto 26px;line-height:1.6;opacity:.85}
.idea-cta .btn-wa{background:#f7eddd;color:var(--dark)}
@media(max-width:900px){.idea-text,.idea-how,.idea-faq,.look{grid-template-columns:1fr}.look{direction:ltr!important}.idea-scheme{position:static}.idea-facts{grid-template-columns:1fr}.idea-facts div{border-right:0;border-bottom:1px solid var(--line)}.idea-facts div:last-child{border-bottom:0}}
@media(max-width:520px){.look-items{grid-template-columns:1fr}.idea-hero{min-height:82vh}}
</style>"""

SCHEME = """<svg viewBox="0 0 420 300" role="img" aria-label="Схема: композиция над кроватью 160 см шириной около 105 см, нижний край на 20–30 см выше изголовья">
<g fill="none" stroke="#2c2725" stroke-width="1.2">
<rect x="160" y="40" width="48" height="58" fill="#f4efe8"/><rect x="212" y="40" width="48" height="58" fill="#f4efe8"/>
<rect x="168" y="50" width="32" height="38" fill="#e3ddd2" stroke-width=".8"/><rect x="220" y="50" width="32" height="38" fill="#e3ddd2" stroke-width=".8"/>
<rect x="90" y="140" width="240" height="46" fill="#ebe4da"/><rect x="70" y="186" width="280" height="64" fill="#f7f3ee"/>
<line x1="60" y1="262" x2="360" y2="262" stroke="#b7aca2"/></g>
<g stroke="#8a5a4a" stroke-width="1" fill="none"><path d="M160 24h100M160 20v8M260 20v8"/><path d="M372 98v42M368 98h8M368 140h8"/><path d="M70 276h280M70 272v8M350 272v8"/></g>
<g font-family="Manrope,Arial,sans-serif" font-size="12" fill="#8a5a4a" text-anchor="middle">
<text x="210" y="16">≈ 105 см (⅔ ширины)</text><text x="70" y="294" text-anchor="start">кровать 160 см</text>
<text x="384" y="124" text-anchor="start" transform="rotate(90 384 124)">20–30 см</text></g></svg>"""


def img_out(slug, src, name, size):
    from PIL import Image
    out = os.path.join(DIST, 'idei', slug, 'img')
    os.makedirs(out, exist_ok=True)
    im = Image.open(os.path.join(MOCK, src)).convert('RGB')
    im.thumbnail(size)
    name = name.replace('.webp', '-' + hashlib.md5(src.encode()).hexdigest()[:6] + '.webp')  # новое фото — новое имя, без старого кеша
    im.save(os.path.join(out, name), 'WEBP', quality=82)
    return f'idei/{slug}/img/{name}'


def money_pair(w):
    pre = 'от ' if w['from'] else ''
    return f'{pre}{b.money(w["kzt"])} ₸', f'{pre}{b.money(w["rub"])} ₽'


def page(template, a, works):
    e = lambda s: html.escape(s or '', quote=True)
    url = f'{SITE}/idei/{a["slug"]}/'
    by = {w['id']: w for w in works}
    picked = [by[i] for i in a['works'] if i in by]
    wa = WA + urllib.parse.quote(a['wa'])
    hero = img_out(a['slug'], a['hero'], 'hero.webp', (2000, 1600))
    t = template.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="/">', 1)
    t = re.sub(r'<title>.*?</title>', f'<title>{e(a["title"])}</title>', t, count=1, flags=re.S)
    for attr, value in (('name="description"', a['desc']), ('property="og:title"', a['title']), ('property="og:description"', a['desc']),
                        ('property="og:url"', url), ('property="og:image"', SITE + '/' + hero), ('name="twitter:title"', a['title']),
                        ('name="twitter:description"', a['desc']), ('name="twitter:image"', SITE + '/' + hero)):
        t = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + e(value) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    if a['draft']:
        t = t.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<meta name="robots" content="noindex">', 1)
    t = t.replace("<script>document.documentElement.classList.add('kk-wait')</script>\n", '', 1)

    looks = ''
    for n, (src, title, text, ids) in enumerate(a['looks'], 1):
        img = img_out(a['slug'], src, f'look-{n}.webp', (900, 1125))
        items = ''.join(
            f'<a href="kartiny/{w["id"]}.html"><img src="{e(w["thumb"])}" alt="{e(w["name"])}" loading="lazy">'
            f'<span><b>{e(w["name"])}</b><span class="lp" data-kzt="{e(money_pair(w)[0])}" data-rub="{e(money_pair(w)[1])}">{e(money_pair(w)[0])}</span></span></a>'
            for w in (by[i] for i in ids if i in by))
        ask = WA + urllib.parse.quote(f'Здравствуйте! Хочу так же, как в образе «{title}» из статьи «{a["h1"]}».')
        looks += (f'<article class="look"><div class="look-img"><img src="{img}" alt="{e(title)} — {e(a["h1"].lower())}" loading="lazy"></div>'
                  f'<div><div class="idea-kicker">Образ {n}</div><h3>{e(title)}</h3><p>{e(text)}</p><div class="look-items">{items}</div>'
                  f'<a class="btn-line" href="{ask}" target="_blank" rel="noopener">Хочу так же</a></div></article>')

    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Article', 'headline': a['h1'], 'description': a['desc'], 'url': url, 'inLanguage': 'ru',
         'image': [SITE + '/' + hero], 'publisher': {'@id': SITE + '/#store'}},
        {'@type': 'ItemList', 'name': f'{a["h1"]} — подборка', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': b.product_url(w), 'name': w['name']} for i, w in enumerate(picked)]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}} for q, ans in a['faq']]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Идеи для интерьера', 'item': SITE + '/idei/'},
            {'@type': 'ListItem', 'position': 3, 'name': a['h1'], 'item': url}]}]}
    t = t.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n' + CSS + '\n</head>', 1)

    paras = lambda ps: ''.join(f'<p>{e(p)}</p>' for p in ps)
    facts = ''.join(f'<div><b>{e(n)}<small>{e(u)}</small></b><span>{e(s)}</span></div>' for n, u, s in a['facts'])
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(ans)}</p></details>' for q, ans in a['faq'])
    main = (f'<main>'
            f'<section class="idea-hero"><img src="{hero}" alt="{e(a["h1"])}: четыре графичных гербария над кроватью" fetchpriority="high">'
            f'<div class="idea-hero-in"><div class="idea-crumbs"><a href="index.html">Главная</a> · Идеи для интерьера</div>'
            f'<h1>{e(a["h1"])}</h1><p>{e(a["lead"])}</p><div class="btns"><a class="btn-wa" href="#podborka">Смотреть подборку</a>'
            f'<a class="btn-line" href="{wa}" target="_blank" rel="noopener">Подобрать под мою спальню</a></div></div></section>'
            f'<div class="idea-wrap"><div class="idea-facts">{facts}</div>'
            f'<section class="idea-text"><div><div class="idea-kicker">С чего начать</div><h2>{e(a["intro"][0])}</h2></div><div>{paras(a["intro"][1])}</div></section>'
            f'<section class="idea-looks"><div><div class="idea-kicker">Образы</div><h2>Три спальни — три настроения</h2></div>{looks}</section>'
            f'<section class="idea-how"><div><div class="block"><h2>{e(a["size"][0])}</h2>{paras(a["size"][1])}</div>'
            f'<div class="block"><h2>{e(a["hang"][0])}</h2>{paras(a["hang"][1])}</div></div>'
            f'<figure class="idea-scheme">{SCHEME}<figcaption>Пример для кровати 160 см: пара работ размера X, промежуток 5–8 см.</figcaption></figure></section>'
            f'<section class="idea-pick" id="podborka"><div class="idea-pick-head"><div><div class="idea-kicker">Подборка</div><h2>Подойдут для спальни</h2>'
            f'<p>Спокойные тона, ботаника, пейзажи и мягкая графика. Каждую работу можно заказать в другом размере и оформлении.</p></div>'
            f'<a href="index.html#catalog">Весь каталог</a></div>'
            f'<div class="catalog" id="catalog"><div class="products" id="products">\n{b.catalog_cards(picked)}\n</div></div></section>'
            f'<section class="idea-faq"><div><div class="idea-kicker">Вопросы</div><h2>Частые вопросы</h2></div><div>{faq}</div></section></div>'
            f'<section class="idea-cta"><h2>Подберём картины под вашу спальню</h2><p>Пришлите фото стены — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.</p>'
            f'<a class="btn-wa" href="{wa}" target="_blank" rel="noopener">Написать в WhatsApp</a></section></main>')
    t = re.sub(r'<main>.*?</main>', lambda m: main, t, count=1, flags=re.S)
    ids = json.dumps(a['works'])
    page_js = ('<script>{const IDS=' + ids + ';catalogWorks=()=>IDS.map(id=>works.find(w=>w.id===id)).filter(Boolean);render();'
               'const cur=()=>{try{return new URLSearchParams(location.search).get("cur")||localStorage.getItem("kk-currency")||"KZT"}catch(e){return"KZT"}};'
               'const sync=()=>{const r=cur()==="RUB";document.querySelectorAll(".lp").forEach(el=>el.textContent=r?el.dataset.rub:el.dataset.kzt)};'
               'sync();document.addEventListener("click",e=>{if(e.target.closest("[data-currency]"))setTimeout(sync,0)})}</script>')
    t = re.sub(r'<script>\s*const productApp=.*?</script>', lambda m: page_js, t, count=1, flags=re.S)
    return t


def main():
    works, _ = b.load()
    template = open(os.path.join(DIST, 'product.html'), encoding='utf-8').read()
    for a in ARTICLES:
        out = os.path.join(DIST, 'idei', a['slug'])
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(os.path.join(out, 'img')) if os.path.isdir(os.path.join(out, 'img')) else []:
            os.remove(os.path.join(out, 'img', f))
        open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page(template, a, works))
        print('ok', a['slug'])


if __name__ == '__main__':
    main()

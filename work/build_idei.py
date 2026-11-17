"""Раздел «Идеи для интерьера»: статьи-подборки под поисковые запросы (dist/idei/<slug>/index.html).

Страница = шаблон product.html (шапка, подвал, виджет связи, site.js) + текст статьи, визуализации
и карусель работ из каталога: id работ задаются в ARTICLES, цены и фото site.js берёт из Google Таблицы.
Пока статья в черновике (draft=True) — noindex и не попадает в sitemap.
Запуск: python3 work/build_idei.py  (нужен Pillow для визуализаций)
"""
import html, json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_seo as b

DIST = b.DIST
SITE = b.SITE
MOCK = os.path.join(os.path.dirname(b.ROOT), 'мокапы', 'для-GPT')

ARTICLES = [{
    'slug': 'kartiny-dlya-spalni',
    'draft': True,
    'title': 'Картины для спальни: как выбрать и повесить над кроватью | КУЛЬТКАРТИН',
    'desc': 'Какие картины повесить в спальне, какой размер выбрать над кроватью и как развесить пару или четыре работы. Подборка спокойных картин и постеров в раме с ценами.',
    'h1': 'Картины для спальни',
    'lead': 'Спальня — единственная комната, где картина работает на отдых, а не на впечатление. Рассказываем, какие сюжеты выбрать, какой нужен размер над кроватью и как повесить работы, — и показываем на примерах из нашего каталога.',
    'works': [9, 70, 30, 99, 56, 85, 86, 114, 116, 66, 135, 89],
    'visuals': [
        ('s5-krovat-temnaya/C2K1_02B4_2шт/3-расстановка.jpg', 'Тёмная спальня: пара ботанических иллюстраций в золотых рамах с паспарту'),
        ('s7-krovat-dub/J1W1_02B5_4шт/3-расстановка.jpg', 'Спальня в светлом дубе: четыре графичных гербария в квадратных рамах'),
        ('s5-krovat-temnaya/C2P_34B5_2шт/3-расстановка.jpg', 'Пейзажи в сепии — тёплый и спокойный вариант для тёмной стены'),
        ('s7-krovat-dub/R1_34B4_4шт/3-расстановка.jpg', 'Акварельные пейзажи: мягкая палитра, которая не спорит с текстилем'),
    ],
    'sections': [
        ('Какие сюжеты подходят для спальни', [
            'Лучше всего в спальне работают спокойные сюжеты с мягкой палитрой: ботанические иллюстрации, гербарии, туманные пейзажи, тонкая графика. Они не перегружают взгляд перед сном и хорошо сочетаются с текстилем — льном, букле, бархатом.',
            'Яркие абстракции, динамичные сцены и контрастные фотографии оставьте для гостиной и кабинета. Если хочется акцента, выберите одну работу с цветом и поддержите её нейтральной парой.',
        ]),
        ('Какой размер выбрать над кроватью', [
            'Ориентируйтесь на ширину изголовья: композиция над кроватью должна занимать примерно две трети её ширины. Для кровати 160 см это около 100–110 см, для кровати 180 см — около 120 см.',
            'На практике это две вертикальные работы размера X (каждая 54,5 × 64,5 см с рамой) или четыре квадратные размера C (около 48 × 48 см), повешенные квадратом. Одна картина над широкой кроватью смотрится мелко — если хочется одну, берите самый крупный формат.',
        ]),
        ('Как повесить картины над кроватью', [
            'Нижний край рамы — на 20–30 см выше изголовья: так картину не заденешь головой, а композиция не «оторвётся» от кровати.',
            'Расстояние между рамами в паре или группе — 5–8 см, одинаковое по вертикали и горизонтали. Центр композиции совмещайте с центром кровати, а не стены.',
            'Если над кроватью уже есть бра, развеску лучше сделать вертикальной парой — работы встанут между светильниками.',
        ]),
    ],
    'faq': [
        ('Какую картину повесить в спальне?', 'Спокойную по цвету и сюжету: ботаническую иллюстрацию, туманный пейзаж, мягкую графику. Яркие и динамичные работы лучше оставить для гостиной.'),
        ('Какого размера должна быть картина над кроватью?', 'Композиция — примерно две трети ширины изголовья: для кровати 160 см около 100–110 см. Это две вертикальные работы размера X или четыре квадратные размера C.'),
        ('На какой высоте вешать картину над кроватью?', 'Нижний край рамы — на 20–30 см выше изголовья, расстояние между рамами в группе — 5–8 см.'),
        ('Можно ли подобрать картину под мою спальню?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
}]

CSS = """<style>
.idea{max-width:1180px;margin:0 auto;padding:clamp(28px,5vw,64px) 20px 0}
.idea-crumbs{font-size:13px;color:#7a706a;margin-bottom:18px}.idea-crumbs a{color:inherit;text-decoration:underline}
.idea h1{font:500 clamp(40px,6vw,76px)/1 var(--serif);margin:0 0 18px;letter-spacing:-.01em}
.idea .lead{max-width:720px;font-size:clamp(16px,1.5vw,19px);line-height:1.6;color:#4f4743;margin:0}
.idea-hero{display:grid;grid-template-columns:1.25fr 1fr;gap:clamp(20px,3vw,40px);align-items:end;margin-bottom:clamp(28px,4vw,48px)}
.idea-hero .btn-wa{justify-self:start}
.idea-vis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(10px,1.5vw,18px);margin:0 0 clamp(36px,5vw,64px)}
.idea-vis figure{margin:0}.idea-vis img{width:100%;aspect-ratio:4/5;object-fit:cover;display:block}
.idea-vis figcaption{font-size:13px;color:#7a706a;margin-top:8px;line-height:1.45}
.idea-body{display:grid;grid-template-columns:minmax(0,720px);justify-content:center;gap:clamp(26px,4vw,44px)}
.idea-body h2{font:500 clamp(28px,3.2vw,40px)/1.1 var(--serif);margin:0 0 12px}
.idea-body p{font-size:17px;line-height:1.7;margin:0 0 12px;color:#2c2725}
.idea .btn-wa{display:inline-block;background:var(--dark);color:#fff;padding:15px 26px;font:600 13px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase}
.idea-pick{margin-top:clamp(40px,6vw,80px)}
.idea-pick .title{margin-bottom:10px}
.idea-pick .sub{text-align:center;color:#6f6762;margin:0 auto 28px;max-width:560px}
.idea-pick #products{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(220px,1fr);grid-template-columns:none;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:12px;gap:16px}
.idea-pick #products .product{scroll-snap-align:start}
.idea-cta{background:var(--dark);color:#f3e8e8;text-align:center;padding:clamp(40px,6vw,72px) 20px;margin-top:clamp(40px,6vw,80px)}
.idea-cta h2{font:500 clamp(28px,3.6vw,44px)/1.1 var(--serif);margin:0 0 12px;color:#fff}
.idea-cta p{max-width:560px;margin:0 auto 22px;line-height:1.6;opacity:.85}
.idea-cta .btn-wa{background:#f3e8e8;color:var(--dark)}
.idea-faq{max-width:720px;margin:clamp(40px,6vw,72px) auto 0;padding:0 20px}
.idea-faq h2{font:500 clamp(28px,3.2vw,40px)/1.1 var(--serif);margin:0 0 14px}
.idea-faq details{border-top:1px solid var(--line);padding:16px 0}.idea-faq summary{cursor:pointer;font-weight:600}
.idea-faq p{margin:10px 0 0;line-height:1.65;color:#4f4743}
@media(max-width:850px){.idea-hero{grid-template-columns:1fr}.idea-vis{grid-template-columns:1fr 1fr}.idea-pick #products{grid-auto-columns:72%}}
@media(max-width:520px){.idea-vis{grid-template-columns:1fr}}
</style>"""


def visuals(a):
    from PIL import Image
    out = os.path.join(DIST, 'idei', a['slug'], 'img')
    os.makedirs(out, exist_ok=True)
    res = []
    for i, (src, cap) in enumerate(a['visuals'], 1):
        im = Image.open(os.path.join(MOCK, src)).convert('RGB')
        im.thumbnail((1200, 1500))
        name = f'{a["slug"]}-{i}.webp'
        im.save(os.path.join(out, name), 'WEBP', quality=82)
        res.append((f'img/{name}', cap))
    return res


def page(template, a, works):
    e = lambda s: html.escape(s or '', quote=True)
    url = f'{SITE}/idei/{a["slug"]}/'
    by = {w['id']: w for w in works}
    picked = [by[i] for i in a['works'] if i in by]
    vis = visuals(a)
    t = template.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="/">', 1)
    t = re.sub(r'<title>.*?</title>', f'<title>{e(a["title"])}</title>', t, count=1, flags=re.S)
    for attr, value in (('name="description"', a['desc']), ('property="og:title"', a['title']), ('property="og:description"', a['desc']),
                        ('property="og:url"', url), ('name="twitter:title"', a['title']), ('name="twitter:description"', a['desc'])):
        t = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + e(value) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    if a['draft']:
        t = t.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<meta name="robots" content="noindex">', 1)
    t = t.replace("<script>document.documentElement.classList.add('kk-wait')</script>\n", '', 1)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Article', 'headline': a['h1'], 'description': a['desc'], 'url': url, 'inLanguage': 'ru',
         'image': [f'{url}{v}' for v, _ in vis], 'publisher': {'@id': SITE + '/#store'}},
        {'@type': 'ItemList', 'name': f'{a["h1"]} — подборка', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': b.product_url(w), 'name': w['name']} for i, w in enumerate(picked)]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}} for q, ans in a['faq']]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Идеи для интерьера', 'item': SITE + '/idei/'},
            {'@type': 'ListItem', 'position': 3, 'name': a['h1'], 'item': url}]}]}
    t = t.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n' + CSS + '\n</head>', 1)
    wa = 'https://wa.me/77071010814?text=' + urllib.parse.quote('Здравствуйте! Хочу подобрать картины для спальни.')
    vis_html = ''.join(f'<figure><img src="idei/{a["slug"]}/{src}" alt="{e(cap)}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>' for src, cap in vis)
    secs = ''.join(f'<section><h2>{e(h)}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in ps) + '</section>' for h, ps in a['sections'])
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(ans)}</p></details>' for q, ans in a['faq'])
    main = (f'<main><article class="idea"><div class="idea-crumbs"><a href="index.html">Главная</a> · Идеи для интерьера</div>'
            f'<div class="idea-hero"><div><h1>{e(a["h1"])}</h1><p class="lead">{e(a["lead"])}</p></div>'
            f'<a class="btn-wa" href="{wa}" target="_blank" rel="noopener">Подобрать под мою спальню</a></div>'
            f'<div class="idea-vis">{vis_html}</div>'
            f'<div class="idea-body">{secs}</div></article>'
            f'<section class="catalog idea-pick" id="catalog"><h2 class="title">Подойдут для спальни</h2>'
            f'<p class="sub">Спокойные тона, ботаника, пейзажи и мягкая графика. Каждую работу можно заказать в другом размере и оформлении.</p>'
            f'<div class="products" id="products">\n{b.catalog_cards(picked)}\n</div></section>'
            f'<section class="idea-faq"><h2>Частые вопросы</h2>{faq}</section>'
            f'<section class="idea-cta"><h2>Подберём картины под вашу спальню</h2><p>Пришлите фото стены — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.</p>'
            f'<a class="btn-wa" href="{wa}" target="_blank" rel="noopener">Написать в WhatsApp</a></section></main>')
    t = re.sub(r'<main>.*?</main>', lambda m: main, t, count=1, flags=re.S)
    # вместо скрипта карточки товара — своя выдача каталога: только работы статьи, в заданном порядке
    ids = json.dumps(a['works'])
    t = re.sub(r'<script>\s*const productApp=.*?</script>',
               f'<script>{{const IDS={ids};catalogWorks=()=>IDS.map(id=>works.find(w=>w.id===id)).filter(Boolean);render()}}</script>', t, count=1, flags=re.S)
    return t


def main():
    works, _ = b.load()
    template = open(os.path.join(DIST, 'product.html'), encoding='utf-8').read()
    for a in ARTICLES:
        out = os.path.join(DIST, 'idei', a['slug'])
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page(template, a, works))
        print('ok', a['slug'])


if __name__ == '__main__':
    main()

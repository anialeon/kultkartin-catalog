# -*- coding: utf-8 -*-
"""SEO-сборка КУЛЬТКАРТИН: берёт каталог из Google Таблицы и обновляет
dist/index.html (JSON-LD и статичные карточки каталога), dist/sitemap.xml,
dist/robots.txt и dist/llms.txt. Запускать перед каждой выкладкой:

    python3 work/build_seo.py
"""
import datetime, html, json, os, re, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
SITE = 'https://catalog.kultkartin.com'
SHEET_ID = '1ApEOrnflSSqiTu9kDIQwuAk9LsWOL5Syw9VfSZWJh80'
LOGO = 'https://m-files.cdnvideo.ru/lpfile/4/d/a/4da194dee1cc6ff27866dae3de89ba90.png'
OG_IMAGE = 'https://m-files.cdn1.cc/lpfile/a/d/a/ada8b3fd3760b96661d479a01bc9d5b2.jpg'
KZT_PER_RUB = 5.33
SOCIALS = [
    'https://kultkartin.com',
    'https://www.instagram.com/kultkartin/',
    'https://www.threads.com/@kultkartin',
    'https://www.youtube.com/@kultkartin',
    'https://t.me/kultkartin',
    'https://2gis.kz/astana/firm/70000001063937568/tab/info',
]


def key(label):
    return re.sub(r'\s+', ' ', str(label or '').replace('*', '')).strip().lower()


def sheet(name):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&headers=1&sheet=' + urllib.parse.quote(name)
    raw = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    table = json.loads(re.search(r'setResponse\((.*)\);?\s*$', raw, re.S).group(1))['table']
    keys = [key(c['label']) for c in table['cols']]
    return [{k: (c or {}).get('v') for k, c in zip(keys, row['c']) if k} for row in table.get('rows') or []]


def text(r, *labels):
    for label in labels:
        v = r.get(key(label))
        if v not in (None, ''):
            return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()
    return ''


def number(r, *labels):
    try:
        return int(float(re.sub(r'[^\d.]', '', text(r, *labels)) or 0))
    except ValueError:
        return 0


def yes(v):
    return str(v).strip().lower() in ('да', 'yes', 'true', '1')


def money(v):
    return f'{v:,}'.replace(',', ' ')


def drive_image(url, width, fmt='rw'):
    m = re.search(r'drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:export=\w+&)?id=|thumbnail\?id=)([\w-]{20,})|googleusercontent\.com/d/([\w-]{20,})', url or '')
    return f'https://lh3.googleusercontent.com/d/{m.group(1) or m.group(2)}=w{width}-{fmt}' if m else url


def first_link(value):
    return next((u for u in re.split(r'[\s,;]+', value or '') if u.startswith('http')), '')


def format_kind(value):
    return 'square' if 'квадрат' in (value or '').lower() else 'rect'


def frame_key(value):
    value = str(value or '').strip()
    return value.zfill(2) if value.isdigit() else value


def work_sizes(w, sizes, frames):
    if re.search(r'по запросу|нет', w['sizes_allowed'] or '', re.I):
        return []
    kind = format_kind(w['format'])
    allowed = re.findall(r'[A-Z]', (w['sizes_allowed'] or '').upper())
    frame = frames.get(frame_key(w['frame']), {})
    result = []
    for s in sizes:
        if s['format'] and s['format'] != kind or allowed and s['code'] not in allowed:
            continue
        dims = frame.get(s['code']) or s['image']
        if dims and '×' not in dims:
            dims = f'{dims} × {dims}'
        elif dims and 'вертик' in (w['format'] or '').lower():
            a, _, b = dims.partition('×')
            dims = f'{b.strip()} × {a.strip()}'
        rub = s['rub'] or round(s['kzt'] / KZT_PER_RUB / 100) * 100
        kzt = s['kzt'] or round(s['rub'] * KZT_PER_RUB / 100) * 100
        result.append({**s, 'dims': f'{dims} см' if dims else '', 'rub': rub, 'kzt': kzt})
    return result


def load():
    sizes = []
    rows = sheet('Размеры')
    if rows and 'размер' in rows[0] and ('цена, ₸' in rows[0] or 'цена, ₽' in rows[0]):
        for r in rows:
            s = {'code': text(r, 'Размер').upper(), 'format': format_kind(text(r, 'Формат')) if text(r, 'Формат') else ('square' if text(r, 'Размер').upper() in 'JCRNY' else 'rect'),
                 'image': re.sub(r'\s*см$', '', text(r, 'Изображение, см', 'Габарит')),
                 'rub': number(r, 'Цена, ₽', 'Цена ₽'), 'kzt': number(r, 'Цена, ₸', 'Цена ₸')}
            if s['code']:
                sizes.append(s)
    frames = {}
    rows = sheet('Рамы')
    if rows and 'рама' in rows[0]:
        for r in rows:
            fid = frame_key(text(r, 'Рама'))
            if fid:
                frames[fid] = {k.upper(): str(v).strip().replace('.', ',') for k, v in r.items() if len(k) == 1 and v not in (None, '')}
    works = []
    try:
        tabs = [text(r, 'Вкладка') for r in sheet('Вкладки каталога')]
        tabs = [t for t in tabs if t] or ['Живопись', 'Наличие', 'Популярные', 'Новое']
    except Exception:
        tabs = ['Живопись', 'Наличие', 'Популярные', 'Новое']
    rows_all = []
    for ti, tab in enumerate(tabs):
        try:
            rows_all += [(ti, i, r) for i, r in enumerate(sheet(tab))]
        except Exception:
            continue
    for ti, i, r in rows_all:
        fmt = text(r, 'Формат')
        w = {
            'id': number(r, 'ID') or 1000 + ti * 1000 + i,
            'order': number(r, 'Порядок на сайте', 'Порядок') or 1000 + ti * 1000 + i,
            'tab': ti,
            'name': text(r, 'Название'),
            'img': drive_image(first_link(text(r, 'URL изображения')), 1200),
            'og': drive_image(first_link(text(r, 'URL изображения')), 1200, 'rj'),
            'thumb': drive_image(first_link(text(r, 'URL изображения')), 560),
            'images': [drive_image(u, 1200) for u in re.split(r'[\s,;]+', text(r, 'URL изображения')) if u.startswith('http')],
            'format': fmt,
            'frame': text(r, 'Рама'),
            'sizes_allowed': text(r, 'Размеры в продаже'),
            'material': text(r, 'Материал'),
            'meta_size': fmt.lower() if fmt else text(r, 'Размер'),
            'description': text(r, 'Описание'),
            'photo': text(r, 'На фото'),
            'alt': text(r, 'Alt-текст'),
            'theme': text(r, 'Тема'),
            'seo': text(r, 'SEO-описание'),
            'rooms': text(r, 'Комнаты'),
            'available': yes(text(r, 'В наличии')),
            'visible': yes(text(r, 'Показывать на сайте')),
        }
        w['sizes'] = work_sizes(w, sizes, frames)
        if len(w['sizes']) == 1 and w['sizes'][0]['dims']:
            w['meta_size'] = w['sizes'][0]['dims']
        w['rub'] = min((s['rub'] for s in w['sizes']), default=0)
        w['kzt'] = min((s['kzt'] for s in w['sizes']), default=0)
        w['from'] = len(w['sizes']) > 1
        if w['visible'] and w['name'] and w['img']:
            works.append(w)
    merged = {}
    for w in works:
        if w['id'] not in merged:
            merged[w['id']] = w
    works = sorted(merged.values(), key=lambda w: (w['tab'], w['order']))
    return works, sizes


def faq_from_html(page):
    items = []
    for q, a in re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>', page, re.S):
        answer = html.unescape(re.sub(r'<[^>]+>', '', a)).replace('\xa0', ' ').strip()
        items.append((html.unescape(q).strip(), answer))
    return items


ROOMS_BY_THEME = {'абстракция': 'гостиная, кабинет, прихожая', 'архитектура': 'гостиная, кабинет, прихожая',
                  'города и берега': 'гостиная, кабинет, прихожая', 'автоспорт': 'кабинет, гостиная, детская',
                  'пейзаж': 'гостиная, спальня, столовая', 'вазы': 'гостиная, столовая, спальня', 'живопись': 'гостиная, спальня, столовая'}


def seo_text(w):
    """Как seoText() в site.js: только для поисковиков и нейросетей, на сайте не показывается."""
    if w['seo']:
        return w['seo']
    rooms = w['rooms'] or ROOMS_BY_THEME.get(w['theme'].lower(), 'спальня, гостиная, кухня')
    theme = f', {w["theme"].lower()}' if w['theme'] else ''
    return (f'{w["name"]} — картина для интерьера{theme}, в раме с паспарту. Для интерьера: {rooms}. '
            'Купить картину в Астане (студия на Кабанбай батыра) или заказать с доставкой в Москве.')


def product_url(w):
    return f'{SITE}/kartiny/{w["id"]}.html'


def jsonld(works, faq):
    store = {
        '@type': 'Store', '@id': SITE + '/#store', 'name': 'КУЛЬТКАРТИН',
        'alternateName': 'Студия декора «Культкартин»', 'url': SITE + '/', 'logo': LOGO, 'image': OG_IMAGE,
        'description': 'Авторские картины, графика и иллюстрации для интерьера в раме с паспарту. Подбор под интерьер, студия в Астане, онлайн-заказ в Москве.',
        'telephone': '+7 707 101 08 14', 'email': 'zakaz@kultkartin.ru',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Кабанбай батыра 60/10, офис 2', 'addressLocality': 'Астана', 'addressCountry': 'KZ'},
        'areaServed': [{'@type': 'Country', 'name': 'Казахстан'}, {'@type': 'Country', 'name': 'Россия'}],
        'currenciesAccepted': 'KZT, RUB', 'sameAs': SOCIALS,
        'contactPoint': [
            {'@type': 'ContactPoint', 'telephone': '+7 707 101 08 14', 'contactType': 'sales', 'areaServed': 'KZ', 'availableLanguage': 'ru'},
            {'@type': 'ContactPoint', 'telephone': '+7 900 096 97 93', 'contactType': 'sales', 'areaServed': 'RU', 'availableLanguage': 'ru'},
        ],
    }
    graph = [
        store,
        {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'КУЛЬТКАРТИН', 'inLanguage': 'ru', 'publisher': {'@id': SITE + '/#store'}},
        {'@type': 'ItemList', 'name': 'Каталог картин КУЛЬТКАРТИН', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': product_url(w), 'name': w['name'], 'description': seo_text(w)} for i, w in enumerate(works)]},
    ]
    if faq:
        graph.append({'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]})
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)
    data = data.replace('<', '\\u003c')  # текст из таблицы не закроет <script>
    return f'<script type="application/ld+json">\n{data}\n</script>'


def catalog_cards(works):
    """Та же разметка карточек, что рисует assets/site.js: видна поисковикам без JavaScript."""
    heart = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.5 12.572l-7.5 7.428l-7.5 -7.428a5 5 0 1 1 7.5 -6.566a5 5 0 1 1 7.5 6.572"></path></svg>'
    cards = []
    for w in works:
        e = lambda s: html.escape(s, quote=True)
        meta = ' · '.join(x for x in (w['material'], w['meta_size']) if x)
        cards.append(
            f'<article class="product" data-product-id="{w["id"]}">\n<div class="product-image">\n'
            f'<img loading="lazy" src="{e(w["thumb"])}" alt="{e(w["alt"] or w["name"])}">\n'
            f'<button class="heart" data-id="{w["id"]}" aria-label="Добавить в избранное">{heart}</button>\n</div>\n'
            f'<h3><a href="kartiny/{w["id"]}.html">{e(w["name"])}</a></h3>\n<div class="meta">{e(meta)}</div>\n'
            f'<div class="price">{"от " if w["from"] else ""}{money(w["rub"])} ₽</div>\n</article>')
    return '\n'.join(cards)


def replace_block(page, name, content):
    pattern = re.compile(rf'(<!-- seo:{name}:start -->\n).*?(<!-- seo:{name}:end -->)', re.S)
    assert pattern.search(page), name
    return pattern.sub(lambda m: m.group(1) + content + '\n' + m.group(2), page)


def llms(works, sizes, faq):
    lines = [
        '# КУЛЬТКАРТИН',
        '',
        '> Авторские картины, графика и иллюстрации для интерьера. Каждая работа продаётся в раме с паспарту, '
        'в нескольких размерах по фиксированной цене (всего 10 форматов: 5 прямоугольных и 5 квадратных). Студия декора «Культкартин» в Астане (Казахстан), '
        'онлайн-заказ в Москве (Россия). Помогаем подобрать картину, формат и оформление под интерьер.',
        '',
        '## Контакты',
        '',
        '- Сайт-каталог: ' + SITE + '/',
        '- Основной сайт: https://kultkartin.com',
        '- Менеджер в WhatsApp (Астана): https://wa.me/77071010814, телефон +7 707 101 08 14',
        '- Студия в Астане: Кабанбай батыра 60/10, офис 2. 2ГИС: https://2gis.kz/astana/firm/70000001063937568/tab/info',
        '- Москва, онлайн: +7 900 096 97 93, Telegram https://t.me/kult_kartin',
        '- Почта: zakaz@kultkartin.ru',
        '- Instagram: https://www.instagram.com/kultkartin/ · Threads: https://www.threads.com/@kultkartin · '
        'YouTube: https://www.youtube.com/@kultkartin · Telegram-канал: https://t.me/kultkartin',
        '',
    ]
    if sizes:
        lines += ['## Размеры и цены за штуку', '', 'Цены фиксированные и включают раму, паспарту, декор, иллюстрацию и бумагу. '
                  'Общий габарит зависит от рамы и указан на странице каждой картины.', '']
        for s in sizes:
            prices = ', '.join(p for p in (f'{money(s["kzt"])} ₸' if s['kzt'] else '', f'{money(s["rub"])} ₽' if s['rub'] else '') if p)
            kind = {'rect': 'прямоугольный', 'square': 'квадратный'}.get(s['format'], '')
            img = f', изображение {s["image"]} см' if s['image'] else ''
            lines.append(f'- {s["code"]}' + (f' ({kind}{img})' if kind or img else '') + (f' — {prices}' if prices else ''))
        lines.append('')
    lines += ['## Каталог', '']
    for w in works:
        meta = ', '.join(x for x in (w['material'], w['meta_size']) if x)
        price = ('от ' if w['from'] else '') + f'{money(w["rub"])} ₽ / {money(w["kzt"])} ₸'
        if w['sizes']:
            meta += '; размеры: ' + ', '.join(f'{s["code"]} {s["dims"]}'.strip() for s in w['sizes'])
        extra = (f' {w["description"]}' if w['description'] else '') + ' ' + seo_text(w)
        lines.append(f'- [{w["name"]}]({product_url(w)}): {meta}, {price}{", в наличии" if w["available"] else ""}.{extra}')
    lines.append('')
    if faq:
        lines += ['## Частые вопросы', '']
        for q, a in faq:
            lines += [f'### {q}', '', a, '']
    return '\n'.join(lines)


def product_jsonld(w):
    url = product_url(w)
    offers = []
    for s in w['sizes']:
        for cur, price, city in (('KZT', s['kzt'], 'Астана'), ('RUB', s['rub'], 'Москва')):
            if price:
                offers.append({'@type': 'Offer', 'name': f'Размер {s["code"]}' + (f', {s["dims"]}' if s['dims'] else ''), 'price': price,
                               'priceCurrency': cur, 'availability': 'https://schema.org/InStock' if w['available'] else 'https://schema.org/MadeToOrder',
                               'url': url, 'areaServed': {'@type': 'City', 'name': city}, 'seller': {'@id': SITE + '/#store'}})
    rooms = w['rooms'] or ROOMS_BY_THEME.get(w['theme'].lower(), 'спальня, гостиная, кухня')
    product = {'@type': 'Product', '@id': url + '#product', 'name': w['name'], 'image': [w['og']], 'url': url,
               'description': w['description'] or seo_text(w), 'sku': str(w['id']), 'category': w['material'] or 'Картина',
               'brand': {'@type': 'Brand', 'name': 'КУЛЬТКАРТИН'},
               'keywords': ', '.join(['картина для интерьера', 'картина в Астане', 'картина в Москве'] + ['картина ' + r.strip() for r in rooms.split(',')])}
    if offers:
        product['offers'] = offers
    data = {'@context': 'https://schema.org', '@graph': [product, {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Каталог', 'item': SITE + '/#catalog'},
        {'@type': 'ListItem', 'position': 3, 'name': w['name'], 'item': url}]}]}
    return json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')


def product_page(template, w):
    """Готовая страница картины для поисковиков и ИИ-ботов, которые не выполняют JavaScript. Скрипт потом рисует её как обычно."""
    e = lambda s: html.escape(s or '', quote=True)
    url = product_url(w)
    title = f'{w["name"]} — картина для интерьера | КУЛЬТКАРТИН'
    desc = seo_text(w)[:300]
    page = template.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="../">', 1)
    page = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', page, count=1, flags=re.S)
    for attr, value in (('name="description"', desc), ('property="og:title"', title), ('property="og:description"', desc),
                        ('property="og:url"', url), ('property="og:image"', w['og']), ('name="twitter:title"', title),
                        ('name="twitter:description"', desc), ('name="twitter:image"', w['og'])):
        page = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + e(value) + m.group(2), page, count=1)
    page = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), page, count=1)
    page = page.replace("<script>document.documentElement.classList.add('kk-wait')</script>\n", '', 1)
    page = page.replace('</head>', f'<script type="application/ld+json" id="productJsonLd">{product_jsonld(w)}</script>\n</head>', 1)
    page = page.replace('<body>', f'<body data-product-id="{w["id"]}" data-canonical="{url}">', 1)
    page = page.replace('href="#contacts"', f'href="kartiny/{w["id"]}.html#contacts"')
    price = ('от ' if w['from'] else '') + f'{money(w["rub"])} ₽ / {money(w["kzt"])} ₸' if w['rub'] or w['kzt'] else 'Цена по запросу'
    sizes = ''.join(f'<li><span class="size-code">{e(s["code"])}</span><span class="size-dim">{e("Общий габарит " + s["dims"] if s["dims"] else "")}</span>'
                    f'<span class="size-price">{money(s["rub"])} ₽ / {money(s["kzt"])} ₸ за шт.</span></li>' for s in w['sizes'])
    meta = ', '.join(x for x in (w['material'], w['meta_size']) if x)
    images = w['images'] or [w['img']]
    thumbs = ''.join(f'<button class="thumb{"" if i else " active"}" type="button" data-src="{e(src)}" aria-label="Фото {i + 1}"><img src="{e(src)}" alt=""></button>' for i, src in enumerate(images))
    fit = ' class="fit"' if w['material'] == 'Живопись' else ''
    app = (f'<a class="back" href="index.html#catalog"><span>←</span>Вернуться в каталог</a><div class="product-layout"><div class="gallery"><div class="thumbs">{thumbs}</div><div class="main-image">'
           f'<img{fit} src="{e(w["img"])}" alt="{e(w["alt"] or w["name"])}"></div></div><div class="product-info"><h1>{e(w["name"])}</h1><p class="meta">{e(meta)}</p>'
           f'<p class="price">{price}</p><div class="product-details">' + (f'<p>{e(w["description"])}</p>' if w['description'] else '')
           + (f'<p>На фото: {e(w["photo"])}</p>' if w['photo'] else '')
           + (f'<h3>Доступно в следующих размерах</h3><ul class="size-list">{sizes}</ul><p class="details-note">Цены фиксированные и уже включают раму, паспарту, декор, иллюстрацию и бумагу.</p>' if sizes else '')
           + '</div></div></div>')
    page = page.replace('<div class="product-page" id="app"></div>', f'<div class="product-page" id="app">{app}</div>', 1)
    return page


def main():
    works, sizes = load()
    today = datetime.date.today().isoformat()
    index_path = os.path.join(DIST, 'index.html')
    page = open(index_path, encoding='utf-8').read()
    faq = faq_from_html(page)
    page = replace_block(page, 'jsonld', jsonld(works, faq))
    page = replace_block(page, 'catalog', catalog_cards(works))
    open(index_path, 'w', encoding='utf-8').write(page)

    urls = [(SITE + '/', '1.0')] + [(product_url(w), '0.8') for w in works]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f'<url><loc>{html.escape(u)}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>' for u, p in urls]
    sitemap.append('</urlset>')
    open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sitemap) + '\n')

    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai',
            'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'YandexBot', 'YandexAdditional', 'Bingbot']
    robots = ['User-agent: *', 'Allow: /', 'Disallow: /favorites.html', '']
    for b in bots:
        robots += [f'User-agent: {b}', 'Allow: /', 'Disallow: /favorites.html', '']
    robots += [f'Sitemap: {SITE}/sitemap.xml', '']
    open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write('\n'.join(robots))

    open(os.path.join(DIST, 'llms.txt'), 'w', encoding='utf-8').write(llms(works, sizes, faq))

    # готовые страницы картин + список для ссылок на сайте (assets/pages.js)
    pages_dir = os.path.join(DIST, 'kartiny')
    os.makedirs(pages_dir, exist_ok=True)
    for name in os.listdir(pages_dir):
        if name.endswith('.html'):
            os.remove(os.path.join(pages_dir, name))
    template = open(os.path.join(DIST, 'product.html'), encoding='utf-8').read()
    for w in works:
        open(os.path.join(pages_dir, f'{w["id"]}.html'), 'w', encoding='utf-8').write(product_page(template, w))
    open(os.path.join(DIST, 'assets', 'pages.js'), 'w', encoding='utf-8').write(
        '// Сгенерировано work/build_seo.py: картины, у которых есть готовая страница kartiny/ID.html\nwindow.kkStaticPages=' + json.dumps([w['id'] for w in works]) + ';\n')
    print(f'ok: {len(works)} картин, {len(sizes)} размеров, {len(faq)} вопросов')


if __name__ == '__main__':
    main()

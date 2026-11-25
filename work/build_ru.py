"""Российская версия сайта для kultkartin.ru (Анна, 2026-11-25): dist/ → dist-ru/.

Основной сайт kultkartin.com (Казахстан) не меняется. Здесь из готовой сборки делается версия для России:
- адреса kultkartin.com → kultkartin.ru (canonical, og, sitemap, llms.txt, feed.yml в рублях), hreflang ru-RU / ru-KZ;
- цены по умолчанию в ₽, тексты «производство в России, изготовление и доставка по России — 2–4 недели»;
- без Instagram, Threads, Facebook (Meta признана в РФ экстремистской): ссылки, иконки, названия, sameAs в JSON-LD;
- WhatsApp в РФ заблокирован → все кнопки ведут в MAX (московский менеджер), WhatsApp из контактов убран;
- шрифты с нашего сервера, а не с Google Fonts (без передачи данных за рубеж);
- плашка о cookie, страницы /politika/ (персональные данные) и /usloviya/ (условия продажи), реквизиты продавца в подвале.
Реквизиты — словарь SELLER ниже: пока Женя их не прислала, там пометки [ЗАПОЛНИТЬ …], сайт с ними не публиковать
(скрипт пишет предупреждение). Запуск: python3 work/build_ru.py  (после work/build_seo.py)
"""
import json, os, re, shutil, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'dist')
OUT = os.path.join(HERE, '..', 'dist-ru')
FONTS_CACHE = os.path.join(HERE, 'fonts-ru')
COM, RU = 'https://kultkartin.com', 'https://kultkartin.ru'
MAX = 'https://max.ru/u/f9LHodD0cOJloE29Q-VzMJYECs3BGioSGMVeFyr-atLdFYsCHGdBmR42H_4'  # московский менеджер (из контактов сайта)
PHONE_RU = '+7 900 096 97 93'
EMAIL = 'zakaz@kultkartin.ru'

# Реквизиты продавца для России — прислать Женя (список вопросов у Анны, 2026-11-25)
SELLER = {
    'name': '[ЗАПОЛНИТЬ: ИП Фамилия Имя Отчество или ООО «…»]',
    'inn': '[ЗАПОЛНИТЬ: ИНН]',
    'ogrn': '[ЗАПОЛНИТЬ: ОГРНИП или ОГРН]',
    'address': '[ЗАПОЛНИТЬ: юридический адрес в России]',
    'prod_address': '[ЗАПОЛНИТЬ: город/адрес производства]',
    'pay': '[ЗАПОЛНИТЬ: способы оплаты — перевод по счёту, карта, СБП, предоплата %]',
    'delivery': '[ЗАПОЛНИТЬ: чем доставляете — СДЭК, Деловые Линии, курьер; кто платит доставку]',
    'rkn': '[ЗАПОЛНИТЬ: номер в реестре операторов ПДн Роскомнадзора, если уже подано]',
}

SKIP = ('pult', 'mishinadesign', 'kollekciya-prototip.html', 'rossiya.html', 'CNAME', '.nojekyll', 'feed-kz.yml', 'wa')
DELIVERY = 'Производство в России, изготовление и доставка по России — 2–4 недели.'
TEXT = [
    ('доставка по Казахстану и России', 'доставка по всей России'),
    ('Доставка по всему Казахстану и России, студия в Астане.', DELIVERY),
    ('от 68 000 ₸', 'от 11 000 ₽'),
    ('Купить картину в Астане (студия на Кабанбай батыра) или заказать с доставкой по России и Казахстану.',
     'Заказать картину с доставкой по всей России. ' + DELIVERY),
    ('обсудим работу, наличие и детали доставки.', 'обсудим работу, наличие и детали доставки. ' + DELIVERY),
    ('В Москве работаем онлайн.', 'По России работаем онлайн: производство в России, изготовление и доставка — 2–4 недели.'),
    ('Напишите нам в почту или социальные сети', 'Напишите нам в MAX, Telegram или на почту'),
    ('Быстрее всего ответим в WhatsApp.', 'Быстрее всего ответим в MAX.'),
    ('в WhatsApp или Telegram', 'в MAX или Telegram'),
    ('в&nbsp;WhatsApp', 'в&nbsp;MAX'), ('в WhatsApp', 'в MAX'), ('Написать в WhatsApp', 'Написать в MAX'),
    ('>WhatsApp</a>', '>MAX</a>'),
    # блок постов: без названия соцсети и без ссылок на неё
    ('<h2>Картины в&nbsp;жизни</h2>', '<h2>Картины в&nbsp;интерьерах</h2>'),
    ('В нашем Instagram&nbsp;— картины в&nbsp;настоящих интерьерах, примерки у&nbsp;клиентов и&nbsp;новинки.',
     'Картины в&nbsp;настоящих интерьерах, примерки у&nbsp;клиентов и&nbsp;новинки.'),
]
META_LINK = re.compile(r'<a\b[^>]*href="[^"]*(?:instagram\.com|threads\.(?:com|net)|facebook\.com|fb\.com)[^"]*"[^>]*>.*?</a>', re.S)
WA_CLINK = re.compile(r'<a class="c-link" href="https://wa\.me/[^"]*"[^>]*>.*?</a>', re.S)
WA_WIDGET = re.compile(r'<a class="contact-channel" href="https://wa\.me/[^"]*"[^>]*>.*?</a>', re.S)
WA_URL = re.compile(r'https://wa\.me/7\d{10}')
SAMEAS_META = re.compile(r'\s*"https://www\.(?:instagram|threads|facebook)\.com/[^"]*",?')

BANNER = ('<div class="ru-cookie" id="ruCookie" hidden><p>Мы используем cookie и&nbsp;Яндекс Метрику, чтобы сайт работал и&nbsp;становился удобнее. '
          'Продолжая пользоваться сайтом, вы&nbsp;соглашаетесь с&nbsp;<a href="/politika/">политикой обработки персональных данных</a>.</p>'
          '<button type="button" id="ruCookieOk">Понятно</button></div>'
          '<script>(function(){var b=document.getElementById("ruCookie");try{if(localStorage.getItem("kk-cookie-ok"))return}catch(e){}'
          'b.hidden=false;document.getElementById("ruCookieOk").onclick=function(){try{localStorage.setItem("kk-cookie-ok","1")}catch(e){}b.hidden=true}})()</script>')
CSS = ('<style>.ru-cookie{position:fixed;z-index:60;left:16px;right:16px;bottom:16px;max-width:620px;margin:0 auto;display:flex;gap:16px;align-items:center;'
       'background:#fbf6ee;color:#161a17;border:1px solid #e2d3c2;padding:14px 16px;box-shadow:0 10px 30px #0000001f;font:14px/1.5 Manrope,Arial,sans-serif}'
       '.ru-cookie[hidden]{display:none}.ru-cookie p{margin:0}.ru-cookie a{color:#440512;text-decoration:underline}'
       '.ru-cookie button{flex:none;border:0;background:#440512;color:#fff;padding:10px 18px;font:600 14px Manrope,Arial,sans-serif;cursor:pointer}'
       '.foot-ru{margin:0 0 10px;font-size:13px;line-height:1.6;color:inherit;opacity:.85}.foot-ru a{text-decoration:underline}'
       '@media(max-width:640px){.ru-cookie{flex-direction:column;align-items:stretch}}</style>')


def head_extra(path):
    return ('<script>try{if(!new URLSearchParams(location.search).get("cur")&&!localStorage.getItem("kk-currency"))localStorage.setItem("kk-currency","RUB")}catch(e){}</script>'
            f'<link rel="alternate" hreflang="ru-RU" href="{RU}{path}"><link rel="alternate" hreflang="ru-KZ" href="{COM}{path}">'
            f'<link rel="alternate" hreflang="x-default" href="{COM}{path}">' + CSS)


def foot_line():
    s = SELLER
    return (f'<p class="foot-ru">Продавец: {s["name"]}, ИНН {s["inn"]}, {s["ogrn"]}. '
            '<a href="/usloviya/">Условия продажи и доставки</a> · <a href="/politika/">Политика обработки персональных данных</a></p>')


def local_fonts(html, assets_prefix):
    """Google Fonts → свои файлы (кеш work/fonts-ru), чтобы браузер не ходил на серверы Google."""
    m = re.search(r'<link[^>]+href="(https://fonts\.googleapis\.com/css2[^"]+)"[^>]*>', html)
    if not m:
        return html
    url = m.group(1).replace('&amp;', '&')
    os.makedirs(FONTS_CACHE, exist_ok=True)
    key = re.sub(r'\W+', '_', url)[-80:]
    css_path = os.path.join(FONTS_CACHE, key + '.css')
    if not os.path.exists(css_path):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'})
        css = urllib.request.urlopen(req, timeout=60).read().decode()
        for f in sorted(set(re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css))):
            name = re.sub(r'\W+', '_', f.split('/s/')[-1])
            dst = os.path.join(FONTS_CACHE, name)
            if not os.path.exists(dst):
                open(dst, 'wb').write(urllib.request.urlopen(f, timeout=60).read())
            css = css.replace(f, '/assets/fonts/' + name)
        open(css_path, 'w').write(css)
    fonts_dir = os.path.join(OUT, 'assets', 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    for f in os.listdir(FONTS_CACHE):
        shutil.copy2(os.path.join(FONTS_CACHE, f), os.path.join(fonts_dir, f))
    html = html.replace(m.group(0), f'<link rel="stylesheet" href="/assets/fonts/{key}.css">')
    return re.sub(r'<link[^>]+(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>\s*', '', html)


def ru_html(html, path):
    html = html.replace('<a class="insta-card"', '<div class="insta-card"')
    html = re.sub(r'(<div class="insta-card") href="[^"]*" target="_blank" rel="noopener"(?: aria-hidden="true" tabindex="-1")?', r'\1', html)
    html = re.sub(r'(<div class="insta-card"[^>]*>.*?)</a>', r'\1</div>', html, flags=re.S)
    html = re.sub(r'alt="(?:Пост|Видео) в Instagram @[\w.]+: ', 'alt="', html)
    html = META_LINK.sub('', html)
    html = WA_CLINK.sub('', html)
    html = SAMEAS_META.sub('', html)
    for a, b in TEXT:
        html = html.replace(a, b)
    html = WA_URL.sub(MAX, html)
    html = html.replace('>kultkartin.com</a>', '>kultkartin.ru</a>')
    html = local_fonts(html, '/assets/')
    html = re.sub(r'<head([^>]*)>', lambda m: m.group(0) + head_extra(path), html, count=1)
    html = html.replace('<a class="foot-credit"', foot_line() + '<a class="foot-credit"', 1)
    html = html.replace('</body>', BANNER + '</body>', 1)
    return html


def ru_text(s):
    s = s.replace(COM, RU).replace('kultkartin.com/', 'kultkartin.ru/')
    return s


def page(title, body):
    tpl = open(os.path.join(HERE, 'ru-page.html'), encoding='utf-8').read()
    return tpl.replace('%TITLE%', title).replace('%BODY%', body).replace('%RU%', RU)


def legal_pages():
    s = {k: f'<span class="fill">{v}</span>' if v.startswith('[') else v for k, v in SELLER.items()}
    usl = '''
<p>Продавец: {name}, ИНН {inn}, {ogrn}, адрес: {address}. Телефон: {phone}, почта: <a href="mailto:{email}">{email}</a>.</p>
<h2>Товар</h2><p>Картины, гравюры и постеры в раме с паспарту. Фото и описания на сайте — справочные: оттенки на экране могут немного отличаться, а оформление можно изменить по договорённости с менеджером.</p>
<h2>Цены</h2><p>Цены указаны в рублях и включают раму, паспарту, печать и бумагу. Стоимость доставки рассчитывается отдельно и сообщается до оплаты.</p>
<h2>Как оформить заказ</h2><p>Напишите менеджеру в MAX, Telegram, позвоните или отправьте письмо. Менеджер подтверждает работу, размер, оформление, цену и срок, после чего присылает счёт или ссылку на оплату.</p>
<h2>Оплата</h2><p>{pay}</p>
<h2>Изготовление и доставка</h2><p>Производство находится в России ({prod_address}). Изготовление и доставка по России занимают 2–4 недели с момента оплаты. {delivery}</p>
<h2>Возврат и обмен</h2><p>Покупатель вправе отказаться от товара надлежащего качества в любое время до его передачи, а после передачи — в течение 7 дней, если сохранены его товарный вид и потребительские свойства (ст.
26.1 Закона «О защите прав потребителей»).
Если работа изготовлена по индивидуальному заказу — в нестандартном размере или оформлении, согласованном с покупателем, — возврат товара надлежащего качества не производится.
При обнаружении брака или повреждения при доставке мы заменим товар или вернём деньги: сообщите нам в течение 7 дней с фото повреждения.</p>
<h2>Персональные данные</h2><p>Обрабатываем данные покупателей только для выполнения заказа — см. <a href="/politika/">политику обработки персональных данных</a>.</p>'''.format(phone=PHONE_RU, email=EMAIL, **s)
    pol = '''
<p>Оператор персональных данных: {name}, ИНН {inn}, {ogrn}, адрес: {address}. Почта для обращений: <a href="mailto:{email}">{email}</a>. Номер в реестре операторов Роскомнадзора: {rkn}.</p>
<h2>Какие данные мы обрабатываем</h2><p>Имя, телефон, адрес электронной почты, адрес доставки и переписку — когда вы пишете нам или оформляете заказ. Технические данные — cookie, сведения о браузере и устройстве, IP-адрес, страницы сайта, которые вы посещаете, — с помощью сервиса Яндекс Метрика (ООО «Яндекс», Россия).</p>
<h2>Зачем</h2><p>Чтобы ответить на ваш вопрос, оформить, изготовить и доставить заказ, а также чтобы понимать, как пользуются сайтом, и делать его удобнее.</p>
<h2>Основания</h2><p>Исполнение договора с вами (заказ и доставка), ваше согласие (cookie и аналитика) и требования закона (бухгалтерский учёт).</p>
<h2>Где и сколько храним</h2><p>Данные граждан России записываются и хранятся в базах данных на территории России. Храним их, пока это нужно для заказа и учёта, затем удаляем. Данные передаются только службам доставки и платёжным сервисам в объёме, необходимом для выполнения заказа.</p>
<h2>Cookie</h2><p>Сайт использует cookie, необходимые для работы (избранное, выбор валюты), и cookie Яндекс Метрики для статистики. Отключить cookie можно в настройках браузера — сайт продолжит работать.</p>
<h2>Ваши права</h2><p>Вы можете узнать, какие данные о вас мы храним, попросить их исправить или удалить, отозвать согласие — напишите на <a href="mailto:{email}">{email}</a>. Ответим в течение 10 рабочих дней.</p>
<p>Политика действует с [ЗАПОЛНИТЬ: дата публикации] и применяется к сайту kultkartin.ru.</p>'''.format(phone=PHONE_RU, email=EMAIL, **s)
    for slug, title, body in (('usloviya', 'Условия продажи и доставки', usl), ('politika', 'Политика обработки персональных данных', pol)):
        os.makedirs(os.path.join(OUT, slug), exist_ok=True)
        open(os.path.join(OUT, slug, 'index.html'), 'w', encoding='utf-8').write(page(title, body).replace(f'<link rel="canonical" href="{RU}/">', f'<link rel="canonical" href="{RU}/{slug}/">'))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT, ignore=lambda d, names: [n for n in names if os.path.samefile(d, SRC) and n in SKIP])
    for root, _, files in os.walk(OUT):
        for f in files:
            p = os.path.join(root, f)
            if not f.endswith(('.html', '.js', '.txt', '.xml', '.yml', '.css', '.json')):
                continue
            s = ru_text(open(p, encoding='utf-8').read())
            rel = '/' + os.path.relpath(p, OUT).replace(os.sep, '/')
            if f.endswith('.html'):
                path = rel[:-len('index.html')] if rel.endswith('/index.html') else rel
                s = ru_html(s, path)
            elif f.endswith('.js'):
                s = WA_WIDGET.sub('', s)
                s = WA_URL.sub(MAX, s)
            elif f == 'llms.txt':
                s = re.sub(r'Instagram: \S+ · |Threads: \S+ · |Instagram/Facebook', '', s)
                s = re.sub(r'Менеджер в WhatsApp \(Астана\): \S+, телефон \+7 707 101 08 14', 'Менеджер для России в MAX: ' + MAX + ', телефон ' + PHONE_RU, s)
                s = s.replace(' (WhatsApp, Telegram, MAX)', ' (MAX, Telegram)').replace(' (WhatsApp)', '')
                s = WA_URL.sub(MAX, s)
                for a, b in TEXT:
                    s = s.replace(a, b)
            open(p, 'w', encoding='utf-8').write(s)
    legal_pages()
    sm = os.path.join(OUT, 'sitemap.xml')
    s = open(sm).read()
    s = s.replace('</urlset>', ''.join(f'<url><loc>{RU}/{x}/</loc></url>' for x in ('usloviya', 'politika')) + '</urlset>')
    open(sm, 'w').write(s)
    # проверка: что осталось из запрещённого и иностранного
    left = {}
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(('.html', '.txt')):
                t = open(os.path.join(root, f), encoding='utf-8').read()
                t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
                for w in ('instagram', 'threads', 'facebook', 'wa.me', 'whatsapp', 'kultkartin.com/', 'fonts.googleapis'):
                    if w in t.lower():
                        left.setdefault(w, []).append(os.path.relpath(os.path.join(root, f), OUT))
    for w, v in left.items():
        print(f'осталось «{w}»: {len(v)} файлов, напр. {v[:3]}')
    if any(v.startswith('[') for v in SELLER.values()):
        print('ВНИМАНИЕ: реквизиты продавца не заполнены (SELLER) — dist-ru не публиковать')
    print('готово:', OUT)


if __name__ == '__main__':
    main()

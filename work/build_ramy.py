"""Библиотека картин в раме: фото с Яндекс Диска заказчицы → dist/assets/ramy/<артикул>.webp (+ s/ — миниатюра)
и данные dist/assets/ramy/data.js (window.RAMY). Артикул C1-1001W1-23B6-44: C1 — формат и размер (буква = строка
листа «Размеры»), 1001 — иллюстрация, W1 — материал (W1 бумага), 23 — рама, B6 — паспарту, 44 — декор.
Цена — по букве размера из листа «Размеры» Google Таблицы каталога. Папки «Фоны» и «Сетка…» пропускаются.
Оригиналы кешируются в work/ramy-src (не в git). Запуск: python3 work/build_ramy.py [--dry] (нужен Pillow)."""
import json, os, re, sys, csv, io, time, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, '..', 'dist')
OUT = os.path.join(DIST, 'assets', 'ramy')
SRC = os.path.join(HERE, 'ramy-src')
KEY = 'https://disk.yandex.ru/d/qNB014o17FNQgQ'
API = 'https://cloud-api.yandex.net/v1/disk/public/resources'
SHEET = 'https://docs.google.com/spreadsheets/d/1ApEOrnflSSqiTu9kDIQwuAk9LsWOL5Syw9VfSZWJh80/gviz/tq?tqx=out:csv&sheet='
SKIP = ('/Фоны', '/Сетка')
COMMON = '/Культкартин - общая папка 2d картин'
SQUARE = set('JCRNY')
LAT = str.maketrans('АВСЕНКМОРТХ', 'ABCEHKMOPTX')
BIG, SMALL = 1100, 420
FIX = {'Черно белые орхидеи': 'Черно-белые орхидеи', 'Попугай': 'Попугаи'}  # опечатки в названиях папок
# плакаты лежат одной папкой — серия по номеру иллюстрации (Анна, 2026-11-11)
POSTERS = {'Паруса': '750 753 754 755 756 757 972 1101 1102 1103 1104', 'Нью-Йорк': '765 766 777 778 779',
           'Гонки': '791 792 793 794 971', 'Города': '795 796 797 798', 'Гравюры': '787 788 789 790',
           'Абстракция': '841 844 845 847 856 857', 'Папоротники': '4238'}
POSTERS = {n: s for s, ns in POSTERS.items() for n in ns.split()}


def get(url, tries=5):
    for i in range(tries):  # Диск иногда отвечает 500/429 — повторяем
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'kultkartin-build'}), timeout=60)
        except (urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)


def ls(path):
    out, off = [], 0
    while True:
        q = urllib.parse.urlencode({'public_key': KEY, 'path': path, 'limit': 1000, 'offset': off,
                                    'fields': '_embedded.items.name,_embedded.items.type,_embedded.items.path,_embedded.items.md5,_embedded.total'})
        e = json.load(get(API + '?' + q))['_embedded']
        out += e['items']; off += len(e['items'])
        if off >= e['total'] or not e['items']:
            return out


def walk(path='/'):
    for x in ls(path):
        if x['type'] == 'dir':
            if not x['path'].startswith(SKIP):
                yield from walk(x['path'])
        elif re.search(r'\.(jpe?g|png)', x['name'], re.I):
            yield x


ART = re.compile(r'([SMXLAJCRNY])(\d)?[- ]*(\d{3,4})-?([A-Z]\d?)?-(\d{2})([A-ZФ][0-9A-ZФ])-?(\d{2})?(?![0-9])')
ART2 = re.compile(r'([SMXLAJCRNY])(\d)?[- ]*(\d{3,4})-?([A-Z]\d?)?-(B[A-Z])(\d{2})(?![0-9])')  # опечатка BY34: паспарту перед рамой


def parse(name):
    n = name.upper().translate(LAT)
    m = ART.search(n)
    if m:
        size, sd, num, mat, frame, mat_b, decor = m.groups()
    else:
        m = ART2.search(n)
        if not m:
            return None
        size, sd, num, mat, mat_b, frame = m.groups(); decor = None
    sm = re.search(r'РАЗМЕР\D*?(\d+(?:,\d+)?)\D+?(\d+(?:,\d+)?)', name.upper())
    return {
        'id': f"{size}{sd or ''}-{num}{mat or ''}-{frame}{mat_b}{decor or ''}",
        'size': size, 'num': num, 'mat': mat or '', 'frame': frame, 'pp': mat_b, 'decor': decor or '',
        'cm': f"{sm.group(1)} × {sm.group(2)}" if sm else '',
    }


def clean_series(folder):
    s = re.sub(r'\(.*?\)', '', folder)
    s = re.sub(r'\b[A-ZА-Я]\d?-[\w-]*\d[\w-]*', '', s)  # коды вида C1-W1-23BA (буквы бывают кириллицей)
    s = re.sub(r'[A-Z]\d\S*', '', s).replace('.', ' ')  # «РозыX1», «Розовые. орхидеи»
    s = re.sub(r'\s+', ' ', s).strip(' -')
    return FIX.get(s, s) or folder


def prices():
    rows = list(csv.reader(io.StringIO(get(SHEET + urllib.parse.quote('Размеры')).read().decode('utf-8'))))
    head = [re.sub(r'[\s*]', '', h).lower() for h in rows[0]]
    col = lambda k: next(i for i, h in enumerate(head) if h.startswith(k))
    num = lambda v: int(re.sub(r'\D', '', v) or 0)
    return {r[col('размер')].strip(): {'rub': num(r[col('цена,₽')]), 'kzt': num(r[col('цена,₸')])} for r in rows[1:] if r[0].strip()}


def main(dry):
    items, bad = {}, []
    for f in walk():
        p = parse(f['name'])
        if not p:
            bad.append(f['path']); continue
        parts = f['path'].strip('/').split('/')
        common = f['path'].startswith(COMMON)
        p.update(src=f['path'], md5=f['md5'], theme=parts[0].strip(), series=clean_series(parts[-2]) if len(parts) > 2 else parts[0].strip(), common=common)
        if common:
            p['theme'] = 'Плакаты' if len(parts) > 2 and parts[1] == 'Плакаты' else ''
        old = items.get(p['id'])
        if not old or (old['common'] and not common):  # папка темы важнее общей
            p['alts'] = (old['alts'] if old else []) + [(f['path'], f['md5'])]
            items[p['id']] = p
        else:
            old['alts'].append((f['path'], f['md5']))
    # из общей папки: тема и название — как у той же иллюстрации в папках тем
    by_num = {}
    for w in items.values():
        if not w['common']:
            by_num.setdefault(w['num'], w)
    for w in items.values():
        if w['common']:
            twin = by_num.get(w['num'])
            if twin:
                w['theme'], w['series'] = twin['theme'], twin['series']
            else:
                w['theme'] = w['theme'] or 'Разное'
                w['series'] = w['theme']
    for w in items.values():
        if w['theme'] == 'Плакаты':
            w['series'] = POSTERS.get(w['num'], 'Плакаты')
    print('фото', sum(1 for _ in items), 'нераспознано', len(bad))
    for b in bad: print('  ?', b)
    from collections import Counter
    print(Counter(w['theme'] for w in items.values()).most_common())
    if dry:
        return
    pr = prices()
    os.makedirs(SRC, exist_ok=True); os.makedirs(os.path.join(OUT, 's'), exist_ok=True)

    def fetch(w):  # своя копия, а если Диск её не отдаёт — копия того же артикула из другой папки
        for path, md5 in sorted(w['alts'], key=lambda a: a[0] != w['src']):
            got = fetch_one(path, md5)
            if got:
                return got
        print('  не скачалось:', w['id'], flush=True)

    def fetch_one(path, md5):
        dst = os.path.join(SRC, md5 + os.path.splitext(path.strip())[1].lower()[:5])
        err = None
        for i in range(3):  # свежая ссылка на каждую попытку
            if os.path.exists(dst):
                return dst
            try:
                href = json.load(get(API + '/download?' + urllib.parse.urlencode({'public_key': KEY, 'path': path})))['href']
                data = get(href, 2).read()
                open(dst + '.part', 'wb').write(data); os.replace(dst + '.part', dst)
            except urllib.error.URLError as e:
                err = e
        print('  ошибка Диска:', path, err, flush=True)

    from PIL import Image
    def conv(w):
        src = fetch(w)
        if not src:
            return None
        big, small = os.path.join(OUT, w['id'] + '.webp'), os.path.join(OUT, 's', w['id'] + '.webp')
        im = Image.open(src).convert('RGB')
        w['w'], w['h'] = im.size
        if not (os.path.exists(big) and os.path.exists(small)):
            for dst, side, q in ((big, BIG, 80), (small, SMALL, 76)):
                k = min(1, side / max(im.size))
                im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).save(dst, 'WEBP', quality=q, method=6)
        return w

    with ThreadPoolExecutor(5) as ex:
        done = [w for w in ex.map(conv, items.values()) if w]
    data = []
    for w in sorted(done, key=lambda w: (w['theme'], w['series'], w['frame'], w['size'], w['num'])):
        f = 's' if w['size'] in SQUARE else ('h' if w['w'] > w['h'] * 1.02 else 'v')
        p = pr.get(w['size'], {})
        data.append({'id': w['id'], 't': w['theme'], 's': w['series'], 'f': f, 'n': w['num'], 'sz': w['size'], 'cm': w['cm'],
                     'mat': w['mat'], 'r': w['frame'], 'pp': w['pp'], 'd': w['decor'], 'kzt': p.get('kzt', 0), 'rub': p.get('rub', 0),
                     'w': round(w['w'] * min(1, SMALL / max(w['w'], w['h']))), 'h': round(w['h'] * min(1, SMALL / max(w['w'], w['h'])))})
    # удалить картинки артикулов, которых больше нет на Диске
    keep = {d['id'] for d in data}
    for folder in (OUT, os.path.join(OUT, 's')):
        for fn in os.listdir(folder):
            if fn.endswith('.webp') and fn[:-5] not in keep:
                os.remove(os.path.join(folder, fn))
    with open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.RAMY=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    og(data)
    print('готово', len(data))


def og(data):
    """Превью для ссылок: три картины в раме на бежевом фоне, 1200×630."""
    from PIL import Image
    dst = os.path.join(OUT, 'og.jpg')
    if os.path.exists(dst):
        return
    pick = [d for d in data if d['f'] == 'v'][:1] + [d for d in data if d['f'] == 's'][:1] + [d for d in data if d['f'] == 'v'][1:2]
    canvas = Image.new('RGB', (1200, 630), (251, 246, 238))
    ims = [Image.open(os.path.join(OUT, d['id'] + '.webp')).convert('RGB') for d in pick]
    gap = 40
    hgt = min(470, (1120 - gap * (len(ims) - 1)) / sum(im.width / im.height for im in ims))  # всё влезает с полями
    ims = [im.resize((round(im.width * hgt / im.height), round(hgt)), Image.LANCZOS) for im in ims]
    x = (1200 - sum(im.width for im in ims) - gap * (len(ims) - 1)) // 2
    for im in ims:
        canvas.paste(im, (x, (630 - im.height) // 2)); x += im.width + gap
    canvas.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)


if __name__ == '__main__':
    main('--dry' in sys.argv)

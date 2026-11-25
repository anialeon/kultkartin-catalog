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
    'hero_alt': 'четыре графичных гербария над кроватью', 'cta_short': 'Подобрать под мою спальню',
    'looks_title': 'Три спальни — три настроения', 'pick_title': 'Подойдут для спальни',
    'pick_sub': 'Спокойные тона, ботаника, пейзажи и мягкая графика. Каждую работу можно заказать в другом размере и оформлении.',
    'cta_title': 'Подберём картины под вашу спальню', 'furn': 'bed',
    'facts': [('2/3', 'ширины кровати', 'столько должна занимать композиция над изголовьем'),
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
    'schemes_title': 'Размер и развеска: четыре схемы',
    'scheme_bg': ('../для-статей/spalnya/schemes.jpg', {'W': 2000, 'H': 1493, 'k': 3.9, 'cx': 1012, 'top': 815, 'w': 180, 'label': 'кровать', 'stands': (516, 1512), 'vb': '390 185 1270 952'}),
    'schemes_lead': 'Композиция над кроватью занимает примерно две трети ширины изголовья. Нижний край рамы — на 20–30 см выше изголовья, между рамами — 5–8 см, центр композиции совпадает с центром кровати. Вот четыре проверенных варианта для кровати 180 см.',
    'schemes': [
        ('pair', 'Пара над изголовьем', 'Две вертикальные работы размера X, каждая 54,5 × 64,5 см с рамой. Ширина композиции — около 115 см.', 'Самый универсальный вариант для кровати 160–180 см.'),
        ('sides', 'Над прикроватными тумбами', 'По две работы размера M (около 35 × 45 см) столбиком над каждой тумбой.', 'Подходит, если над изголовьем бра, полка или высокое мягкое изголовье.'),
        ('panel', 'Одно большое панно', 'Горизонтальная работа размера A — 82 × 72 см с рамой.', 'Спокойный акцент для кровати 140–160 см и низкого изголовья.'),
        ('grid', 'Квадрат из четырёх', 'Четыре квадратные работы размера C, около 48 × 48 см каждая. Вместе — примерно 102 × 102 см.', 'Хорошо держит высокую стену и светлые стены в скандинавском интерьере.'),
    ],
    'size': ('Какой размер выбрать над кроватью', [
        'Ориентируйтесь на ширину изголовья: композиция должна занимать примерно две трети её ширины. Для кровати 160 см это около 100–110 см, для кровати 180 см — около 120 см.',
        'На практике это две вертикальные работы размера X (каждая 54,5 × 64,5 см с рамой) или четыре квадратные размера C (около 48 × 48 см), повешенные квадратом. Одна картина над широкой кроватью смотрится мелко — если хочется одну, берите самый крупный формат.']),
    'hang': ('Как повесить картины над кроватью', [
        'Нижний край рамы — на 20–30 см выше изголовья: так картину не заденешь головой, а композиция не «оторвётся» от кровати.',
        'Расстояние между рамами — 5–8 см, одинаковое по вертикали и горизонтали. Центр композиции совмещайте с центром кровати, а не стены.',
        'Если над кроватью уже есть бра, развеску лучше сделать вертикальной парой — работы встанут между светильниками.']),
    'cta_bg': 's7-krovat-dub/X2W1_34B6_4шт/3-расстановка.jpg',
    'works': [87, 85, 56, 9, 70, 30, 99, 114, 116, 66, 135, 86],
    'faq': [
        ('Какую картину повесить в спальне?', 'Спокойную по цвету и сюжету: ботаническую иллюстрацию, туманный пейзаж, мягкую графику. Яркие и динамичные работы лучше оставить для гостиной.'),
        ('Какого размера должна быть картина над кроватью?', 'Композиция — примерно две трети ширины изголовья: для кровати 160 см около 100–110 см. Это две вертикальные работы размера X или четыре квадратные размера C.'),
        ('На какой высоте вешать картину над кроватью?', 'Нижний край рамы — на 20–30 см выше изголовья, расстояние между рамами в группе — 5–8 см.'),
        ('Можно ли заказать картину в другом размере?', 'Да. Любую работу из каталога можно сделать в другом размере, раме и с другим паспарту — менеджер подскажет варианты и цену.'),
        ('Можно ли подобрать картину под мою спальню?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
}]

ARTICLES += [{
    'slug': 'kartiny-dlya-gostinoy', 'draft': True, 'furn': 'sofa',
    'title': 'Картины для гостиной: какой размер над диваном и как повесить | КУЛЬТКАРТИН',
    'desc': 'Какие картины повесить в гостиной, какой размер выбрать над диваном и как собрать пару, ряд или галерею. Подборка картин и постеров в раме с ценами.',
    'h1': 'Картины для гостиной',
    'lead': 'Гостиная — главная стена в доме. Разбираем, какой размер нужен над диваном, как собрать пару, ряд или галерею, и показываем на примерах из нашего каталога.',
    'hero': 's3-derevo/C1W1_09B6_3шт/3-расстановка.jpg', 'hero_alt': 'ботанические иллюстрации над диваном',
    'wa': 'Здравствуйте! Хочу подобрать картины для гостиной.', 'cta_short': 'Подобрать под мою гостиную',
    'schemes_title': 'Над диваном: четыре схемы',
    'schemes_lead': 'Композиция над диваном занимает примерно две трети его ширины. Нижний край рам — на 20–25 см выше спинки, между рамами — 5–8 см, центр композиции совпадает с центром дивана. Схемы — для дивана около 220 см.',
    'schemes': [
        ('pair', 'Пара над диваном', 'Две вертикальные работы размера X, каждая 54,5 × 64,5 см с рамой. Ширина — около 115 см.', 'Для дивана 180–200 см и спокойного интерьера.'),
        ('row3', 'Ряд из трёх', 'Три квадратные работы размера C, около 48 × 48 см. Вместе — около 156 см.', 'Для длинного дивана 220–240 см: держит всю стену.'),
        ('grid6', 'Галерея из шести', 'Шесть работ размера M (около 35 × 45 см) в два ряда. Около 117 × 97 см.', 'Для серий — ботаника, вазы, фасады. Выглядит как коллекция.'),
        ('panel', 'Одно большое панно', 'Горизонтальная работа размера A — 82 × 72 см с рамой.', 'Акцент для компактного дивана до 180 см.'),
    ],
    'looks_title': 'Три гостиные — три настроения',
    'looks': [
        ('s2-dalmatin/A2P1_01BA_chrysler_3шт/3-расстановка.jpg', 'Монохром над светлым диваном',
         'Три чёрно-белые фотографии Крайслер-билдинга в тонких рамах — графичный акцент для светлой гостиной с текстилем и деревом.', [19, 20, 21]),
        ('s3-derevo/M2V1_23B5_6шт/3-расстановка.jpg', 'Античные вазы на тёмном дереве',
         'Шесть иллюстраций с вазами и урнами в два ряда: на тёмных панелях серо-голубая палитра читается особенно благородно.', [50, 51, 52, 53, 54, 55]),
        ('s2-dalmatin/M1W1_11B655_4шт/3-расстановка.jpg', 'Классические фасады',
         'Архитектурная графика в светлых рамах добавляет гостиной строгости и подходит к неоклассике.', [38, 39, 40, 41]),
    ],
    'pick_title': 'Подойдут для гостиной',
    'pick_sub': 'Архитектура, фотография, вазы, абстракция и ботаника. Каждую работу можно заказать в другом размере и оформлении.',
    'works': [19, 38, 50, 137, 89, 56, 26, 66, 17, 42, 13, 85],
    'faq': [
        ('Какого размера должна быть картина над диваном?', 'Композиция — примерно две трети ширины дивана: для дивана 220 см около 145 см. Это три квадратные работы размера C в ряд или галерея из шести работ M.'),
        ('На какой высоте вешать картину над диваном?', 'Нижний край рамы — на 20–25 см выше спинки дивана. Если дивана нет, центр картины — на высоте 150–160 см от пола.'),
        ('Одна большая картина или несколько?', 'Одна крупная работа подходит для компактного дивана и минималистичного интерьера. Над длинным диваном лучше смотрится ряд или галерея из одной серии.'),
        ('Можно ли заказать картину в другом размере?', 'Да. Любую работу из каталога можно сделать в другом размере, раме и с другим паспарту — менеджер подскажет варианты и цену.'),
        ('Можно ли подобрать картины под мою гостиную?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
    'cta_title': 'Подберём картины под вашу гостиную', 'cta_bg': 's1-biblioteka/M1K2_13B755_6шт/3-расстановка.jpg',
}, {
    'slug': 'kartiny-dlya-kuhni', 'draft': True, 'furn': 'table',
    'title': 'Картины для кухни и столовой: какие выбрать и куда повесить | КУЛЬТКАРТИН',
    'desc': 'Какие картины подходят для кухни и столовой, какой размер выбрать над обеденным столом и где их лучше не вешать. Ботаника, вазы и травы в раме с ценами.',
    'h1': 'Картины для кухни и столовой',
    'lead': 'Ботаника, травы и античные вазы делают кухню уютнее. Разбираем, какой размер нужен над столом и буфетом и где картины лучше не вешать.',
    'hero': 's2-dalmatin/M2V1_23B5_6шт/3-расстановка.jpg#top', 'hero_alt': 'античные вазы в рамах на стене',
    'wa': 'Здравствуйте! Хочу подобрать картины для кухни.', 'cta_short': 'Подобрать под мою кухню',
    'schemes_title': 'Над столом и буфетом: четыре схемы',
    'schemes_lead': 'Над обеденным столом композиция занимает около двух третей его длины, нижний край рам — на 25–35 см выше столешницы. Над плитой и мойкой картины не вешают: пар и брызги. Работы у нас под стеклом, их легко протереть.',
    'schemes': [
        ('pairM', 'Пара над небольшим столом', 'Две работы размера M, около 35 × 45 см каждая. Ширина — около 76 см.', 'Для стола на 2–4 человек и кухонного уголка.'),
        ('row3', 'Ряд над длинным столом', 'Три квадратные работы размера C, около 48 × 48 см. Вместе — около 156 см.', 'Для стола 180 см и больше в столовой.'),
        ('grid', 'Квадрат из четырёх', 'Четыре квадратные работы размера C. Вместе — около 102 × 102 см.', 'Хорошо смотрится серия: травы, вазы, цветы.'),
        ('panel', 'Одна над буфетом', 'Горизонтальная работа размера A — 82 × 72 см с рамой.', 'Над буфетом или комодом в столовой.'),
    ],
    'looks_title': 'Три идеи для кухни',
    'looks': [
        ('s1-biblioteka/M2V1_23B5_6шт/3-расстановка.jpg#top', 'Античные вазы',
         'Серия ваз и урн в два ряда — классика для столовой. Спокойная серо-голубая палитра подходит и к дереву, и к светлым фасадам.', [50, 51, 52, 53, 54, 55]),
        ('s2-dalmatin/L1W1_11B655_4шт/3-расстановка.jpg#top', 'Травы в сепии',
         'Тёплая ботаника в тёмных рамах: работает на кухне в деревенском и современном стиле.', [102, 113, 133]),
        ('s3-derevo/C1W1_09B6_3шт/3-расстановка.jpg#top', 'Рододендрон и магнолия',
         'Квадратные ботанические иллюстрации — свежий акцент над столом или открытыми полками.', [82, 83, 84]),
    ],
    'pick_title': 'Подойдут для кухни',
    'pick_sub': 'Ботаника, травы, вазы, цветы и птицы. Каждую работу можно заказать в другом размере и оформлении.',
    'works': [50, 53, 99, 110, 82, 83, 70, 9, 114, 30, 36, 62],
    'faq': [
        ('Какие картины повесить на кухне?', 'Спокойные и «съедобные» сюжеты: ботаника, травы, цветы, вазы, птицы. Они поддерживают тему дома и не утомляют.'),
        ('Можно ли вешать картину над плитой или мойкой?', 'Лучше нет: пар, жир и брызги. Выберите стену над столом, буфетом или открытыми полками.'),
        ('Какого размера картину повесить над обеденным столом?', 'Около двух третей длины стола: над столом 120 см — пара работ M, над столом 180 см — ряд из трёх квадратных C.'),
        ('Как ухаживать за картиной на кухне?', 'Наши работы оформлены под стеклом — достаточно протереть его мягкой влажной тканью.'),
        ('Можно ли подобрать картины под мою кухню?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
    'cta_title': 'Подберём картины под вашу кухню', 'cta_bg': 's3-derevo/X1V1_11B6_4шт/3-расстановка.jpg',
}, {
    'slug': 'kartiny-v-prihozhuyu', 'draft': True, 'furn': 'console',
    'title': 'Картины в прихожую и коридор: размер, высота, идеи развески | КУЛЬТКАРТИН',
    'desc': 'Какие картины повесить в прихожей и коридоре, на какой высоте и какого размера. Вертикальные пары, работы над консолью и ряды вдоль стены — с ценами.',
    'h1': 'Картины в прихожую',
    'lead': 'Прихожая — первое, что видят гости. Узкие стены, консоль и длинный коридор требуют своих приёмов: разбираем размеры и развеску на примерах из каталога.',
    'hero': 's1-biblioteka/X1W1_21BY_4шт/3-расстановка.jpg#top', 'hero_alt': 'графичные орхидеи в рамах на стене',
    'wa': 'Здравствуйте! Хочу подобрать картины в прихожую.', 'cta_short': 'Подобрать под мою прихожую',
    'schemes_title': 'Прихожая и коридор: четыре схемы',
    'schemes_lead': 'Центр картины в прихожей — на высоте 150–160 см от пола, на уровне глаз. Над консолью нижний край рамы — на 25–30 см выше столешницы. Между рамами — 5–8 см.',
    'schemes': [
        ('column', 'Вертикальная пара', 'Две работы размера M (около 35 × 45 см) одна над другой.', 'Для узкой стены, простенка у двери или зеркала.'),
        ('pairM', 'Пара над консолью', 'Две работы размера M рядом. Ширина — около 76 см.', 'Для консоли или комода шириной около метра.'),
        ('panel', 'Одна крупная над консолью', 'Горизонтальная работа размера A — 82 × 72 см с рамой.', 'Встречает гостей и задаёт тон всему дому.'),
        ('row3', 'Ряд вдоль коридора', 'Три квадратные работы размера C, около 48 × 48 см, с равным шагом.', 'Для длинного коридора: стена перестаёт быть пустой.'),
    ],
    'looks_title': 'Три идеи для прихожей',
    'looks': [
        ('s2-dalmatin/J1W1_02B5_4шт/3-расстановка.jpg#top', 'Графичные орхидеи',
         'Тонкая штриховая графика на белом — лёгкое решение для небольшой светлой прихожей.', [95, 96, 97, 98]),
        ('s3-derevo/M1W1_11B655_4шт/3-расстановка.jpg#top', 'Фасады на тёмной стене',
         'Архитектурная графика держит строгую прихожую в неоклассике и сочетается с латунью и камнем.', [38, 39, 40, 41]),
        ('s2-dalmatin/A2P1_01BA_chrysler_3шт/3-расстановка.jpg#top', 'Город в монохроме',
         'Чёрно-белые фотографии Нью-Йорка — для коридора в современной квартире.', [19, 20, 21]),
    ],
    'pick_title': 'Подойдут для прихожей',
    'pick_sub': 'Графика, архитектура, города и силуэты растений. Каждую работу можно заказать в другом размере и оформлении.',
    'works': [19, 38, 26, 29, 13, 126, 95, 103, 134, 60, 42, 89],
    'faq': [
        ('На какой высоте вешать картину в прихожей?', 'Центр картины — на высоте 150–160 см от пола. Над консолью нижний край рамы — на 25–30 см выше столешницы.'),
        ('Какую картину повесить на узкую стену?', 'Вертикальную или вертикальную пару одна над другой — работы размера M или S.'),
        ('Как оформить длинный коридор?', 'Рядом из трёх–пяти работ одной серии с равным шагом. Так коридор выглядит собранным, а не пустым.'),
        ('Можно ли заказать картину в другом размере?', 'Да. Любую работу из каталога можно сделать в другом размере, раме и с другим паспарту — менеджер подскажет варианты и цену.'),
        ('Можно ли подобрать картины под мою прихожую?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
    'cta_title': 'Подберём картины для вашей прихожей', 'cta_bg': 's2-dalmatin/X1V1_01B844_6шт/3-расстановка.jpg',
}, {
    'slug': 'kartiny-dlya-kabineta', 'draft': True, 'furn': 'desk',
    'title': 'Картины для кабинета: постеры, фотографии и графика в раме | КУЛЬТКАРТИН',
    'desc': 'Какие картины повесить в кабинете и домашнем офисе: ретро-постеры гонок, города, архитектура. Размеры над рабочим столом и идеи развески — с ценами.',
    'h1': 'Картины для кабинета',
    'lead': 'Кабинет — место с характером: ретро-гонки, города Италии, архитектура и побережья. Разбираем, что повесить над рабочим столом и за спиной — для видеозвонков.',
    'hero': 's1-biblioteka/A2P1_02BA_4шт/3-расстановка.jpg', 'hero_alt': 'постеры городов Италии в кабинете с библиотекой',
    'wa': 'Здравствуйте! Хочу подобрать картины для кабинета.', 'cta_short': 'Подобрать под мой кабинет',
    'schemes_title': 'Над рабочим столом: четыре схемы',
    'schemes_lead': 'Над рабочим столом нижний край рам — на 25–30 см выше столешницы, композиция — около двух третей его ширины. Стена за спиной видна на видеозвонках: там хорошо работает ряд или одна крупная работа.',
    'schemes': [
        ('pair', 'Пара над столом', 'Две вертикальные работы размера X, каждая 54,5 × 64,5 см с рамой. Около 115 см.', 'Для стола 140–160 см.'),
        ('grid', 'Квадрат из четырёх постеров', 'Четыре работы одной серии, около 48 × 48 см. Вместе — около 102 × 102 см.', 'Серия гонок или городов — как коллекция.'),
        ('row3', 'Ряд за спиной', 'Три работы в ряд, около 156 см.', 'Красивый фон для видеозвонков.'),
        ('panel', 'Одна крупная', 'Горизонтальная работа размера A — 82 × 72 см с рамой.', 'Над узким столом или за креслом.'),
    ],
    'looks_title': 'Три кабинета — три характера',
    'looks': [
        ('s1-biblioteka/A2P1_01BA_races_4шт/3-расстановка.jpg', 'Ретро-гонки',
         'Четыре фотографии Гран-при 1950-х рядом с книжными полками — кабинет с характером и любовью к деталям.', [22, 23, 24, 25]),
        ('s3-derevo/A2P1_02BA_4шт/3-расстановка.jpg', 'Города Италии',
         'Флоренция, Милан, Рим и Венеция в графике — спокойная серия для кабинета в тёплом дереве.', [26, 27, 28, 29]),
        ('s2-dalmatin/M1W2_01B5_4шт/3-расстановка.jpg', 'Побережье',
         'Морские пейзажи в светлых рамах — воздух и простор для домашнего офиса.', [42, 43, 44, 45]),
    ],
    'pick_title': 'Подойдут для кабинета',
    'pick_sub': 'Гонки, города, архитектура, побережья и графика. Каждую работу можно заказать в другом размере и оформлении.',
    'works': [22, 23, 24, 25, 19, 26, 27, 38, 42, 44, 89, 137],
    'faq': [
        ('Какие картины повесить в кабинете?', 'Сюжеты с характером и смыслом для вас: ретро-фотографии гонок, города, архитектура, побережья, графика. Лучше всего смотрится серия из 3–4 работ.'),
        ('Что повесить за спиной для видеозвонков?', 'Ряд из трёх работ или одну крупную горизонтальную. Спокойные тона не отвлекают собеседника.'),
        ('На какой высоте вешать картину над рабочим столом?', 'Нижний край рамы — на 25–30 см выше столешницы, композиция — около двух третей ширины стола.'),
        ('Можно ли заказать картину в другом размере?', 'Да. Любую работу из каталога можно сделать в другом размере, раме и с другим паспарту — менеджер подскажет варианты и цену.'),
        ('Можно ли подобрать картины под мой кабинет?', 'Да. Пришлите фото стены в WhatsApp — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.'),
    ],
    'cta_title': 'Подберём картины для вашего кабинета', 'cta_bg': 's3-derevo/A2P1_01BA_chrysler_3шт/3-расстановка.jpg',
}]


CSS = """<style>
.idea-hero{position:relative;min-height:min(56vh,500px);display:grid;align-items:end;color:#fff;overflow:hidden;background:#2a1f1b}
.idea-hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.idea-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,12,10,.72) 0%,rgba(20,12,10,.35) 45%,rgba(20,12,10,0) 70%)}
.idea-hero-in{position:relative;z-index:1;width:min(1180px,100%);margin:0 auto;padding:0 20px clamp(28px,4vw,52px)}
.idea-crumbs{font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.8;margin-bottom:18px}.idea-crumbs a{text-decoration:underline}
.idea-hero h1{font:500 clamp(40px,5.6vw,76px)/.95 var(--serif);margin:0 0 14px;max-width:11em}
.idea-hero p{max-width:520px;font-size:clamp(16px,1.5vw,19px);line-height:1.55;margin:0 0 26px;opacity:.92}
.btn-wa{display:inline-block;background:var(--dark);color:#fff;padding:16px 28px;font:600 12.5px/1 var(--sans);letter-spacing:.12em;text-transform:uppercase}
.btn-line{display:inline-block;border:1px solid currentColor;padding:15px 26px;font:600 12.5px/1 var(--sans);letter-spacing:.12em;text-transform:uppercase}
.idea-hero .btn-wa{background:#f7eddd;color:var(--dark)}
.idea-hero .btns{display:flex;gap:10px;flex-wrap:wrap}
.idea-wrap{width:min(1180px,100%);margin:0 auto;padding:0 20px}
.idea-facts{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--line)}
.idea-facts div{padding:clamp(22px,3vw,34px) clamp(14px,2vw,28px);border-right:1px solid var(--line)}.idea-facts div:last-child{border-right:0}
.idea-facts b{display:block;font:400 clamp(40px,5vw,64px)/1 var(--serif);color:var(--dark);font-variant-numeric:lining-nums}
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
.idea-cta{position:relative;color:#f3e8e8;text-align:center;padding:clamp(80px,12vw,160px) 20px;overflow:hidden;background:#2a1f1b}.idea-cta>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 25%}.idea-cta::after{content:"";position:absolute;inset:0;background:rgba(32,14,14,.62)}.idea-cta>*:not(img){position:relative;z-index:1}.idea-marquee{overflow:hidden;padding:8px 0 clamp(48px,7vw,96px);border-bottom:1px solid var(--line);-webkit-mask:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}.idea-marquee-track{display:flex;gap:clamp(18px,2.5vw,36px);width:max-content;align-items:flex-end;animation:ideaMarq 70s linear infinite}.idea-marquee:hover .idea-marquee-track{animation-play-state:paused}.idea-marquee img{height:clamp(150px,18vw,240px);width:auto;display:block;filter:drop-shadow(0 10px 14px rgba(60,40,30,.16))}@keyframes ideaMarq{to{transform:translateX(-50%)}}@media(prefers-reduced-motion:reduce){.idea-marquee-track{animation:none}.idea-marquee{overflow-x:auto}}.idea-text{border-bottom:0!important}.idea-schemes{padding:clamp(48px,7vw,96px) 0;border-bottom:1px solid var(--line)}.idea-schemes-head{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);align-items:end;gap:clamp(24px,5vw,80px);margin-bottom:clamp(28px,4vw,48px)}.idea-schemes-head h2{font:500 clamp(32px,4vw,52px)/1.02 var(--serif);margin:0}.idea-schemes-head p{font-size:17px;line-height:1.75;margin:0;color:#2c2725;max-width:62ch}.scheme-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(12px,1.6vw,20px)}.scheme{background:#fff;border:1px solid var(--line);display:grid;grid-template-rows:auto 1fr}.scheme svg,.scheme>img{width:100%;aspect-ratio:4/3;display:block;background:#efe9e1;object-fit:cover}.scheme div{padding:18px 18px 20px}.scheme h3{font:500 22px/1.15 var(--serif);margin:0 0 8px}.scheme p{margin:0 0 8px;font-size:14.5px;line-height:1.55;color:#2c2725}.scheme p+p{color:#6f6762;margin:0}@media(max-width:1000px){.scheme-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.idea-schemes-head{grid-template-columns:1fr}}@media(max-width:520px){.scheme-grid{grid-template-columns:1fr}}.scheme-grid.photo{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:700px){.scheme-grid.photo{grid-template-columns:1fr}}
html body .idea-cta h2{font:500 clamp(32px,4vw,52px)/1.05 var(--serif);margin:0 auto 18px;max-width:12.5em;text-wrap:balance;color:#fff}
.idea-cta p{max-width:560px;margin:0 auto 26px;line-height:1.6;opacity:.85}
.idea-cta .btn-wa{background:#f7eddd;color:var(--dark)}
@media(max-width:900px){.idea-text,.idea-how,.idea-faq,.look{grid-template-columns:1fr}.look{direction:ltr!important}.idea-scheme{position:static}.idea-facts{grid-template-columns:1fr}.idea-facts div{border-right:0;border-bottom:1px solid var(--line)}.idea-facts div:last-child{border-bottom:0}}
@media(max-width:520px){.look-items{grid-template-columns:1fr}.idea-hero{min-height:62vh}}
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


def scheme_svg(kind, furn='bed'):
    """Временный эскиз развески (пока нет иллюстраций Анны). Масштаб 1,1 px/см.
    furn: bed — кровать 160 см, sofa — диван 220 см, table — обеденный стол 160 см, console — консоль 100 см, desk — рабочий стол 140 см."""
    k = 1.1; cx = 200; floor = 262
    frame = lambda x, y, w, h, art: (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#fbf8f3" stroke="#b39466" stroke-width="2.2"/>'
                                     f'<rect x="{x + w * .2:.1f}" y="{y + h * .2:.1f}" width="{w * .6:.1f}" height="{h * .6:.1f}" fill="{art}"/>')
    g = []
    if furn == 'bed':
        fw = 160 * k; top = 168
        if kind == 'sides':
            for sx in (cx - fw / 2 - 58, cx + fw / 2 + 8):
                g.append(f'<rect x="{sx:.1f}" y="{floor - 58}" width="50" height="58" rx="3" fill="#cbbba6"/>')
        g.append(f'<rect x="{cx - fw / 2:.1f}" y="{top}" width="{fw:.1f}" height="{floor - top - 18}" rx="12" fill="#d8cdbf"/>')
        g.append(f'<rect x="{cx - fw / 2 - 6:.1f}" y="{top + 44}" width="{fw + 12:.1f}" height="{floor - top - 44}" rx="8" fill="#f4eee6"/>')
        g.append(f'<rect x="{cx - fw / 2 + 14:.1f}" y="{top + 26}" width="{fw / 2 - 22:.1f}" height="24" rx="9" fill="#fbf8f3"/><rect x="{cx + 8:.1f}" y="{top + 26}" width="{fw / 2 - 22:.1f}" height="24" rx="9" fill="#fbf8f3"/>')
    elif furn == 'sofa':
        k = .9; fw = 220 * k; top = 180
        g.append(f'<rect x="{cx - fw / 2:.1f}" y="{top}" width="{fw:.1f}" height="{floor - top - 8}" rx="14" fill="#cdbfae"/>')
        g.append(f'<rect x="{cx - fw / 2 - 8:.1f}" y="{top + 30}" width="26" height="{floor - top - 30}" rx="10" fill="#bfae99"/><rect x="{cx + fw / 2 - 18:.1f}" y="{top + 30}" width="26" height="{floor - top - 30}" rx="10" fill="#bfae99"/>')
        g.append(f'<rect x="{cx - fw / 2 + 18:.1f}" y="{top + 40}" width="{fw - 36:.1f}" height="28" rx="8" fill="#e6dccf"/>')
    elif furn == 'table':
        fw = 160 * k; top = 196
        g.append(f'<rect x="{cx - fw / 2:.1f}" y="{top}" width="{fw:.1f}" height="8" rx="2" fill="#a88f74"/><rect x="{cx - fw / 2 + 10:.1f}" y="{top + 8}" width="6" height="{floor - top - 8}" fill="#a88f74"/><rect x="{cx + fw / 2 - 16:.1f}" y="{top + 8}" width="6" height="{floor - top - 8}" fill="#a88f74"/>')
        for chx in (cx - 55, cx + 25):
            g.append(f'<rect x="{chx:.1f}" y="{top - 20}" width="30" height="{floor - top + 20}" rx="6" fill="#d8cdbf" opacity=".9"/>')
    elif furn == 'console':
        fw = 100 * k; top = 190
        g.append(f'<rect x="{cx - fw / 2:.1f}" y="{top}" width="{fw:.1f}" height="10" rx="2" fill="#a88f74"/><rect x="{cx - fw / 2 + 6:.1f}" y="{top + 10}" width="5" height="{floor - top - 10}" fill="#a88f74"/><rect x="{cx + fw / 2 - 11:.1f}" y="{top + 10}" width="5" height="{floor - top - 10}" fill="#a88f74"/>'
                 f'<ellipse cx="{cx + 28:.1f}" cy="{top - 12}" rx="9" ry="13" fill="#d8cdbf"/>')
    else:  # desk
        fw = 140 * k; top = 196
        g.append(f'<rect x="{cx - fw / 2:.1f}" y="{top}" width="{fw:.1f}" height="9" rx="2" fill="#8f7a64"/><rect x="{cx - fw / 2 + 6:.1f}" y="{top + 9}" width="40" height="{floor - top - 9}" fill="#a88f74"/><rect x="{cx + fw / 2 - 12:.1f}" y="{top + 9}" width="6" height="{floor - top - 9}" fill="#8f7a64"/>'
                 f'<rect x="{cx + 12:.1f}" y="{top - 26}" width="34" height="22" rx="2" fill="#d8cdbf"/><rect x="{cx - 34:.1f}" y="{top - 30}" width="4" height="30" fill="#8f7a64"/><path d="M{cx - 44:.1f} {top - 30}h24l-6 -12h-12z" fill="#e6dccf"/>')
    bottom = top - (25 if furn in ('bed', 'sofa') else 30) * k
    gap = 6 * k
    arts = ['#c9cdb4', '#d7c2a5', '#bfc6c4', '#d9cbb8', '#cfc4b4', '#c4cbbd']
    label, lx1, lx2, ly = '', 0, 0, 0
    def row(n, w, h, y_bottom, label_text):
        x0 = cx - (n * w + (n - 1) * gap) / 2
        for i in range(n):
            g.append(frame(x0 + i * (w + gap), y_bottom - h, w, h, arts[i % len(arts)]))
        return label_text, x0, x0 + n * w + (n - 1) * gap, y_bottom - h - 10
    if kind == 'pair':
        label, lx1, lx2, ly = row(2, 54.5 * k, 64.5 * k, bottom, f'≈ {round(2 * 54.5 + 6)} см')
    elif kind == 'pairM':
        label, lx1, lx2, ly = row(2, 35 * k, 45 * k, bottom, '≈ 76 см')
    elif kind == 'row3':
        label, lx1, lx2, ly = row(3, 48 * k, 48 * k, bottom, '≈ 156 см')
    elif kind == 'grid':
        w = 48 * k
        row(2, w, w, bottom, '')
        label, lx1, lx2, ly = row(2, w, w, bottom - w - gap, '≈ 102 см')
    elif kind == 'grid6':
        w, h = 35 * k, 45 * k
        row(3, w, h, bottom, '')
        label, lx1, lx2, ly = row(3, w, h, bottom - h - gap, '≈ 117 см')
    elif kind == 'panel':
        label, lx1, lx2, ly = row(1, 82 * k, 72 * k, bottom, '82 см')
    elif kind == 'column':
        w, h = 35 * k, 45 * k
        row(1, w, h, bottom, '')
        label, lx1, lx2, ly = row(1, w, h, bottom - h - gap, 'вертикальная пара')
    else:  # sides
        w, h = 35 * k, 45 * k; fw = 160 * k
        for sx in (cx - fw / 2 - 33, cx + fw / 2 + 33):
            b0 = floor - 58 - 40 * k
            g += [frame(sx - w / 2, b0 - h, w, h, arts[0]), frame(sx - w / 2, b0 - 2 * h - gap, w, h, arts[3])]
        label, lx1, lx2, ly = 'по 2 работы M', cx - fw / 2 - 33 - w / 2, cx - fw / 2 - 33 + w / 2, floor - 58 - 40 * k - 2 * h - gap - 10
    dim = (f'<path d="M{lx1:.1f} {ly:.1f}H{lx2:.1f}M{lx1:.1f} {ly - 4:.1f}v8M{lx2:.1f} {ly - 4:.1f}v8" stroke="#8a5a4a" stroke-width="1"/>'
           f'<text x="{(lx1 + lx2) / 2:.1f}" y="{ly - 7:.1f}" text-anchor="middle" font-family="Manrope,Arial,sans-serif" font-size="11" fill="#8a5a4a">{label}</text>')
    return (f'<svg viewBox="0 0 400 300" role="img" aria-hidden="true"><rect width="400" height="300" fill="#efe9e1"/>'
            f'<rect y="{floor}" width="400" height="{300 - floor}" fill="#e2d8cb"/>{"".join(g)}{dim}</svg>')


def marquee(n=22):
    """Лента работ из библиотеки (dist/assets/lib): разные темы, без детской и «стиля» (там флаконы с логотипами)."""
    page_html = open(os.path.join(DIST, 'biblioteka.html'), encoding='utf-8').read()
    data = json.loads(re.search(r'const DATA=(\[.*?\]);', page_html, re.S).group(1))
    seen, picked = set(), []
    for item in data:
        key = (item.get('m'), item.get('t'))
        if item.get('m') in ('kids', 'style') or key in seen:
            continue
        seen.add(key); picked.append(item)
    by_kind = {}
    for item in picked:
        by_kind.setdefault(item['m'], []).append(item)
    mixed = []
    while len(mixed) < n and any(by_kind.values()):
        for k in list(by_kind):
            if by_kind[k]:
                mixed.append(by_kind[k].pop(0))
    imgs = ''.join(f'<img src="{html.escape(i["img"])}" alt="" loading="lazy" width="{i["w"]}" height="{i["h"]}">' for i in mixed[:n])
    return f'<div class="idea-marquee" aria-hidden="true"><div class="idea-marquee-track">{imgs}{imgs}</div></div>'


SHORT = re.compile(r'(?<![\w-])([А-Яа-яЁёA-Za-z]{1,3}|\d+|—)\s+(?=\S)')


def nbsp(fragment):
    """Без висящих предлогов: неразрывный пробел после коротких слов и чисел — только в тексте, не в атрибутах."""
    return re.sub(r'>([^<]+)<', lambda m: '>' + SHORT.sub(lambda x: x.group(1) + '&nbsp;', m.group(1)).replace(' —', '&nbsp;—') + '<', fragment)


def img_out(slug, src, name, size):
    from PIL import Image
    out = os.path.join(DIST, 'idei', slug, 'img')
    os.makedirs(out, exist_ok=True)
    crop = None
    if '#top' in src:
        src, crop = src.split('#')[0], .58
    im = Image.open(os.path.join(MOCK, src)).convert('RGB')
    if crop:
        im = im.crop((0, 0, im.width, int(im.height * crop)))
    im.thumbnail(size)
    name = name.replace('.webp', '-' + hashlib.md5((src + str(crop)).encode()).hexdigest()[:6] + '.webp')  # новое фото — новое имя, без старого кеша
    im.save(os.path.join(out, name), 'WEBP', quality=82)
    return f'idei/{slug}/img/{name}'


def money_pair(w):
    pre = 'от ' if w['from'] else ''
    return f'{pre}{b.money(w["kzt"])} ₸', f'{pre}{b.money(w["rub"])} ₽'


SCHEME_FRAMES = {  # размеры с рамой, см
    'pair': [(54.5, 64.5)] * 2, 'panel': [(82, 72)], 'grid': [(48, 48)] * 4,
    'row3': [(48, 48)] * 3, 'pairM': [(35, 45)] * 2,
}


def scheme_photo(kind, img, g):
    """Схема развески поверх фото интерьера: контуры рам с размерами и размерные линии.
    g: k — px на см, cx — центр мебели, top — верх изголовья/спинки (px), w — ширина мебели (см), stands — центры тумб, vb — кадр."""
    k, cx, top, gap, lift = g['k'], g['cx'], g['top'], 6, 25
    base = top - lift * k
    C, F = '#3a2a22', "font-family=\"Manrope,Arial,sans-serif\" font-size=\"34\" fill=\"#3a2a22\" text-anchor=\"middle\""
    num = lambda v: (f'{v:g}').replace('.', ',')
    fr = []  # x, y, w, h (px), подпись

    def row(sizes, bottom, x0=None):
        tw = sum(w for w, h in sizes) + gap * (len(sizes) - 1)
        x = (cx - tw * k / 2) if x0 is None else x0
        for w, h in sizes:
            fr.append((x, bottom - h * k, w * k, h * k, f'{num(w)}×{num(h)} см')); x += (w + gap) * k
        return tw
    if kind == 'sides':
        for sx in g['stands']:
            for i in range(2):
                b = base - i * (45 + gap) * k
                fr.append((sx - 35 * k / 2, b - 45 * k, 35 * k, 45 * k, '35×45 см'))
    elif kind == 'grid':
        row([(48, 48)] * 2, base); row([(48, 48)] * 2, base - (48 + gap) * k)
    else:
        row(SCHEME_FRAMES[kind], base)
    out = [f'<image href="{img}" x="0" y="0" width="{g["W"]}" height="{g["H"]}"/>']
    for x, y, w, h, t in fr:
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="rgba(255,255,255,.28)" stroke="{C}" stroke-width="4"/>'
                   f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + 10:.0f}" font-family="Manrope,Arial,sans-serif" font-size="{min(34, w * .88 / (len(t) * .56)):.0f}" fill="{C}" text-anchor="middle">{t}</text>')

    def hdim(x1, x2, y, label, ly=None):
        out.append(f'<path d="M{x1:.0f} {y:.0f}H{x2:.0f}M{x1:.0f} {y - 12:.0f}v24M{x2:.0f} {y - 12:.0f}v24" stroke="{C}" stroke-width="3" fill="none"/>'
                   f'<text x="{(x1 + x2) / 2:.0f}" y="{(ly if ly is not None else y - 20):.0f}" {F}>{label}</text>')
    tops = min(y for x, y, w, h, t in fr)
    if kind == 'sides':
        for sx in g['stands']:
            x1 = sx - 35 * k / 2; hdim(x1, x1 + 35 * k, tops - 30, '35 см')
    else:
        x1, x2 = min(f[0] for f in fr), max(f[0] + f[2] for f in fr)
        hdim(x1, x2, tops - 70, f'{num(round((x2 - x1) / k, 1))} см')
        cols = sorted({round(f[0]) for f in fr})
        for a, b2 in zip(cols, cols[1:]):  # зазоры между рамами
            ga = next(f for f in fr if round(f[0]) == a); gx = ga[0] + ga[2]
            out.append(f'<path d="M{gx:.0f} {tops - 22:.0f}H{b2:.0f}" stroke="{C}" stroke-width="3"/>')
            out.append(f'<text x="{(gx + b2) / 2:.0f}" y="{tops - 30:.0f}" font-family="Manrope,Arial,sans-serif" font-size="30" fill="{C}" text-anchor="middle">{gap} см</text>')
    # высота над изголовьем
    rx = (min(f[0] for f in fr) + 35 * k + 34) if kind == 'sides' else max(f[0] + f[2] for f in fr) + 34
    out.append(f'<path d="M{rx:.0f} {base:.0f}V{top:.0f}M{rx - 10:.0f} {base:.0f}h20M{rx - 10:.0f} {top:.0f}h20" stroke="{C}" stroke-width="3"/>'
               f'<text x="{rx + 14:.0f}" y="{(base + top) / 2 + 12:.0f}" font-family="Manrope,Arial,sans-serif" font-size="30" fill="{C}">{lift} см</text>')
    # ширина мебели
    hw = g['w'] * k / 2
    hdim(cx - hw, cx + hw, top - 14, f'{g["label"]} {g["w"]} см', top - 30)
    return f'<svg viewBox="{g["vb"]}" role="img" aria-label="Схема развески">{"".join(out)}</svg>'


# стиль по мотивам 12 Storeez (текст, теги, вопросы, кнопки), утвердила Анна 2026-11-25
STYLE12 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'idei-style.html'), encoding='utf-8').read()


def page(template, a, works):
    e = lambda s: html.escape(s or '', quote=True)
    url = f'{SITE}/idei/{a["slug"]}/'
    by = {w['id']: w for w in works}
    picked = [by[i] for i in a['works'] if i in by]
    wa = WA + urllib.parse.quote(a['wa'])
    hero = img_out(a['slug'], a['hero'], 'hero.webp', (2000, 1600))
    cta_bg = img_out(a['slug'], a['cta_bg'], 'cta.webp', (1800, 1400))
    sbg = img_out(a['slug'], a['scheme_bg'][0], 'schemes.webp', (2000, 1500)) if a.get('scheme_bg') else None
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
    t = t.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n' + CSS + '\n' + STYLE12 + '\n</head>', 1)

    paras = lambda ps: ''.join(f'<p>{e(p)}</p>' for p in ps)
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(ans)}</p></details>' for q, ans in a['faq'])
    main = (f'<main>'
            f'<section class="idea-hero"><img src="{hero}" alt="{e(a["h1"])}: {e(a["hero_alt"])}" fetchpriority="high">'
            f'<div class="idea-hero-in"><div class="idea-crumbs"><a href="index.html">Главная</a> · Идеи для интерьера</div>'
            f'<h1>{e(a["h1"])}</h1><p>{e(a["lead"])}</p><div class="btns"><a class="btn-wa" href="#podborka">Смотреть подборку</a>'
            f'<a class="btn-line" href="{wa}" target="_blank" rel="noopener">{e(a["cta_short"])}</a></div></div></section>'
            + '<div class="idea-wrap">'
            + f'<section class="idea-schemes"><div class="idea-schemes-head"><div><div class="idea-kicker">Размер и развеска</div><h2>{e(a["schemes_title"]).replace(": ", ":<br>", 1)}</h2></div><p>{e(a["schemes_lead"])}</p></div>'
            + f'<div class="scheme-grid{" photo" if sbg else ""}">' + ''.join(
                f'<article class="scheme">{scheme_photo(k, sbg, a["scheme_bg"][1]) if sbg else scheme_svg(k, a.get("furn", "bed"))}<div><h3>{e(t)}</h3><p>{e(sz)}</p><p>{e(note)}</p></div></article>' for k, t, sz, note in a['schemes'])
            + '</div></section>'
            + f'<section class="idea-looks"><div><div class="idea-kicker">Образы</div><h2>{e(a["looks_title"])}</h2></div>{looks}</section>'
            + f'<section class="idea-pick" id="podborka"><div class="idea-pick-head"><div><div class="idea-kicker">Подборка</div><h2>{e(a["pick_title"])}</h2>'
            f'<p>{e(a["pick_sub"])}</p></div>'
            f'<a href="index.html#catalog">Весь каталог&nbsp;→</a></div>'
            f'<div class="catalog" id="catalog"><div class="products" id="products">\n{b.catalog_cards(picked)}\n</div></div></section>'
            f'<section class="idea-faq"><div><div class="idea-kicker">Вопросы</div><h2>Частые вопросы</h2></div><div>{faq}</div></section></div>'
            f'<section class="idea-cta"><img src="{cta_bg}" alt="" loading="lazy"><h2>{e(a["cta_title"])}</h2><p>Пришлите фото стены — менеджер бесплатно подберёт работы, размеры и развеску и пришлёт коллаж с ценами.</p>'
            f'<a class="btn-wa" href="{wa}" target="_blank" rel="noopener">Написать в WhatsApp</a></section></main>')
    main = nbsp(main)
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

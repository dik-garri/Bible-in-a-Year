#!/usr/bin/env python3
"""
Скачивает Юбилейное издание Синодального перевода (Свет на Востоке, 2008)
с bible.by по одной главе с сохранением прогресса.

Источник: https://bible.by/jbl/
URL-паттерн: https://bible.by/jbl/{книга}/{глава}/

Использование:
  python3 download_jbl.py                          # все 66 книг
  python3 download_jbl.py --from 1 --to 7          # книги 1-7
  python3 download_jbl.py --from 1 --to 7 -o p1.json  # в указанный файл
"""

import argparse
import json
import re
import os
import time
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, '..', 'viewer', 'data', 'jbl.json')
BASE_URL = 'https://bible.by/jbl'
DELAY = 0.3  # пауза между запросами (секунды)

CHAPTERS_PER_BOOK = [
    50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
    22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
    12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
    1, 4, 7, 3, 3, 3, 2, 14, 4,
    28, 16, 24, 21, 28, 16, 16, 13, 6, 6,
    4, 4, 5, 3, 6, 4, 3, 1, 13, 5,
    5, 3, 5, 1, 1, 1, 22
]

# Маппинг: наш порядок книг (стандартный протестантский) → номер книги на bible.by
# ВЗ (1-39) совпадает, НЗ отличается: на bible.by соборные послания идут перед Павловыми
# Наш: ..., Рим(45), 1Кор(46), ..., Флм(57), Евр(58), Иак(59), ..., Иуд(65), Откр(66)
# bible.by: ..., Иак(45), 1Пет(46), ..., Иуд(51), Рим(52), ..., Евр(65), Откр(66)
BIBLE_BY_BOOK_NUM = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39,
    40, 41, 42, 43, 44,       # Мф, Мк, Лк, Ин, Деян
    52, 53, 54, 55, 56,       # Рим, 1Кор, 2Кор, Гал, Еф
    57, 58, 59, 60, 61,       # Флп, Кол, 1Фес, 2Фес, 1Тим
    62, 63, 64, 65,           # 2Тим, Тит, Флм, Евр
    45, 46, 47, 48, 49,       # Иак, 1Пет, 2Пет, 1Ин, 2Ин
    50, 51,                   # 3Ин, Иуд
    66,                       # Откр
]

BOOK_ABBREVS = [
    'gn', 'ex', 'lv', 'nm', 'dt', 'js', 'jud', 'rt', '1sm', '2sm',
    '1kgs', '2kgs', '1ch', '2ch', 'ezr', 'ne', 'et', 'job', 'ps', 'prv',
    'ec', 'so', 'is', 'jr', 'lm', 'ez', 'dn', 'ho', 'jl', 'am',
    'ob', 'jn', 'mi', 'na', 'hk', 'zp', 'hg', 'zc', 'ml',
    'mt', 'mk', 'lk', 'jo', 'act', 'rm', '1co', '2co', 'gl', 'eph',
    'ph', 'cl', '1ts', '2ts', '1tm', '2tm', 'tt', 'phm', 'hb', 'jm',
    '1pe', '2pe', '1jo', '2jo', '3jo', 'jd', 're'
]

BOOK_NAMES = [
    'Бытие', 'Исход', 'Левит', 'Числа', 'Второзаконие',
    'Иисус Навин', 'Судьи', 'Руфь', '1 Царств', '2 Царств',
    '3 Царств', '4 Царств', '1 Паралипоменон', '2 Паралипоменон', 'Ездра',
    'Неемия', 'Есфирь', 'Иов', 'Псалтирь', 'Притчи',
    'Екклесиаст', 'Песня Песней', 'Исаия', 'Иеремия', 'Плач Иеремии',
    'Иезекииль', 'Даниил', 'Осия', 'Иоиль', 'Амос',
    'Авдий', 'Иона', 'Михей', 'Наум', 'Аввакум',
    'Софония', 'Аггей', 'Захария', 'Малахия',
    'Матфея', 'Марка', 'Луки', 'Иоанна', 'Деяния',
    'Римлянам', '1 Коринфянам', '2 Коринфянам', 'Галатам', 'Ефесянам',
    'Филиппийцам', 'Колоссянам', '1 Фессалоникийцам', '2 Фессалоникийцам', '1 Тимофею',
    '2 Тимофею', 'Титу', 'Филимону', 'Евреям', 'Иакова',
    '1 Петра', '2 Петра', '1 Иоанна', '2 Иоанна', '3 Иоанна',
    'Иуды', 'Откровение'
]


def load_progress():
    """Загружает существующий прогресс"""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_progress(bible):
    """Сохраняет текущий прогресс"""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bible, f, ensure_ascii=False)


def parse_verses(html):
    """Извлекает стихи из HTML-страницы bible.by"""
    divs = re.findall(r'<div id="(\d+)">(.*?)</div>', html, re.DOTALL)
    verses = []
    for verse_num, content in divs:
        # Убираем подзаголовки разделов
        text = re.sub(r'<span class="subtitle">.*?</span>', '', content, flags=re.DOTALL)
        # Убираем номер стиха
        text = re.sub(r'<sup>\d+</sup>', '', text)
        # Убираем оставшиеся HTML-теги (em, i, b и т.д.)
        text = re.sub(r'<[^>]+>', '', text)
        # Нормализуем пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            verses.append(text)
    return verses


def download_chapter(book_num, chapter):
    """Скачивает одну главу"""
    url = f'{BASE_URL}/{book_num}/{chapter}/'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; BibleDownloader/1.0)'
    })
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    return parse_verses(html)


def download_book(book_num):
    """Скачивает одну книгу (book_num — наш стандартный номер 1-66)"""
    bible_by_num = BIBLE_BY_BOOK_NUM[book_num - 1]
    chapters_count = CHAPTERS_PER_BOOK[book_num - 1]
    chapters = []

    for ch in range(1, chapters_count + 1):
        verses = download_chapter(bible_by_num, ch)
        if not verses:
            raise ValueError(f'Глава {ch} пустая (bible.by книга {bible_by_num})')
        chapters.append(verses)
        time.sleep(DELAY)

    return {
        'abbrev': BOOK_ABBREVS[book_num - 1],
        'chapters': chapters
    }


def download_range(from_book, to_book, output_file):
    """Скачивает диапазон книг [from_book, to_book] включительно"""
    bible = []

    # Загружаем прогресс если файл уже есть
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            bible = json.load(f)

    start_book = from_book + len(bible)
    total_chapters = sum(CHAPTERS_PER_BOOK[i] for i in range(from_book - 1, to_book))

    if start_book > to_book:
        print(f'✅ Книги {from_book}-{to_book} уже скачаны!')
        return

    done_chapters = sum(CHAPTERS_PER_BOOK[i] for i in range(from_book - 1, start_book - 1))
    print(f'Книги {from_book}-{to_book} ({total_chapters} глав, скачано {done_chapters})\n')

    for book_num in range(start_book, to_book + 1):
        name = BOOK_NAMES[book_num - 1]
        chapters_count = CHAPTERS_PER_BOOK[book_num - 1]

        print(f'[{book_num}/66] {name} ({chapters_count} глав)...', end=' ', flush=True)

        try:
            book = download_book(book_num)
            bible.append(book)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(bible, f, ensure_ascii=False)
            total_verses = sum(len(ch) for ch in book['chapters'])
            print(f'✓ {total_verses} стихов')
        except Exception as e:
            print(f'ОШИБКА: {e}')
            print(f'Прогресс сохранён: {len(bible)} книг')
            print('Перезапустите скрипт для продолжения.')
            return

    print(f'\n✅ Книги {from_book}-{to_book} готовы! → {output_file}')


def merge_parts(parts_dir, output_file):
    """Собирает части в один файл"""
    bible = []
    for i in range(1, 11):
        part_file = os.path.join(parts_dir, f'jbl_part{i}.json')
        if not os.path.exists(part_file):
            print(f'❌ Не найден {part_file}')
            return False
        with open(part_file, 'r', encoding='utf-8') as f:
            books = json.load(f)
        bible.extend(books)
        print(f'Часть {i}: {len(books)} книг')

    if len(bible) != 66:
        print(f'❌ Ожидалось 66 книг, получено {len(bible)}')
        return False

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bible, f, ensure_ascii=False)

    file_size = os.path.getsize(output_file) / 1024 / 1024
    print(f'\n✅ Все 66 книг собраны в {output_file} ({file_size:.1f} МБ)')
    return True


def main():
    parser = argparse.ArgumentParser(description='Скачать Юбилейное издание с bible.by')
    parser.add_argument('--from', dest='from_book', type=int, default=1, help='Начальная книга (1-66)')
    parser.add_argument('--to', dest='to_book', type=int, default=66, help='Конечная книга (1-66)')
    parser.add_argument('-o', '--output', default=None, help='Файл для сохранения')
    parser.add_argument('--merge', default=None, help='Собрать части из указанной директории')
    args = parser.parse_args()

    if args.merge:
        merge_parts(args.merge, args.output or DEFAULT_OUTPUT)
        return

    output = args.output or DEFAULT_OUTPUT
    print(f'Юбилейное издание — bible.by/jbl/')
    print(f'Пауза между запросами: {DELAY}с')
    download_range(args.from_book, args.to_book, output)


if __name__ == '__main__':
    main()

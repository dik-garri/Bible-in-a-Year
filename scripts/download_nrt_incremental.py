#!/usr/bin/env python3
"""
Скачивает НРП по одной книге с сохранением прогресса
"""

import json
import urllib.request
import os

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'nrt.json')

CHAPTERS_PER_BOOK = [
    50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
    22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
    12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
    1, 4, 7, 3, 3, 3, 2, 14, 4,
    28, 16, 24, 21, 28, 16, 16, 13, 6, 6,
    4, 4, 5, 3, 6, 4, 3, 1, 13, 5,
    5, 3, 5, 1, 1, 1, 22
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


def download_book(book_num):
    """Скачивает одну книгу"""
    chapters_count = CHAPTERS_PER_BOOK[book_num - 1]
    chapters = []

    for ch in range(1, chapters_count + 1):
        url = f'https://bolls.life/get-chapter/NRT/{book_num}/{ch}/'
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            verses = [v['text'] for v in data]
            chapters.append(verses)

    return {
        'abbrev': BOOK_ABBREVS[book_num - 1],
        'chapters': chapters
    }


def main():
    bible = load_progress()
    start_book = len(bible) + 1

    if start_book > 66:
        print('✅ Все 66 книг уже скачаны!')
        return

    print(f'Продолжаю с книги {start_book}/66\n')

    for book_num in range(start_book, 67):
        name = BOOK_NAMES[book_num - 1]
        chapters_count = CHAPTERS_PER_BOOK[book_num - 1]

        print(f'[{book_num}/66] {name} ({chapters_count} глав)...', end=' ', flush=True)

        try:
            book = download_book(book_num)
            bible.append(book)
            save_progress(bible)
            print('✓ сохранено')
        except Exception as e:
            print(f'ОШИБКА: {e}')
            print(f'Прогресс сохранён: {len(bible)} книг')
            return

    print(f'\n✅ Готово! Все 66 книг сохранены в {OUTPUT_FILE}')
    file_size = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    print(f'Размер файла: {file_size:.1f} МБ')


if __name__ == '__main__':
    main()

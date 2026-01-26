
// Вставьте сюда ваши данные (не коммитьте реальные токены!)
const TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN';
const CHAT_ID = 'YOUR_CHAT_ID'; // Обычно начинается с минуса, например -100123456789

// URL вашего просмотрщика на GitHub Pages
const VIEWER_URL = 'https://dik-garri.github.io/Bible-in-a-Year/viewer/';

// Список книг для валидации
const BOOK_NAMES = [
  // Ветхий Завет
  'Бытие', 'Исход', 'Левит', 'Числа', 'Второзаконие',
  'Иисус Навин', 'Судьи', 'Руфь', '1 Царств', '2 Царств',
  '3 Царств', '4 Царств', '1 Паралипоменон', '2 Паралипоменон',
  'Ездра', 'Неемия', 'Есфирь', 'Иов', 'Псалтирь', 'Притчи',
  'Екклесиаст', 'Песня Песней', 'Исаия', 'Иеремия', 'Плач Иеремии',
  'Иезекииль', 'Даниил', 'Осия', 'Иоиль', 'Амос', 'Авдий',
  'Иона', 'Михей', 'Наум', 'Аввакум', 'Софония', 'Аггей',
  'Захария', 'Малахия',
  // Новый Завет
  'Матфея', 'Марка', 'Луки', 'Иоанна', 'Деяния', 'Римлянам',
  '1 Коринфянам', '2 Коринфянам', 'Галатам', 'Ефесянам',
  'Филиппийцам', 'Колоссянам', '1 Фессалоникийцам', '2 Фессалоникийцам',
  '1 Тимофею', '2 Тимофею', 'Титу', 'Филимону', 'Евреям',
  'Иакова', '1 Петра', '2 Петра', '1 Иоанна', '2 Иоанна',
  '3 Иоанна', 'Иуды', 'Откровение'
];


/**
 * Парсит строку чтения и извлекает части
 * "Бытие 1-3; Матфея 5:1-26" → [{query: "Бытие 1-3", book: "Бытие"}, ...]
 */
function parseReadingText(text) {
  const parts = text.split(';').map(s => s.trim());
  const readings = [];

  for (const part of parts) {
    // Матч: "Книга ..." - извлекаем название книги и полный запрос
    const match = part.match(/^(.+?)\s+(\d+.*)$/);
    if (match) {
      const bookName = match[1].trim();
      if (BOOK_NAMES.includes(bookName)) {
        readings.push({
          query: part,  // полный запрос: "Бытие 1-3"
          book: bookName
        });
      }
    }
  }

  return readings;
}

/**
 * Генерирует URL для просмотрщика
 * @param {string} query - запрос (Бытие 1-3)
 * @param {string} translation - synod или nrt
 */
function getViewerUrl(query, translation) {
  return VIEWER_URL + '?q=' + encodeURIComponent(query) + '&t=' + translation;
}

/**
 * Создаёт inline keyboard с кнопками для чтения
 * @param {Array} readings - массив из parseReadingText
 */
function buildReadingKeyboard(readings) {
  const keyboard = [];

  for (const reading of readings) {
    const row = [
      {
        text: `${reading.book} (Синод)`,
        url: getViewerUrl(reading.query, 'synod')
      },
      {
        text: `${reading.book} (НРП)`,
        url: getViewerUrl(reading.query, 'nrt')
      }
    ];
    keyboard.push(row);
  }

  return { inline_keyboard: keyboard };
}

function sendReadingFromSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();

  // Убедитесь, что формат даты совпадает с вашей таблицей (dd-MM-yyyy)
  const todayStr = Utilities.formatDate(new Date(), "GMT+6", "dd-MM-yyyy");

  let readingText = "";

  for (let i = 0; i < data.length; i++) {
    let rowDate = data[i][0];
    let rowDateStr = (rowDate instanceof Date)
      ? Utilities.formatDate(rowDate, "GMT+6", "dd-MM-yyyy")
      : rowDate.toString();

    if (rowDateStr === todayStr) {
      readingText = data[i][1];
      break;
    }
  }

  if (readingText) {
    // Разделяем по символу ";" и объединяем через перенос строки
    let formattedReading = readingText.split(';').map(s => s.trim()).join('\n');
    const message = "📖 *Тексты на сегодня:*\n" + formattedReading;

    // Парсим текст и создаём кнопки
    const readings = parseReadingText(readingText);
    const keyboard = buildReadingKeyboard(readings);

    sendToTelegram(message, keyboard);
  } else {
    console.log("Данные на " + todayStr + " не найдены.");
  }
}


function sendToTelegram(text, keyboard) {
  const url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage";
  const payload = {
    "chat_id": CHAT_ID,
    "text": text,
    "parse_mode": "Markdown"
  };

  if (keyboard) {
    payload.reply_markup = keyboard;
  }

  UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  });
}


/**
 * Получает данные "Библия за год" по API ODB.
 *
 * @param {"01-15-2026"} dateString Дата в формате ММ-ДД-ГГГГ.
 * @return Текст чтения библии.
 * @customfunction
 */
function GET_BIBLE_PLAN(dateString) {
  // Базовая ссылка API
  var url = "https://api.experience.odb.org/devotionals/v2?site_id=18&status=publish&country=KG&on=" + dateString;

  try {
    // Делаем запрос
    var response = UrlFetchApp.fetch(url);
    var json = JSON.parse(response.getContentText());

    // Получаем поле с чтением (оно содержит HTML теги)
    // Данные лежат в первом элементе массива [0]
    var rawHtml = json[0].bible_in_a_year;

    // Удаляем HTML теги (<a href...>), чтобы остался чистый текст
    var cleanText = rawHtml.replace(/<[^>]+>/g, '');

    return cleanText;

  } catch (e) {
    return "Ошибка: " + e.message;
  }
}

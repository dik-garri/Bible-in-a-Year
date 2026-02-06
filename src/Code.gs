
// Вставьте сюда ваши данные (не коммитьте реальные токены!)
const TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN';

// ID чатов для отправки (группа и канал)
const CHAT_IDS = [
  'YOUR_GROUP_ID',   // ID группы (например -100123456789)
  'YOUR_CHANNEL_ID'  // ID канала (например -100987654321)
];

// URL вашего просмотрщика на GitHub Pages
const VIEWER_URL = 'https://church.kg/bible/';

// Маппинг русских названий книг на латинские аббревиатуры
const BOOK_ABBREV = {
  'Бытие': 'gn', 'Исход': 'ex', 'Левит': 'lv', 'Числа': 'nm', 'Второзаконие': 'dt',
  'Иисус Навин': 'js', 'Навин': 'js', 'Судьи': 'jud', 'Руфь': 'rt',
  '1 Царств': '1sm', '2 Царств': '2sm', '3 Царств': '1kgs', '4 Царств': '2kgs',
  '1 Паралипоменон': '1ch', '2 Паралипоменон': '2ch',
  'Ездра': 'ezr', 'Неемия': 'ne', 'Есфирь': 'et', 'Иов': 'job',
  'Псалтирь': 'ps', 'Псалом': 'ps', 'Притчи': 'prv',
  'Екклесиаст': 'ec', 'Песня Песней': 'so', 'Песнь Песней': 'so',
  'Исаия': 'is', 'Иеремия': 'jr', 'Плач Иеремии': 'lm',
  'Иезекииль': 'ez', 'Даниил': 'dn',
  'Осия': 'ho', 'Иоиль': 'jl', 'Амос': 'am', 'Авдий': 'ob',
  'Иона': 'jn', 'Михей': 'mi', 'Наум': 'na', 'Аввакум': 'hk',
  'Софония': 'zp', 'Аггей': 'hg', 'Захария': 'zc', 'Малахия': 'ml',
  'Матфея': 'mt', 'От Матфея': 'mt', 'Марка': 'mk', 'От Марка': 'mk',
  'Луки': 'lk', 'От Луки': 'lk', 'Иоанна': 'jo', 'От Иоанна': 'jo',
  'Деяния': 'act', 'Римлянам': 'rm',
  '1 Коринфянам': '1co', '2 Коринфянам': '2co',
  'Галатам': 'gl', 'Ефесянам': 'eph', 'Филиппийцам': 'ph', 'Колоссянам': 'cl',
  '1 Фессалоникийцам': '1ts', '2 Фессалоникийцам': '2ts',
  '1 Тимофею': '1tm', '2 Тимофею': '2tm',
  'Титу': 'tt', 'Филимону': 'phm', 'Евреям': 'hb', 'Иакова': 'jm',
  '1 Петра': '1pe', '2 Петра': '2pe',
  '1 Иоанна': '1jo', '2 Иоанна': '2jo', '3 Иоанна': '3jo',
  'Иуды': 'jd', 'Откровение': 're'
};

/**
 * Конвертирует запрос из русского в латинские аббревиатуры
 * "Бытие 1-3; Матфея 1" → "gn 1-3;mt 1"
 */
function queryToLatin(query) {
  return query.split(';').map(function(part) {
    part = part.trim();
    var match = part.match(/^(.+?)\s+(\d.*)$/);
    if (!match) return part;
    var bookName = match[1];
    var rest = match[2];
    var abbrev = BOOK_ABBREV[bookName];
    if (!abbrev) {
      // Попробовать без учёта регистра
      for (var key in BOOK_ABBREV) {
        if (key.toLowerCase() === bookName.toLowerCase()) {
          abbrev = BOOK_ABBREV[key];
          break;
        }
      }
    }
    return (abbrev || bookName) + ' ' + rest;
  }).join(';');
}

/**
 * Генерирует URL для просмотрщика
 * @param {string} query - запрос (Бытие 1-3)
 * @param {string} translation - synod или nrt
 */
function getViewerUrl(query, translation) {
  return VIEWER_URL + '?q=' + encodeURIComponent(queryToLatin(query)) + '&t=' + translation;
}

/**
 * Создаёт inline keyboard с 2 кнопками для чтения
 * @param {string} readingText - полный текст чтения (Бытие 1-3; Матфея 5)
 */
function buildReadingKeyboard(readingText) {
  return {
    inline_keyboard: [[
      {
        text: 'Синодальный',
        url: getViewerUrl(readingText, 'synod')
      },
      {
        text: 'НРП',
        url: getViewerUrl(readingText, 'nrt')
      }
    ]]
  };
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

    // Создаём 2 кнопки (Синодальный / НРП)
    const keyboard = buildReadingKeyboard(readingText);

    sendToTelegram(message, keyboard);
  } else {
    console.log("Данные на " + todayStr + " не найдены.");
  }
}


function sendToTelegram(text, keyboard) {
  const url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage";

  // Отправляем во все чаты из списка
  CHAT_IDS.forEach(chatId => {
    const payload = {
      "chat_id": chatId,
      "text": text,
      "parse_mode": "Markdown"
    };

    if (keyboard) {
      payload.reply_markup = keyboard;
    }

    try {
      UrlFetchApp.fetch(url, {
        "method": "post",
        "contentType": "application/json",
        "payload": JSON.stringify(payload)
      });
    } catch (e) {
      console.log('Ошибка отправки в ' + chatId + ': ' + e.message);
    }
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

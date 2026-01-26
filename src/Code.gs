
// Вставьте сюда ваши данные (не коммитьте реальные токены!)
const TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN';
const CHAT_ID = 'YOUR_CHAT_ID'; // Обычно начинается с минуса, например -100123456789

// URL вашего просмотрщика на GitHub Pages
const VIEWER_URL = 'https://dik-garri.github.io/Bible-in-a-Year/viewer/';

/**
 * Генерирует URL для просмотрщика
 * @param {string} query - запрос (Бытие 1-3)
 * @param {string} translation - synod или nrt
 */
function getViewerUrl(query, translation) {
  return VIEWER_URL + '?q=' + encodeURIComponent(query) + '&t=' + translation;
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

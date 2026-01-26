# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"Библия за год" (Bible in a Year) — Telegram bot that sends daily Bible reading schedules with inline buttons linking to two translations (Synodal and NRP). Also includes an HTML viewer for browsing Bible texts locally.

## Architecture

```
├── src/
│   └── Code.gs              # Main bot code (Google Apps Script)
├── data/
│   ├── synodal.json         # Synodal translation (66 books, ~6MB)
│   └── nrt.json             # NRP translation (66 books, ~6MB)
├── viewer/
│   └── index.html           # Local HTML viewer for Bible texts
└── scripts/
    └── download_nrt_incremental.py  # Python script to download NRP via bolls.life API
```

## Bot (src/Code.gs)

**Platform:** Google Apps Script
**Trigger:** Daily time-based trigger on `sendReadingFromSheet()`

**Key functions:**
- `sendReadingFromSheet()` — Finds today's reading, sends message with inline keyboard
- `parseReadingText(text)` — Parses "Бытие 1-3; Матфея 5:1-26" into structured data
- `buildReadingKeyboard(readings)` — Creates inline URL buttons for only.bible
- `GET_BIBLE_PLAN(dateString)` — Custom spreadsheet function fetching from ODB API

**Inline buttons link to:** `https://only.bible/bible/{translation}/{book}-{chapter}/`
- Synodal: `rst78`
- NRP: `nrt`

**Book mapping:** `BOOK_CODES` object maps Russian names → only.bible codes (e.g., "Бытие" → "gen")

## HTML Viewer (viewer/index.html)

Local viewer using JSON data files. Requires local server due to CORS:
```bash
python3 -m http.server 8000
# Open: http://localhost:8000/viewer/
```

**URL parameters:**
- `q` — query to load (e.g., `?q=Бытие 1-3`)
- `t` — translation (`synod` or `nrt`, e.g., `?t=nrt`)

**Book picker UI:**
- Testament selection (Ветхий Завет / Новый Завет)
- Books grid (39 OT + 27 NT books)
- Chapters grid for selected book
- Breadcrumb navigation with back buttons

**Manual query formats:**
- `Бытие 1` — chapter, all verses
- `Бытие 1-3` — chapters 1-3, all verses
- `Бытие 1:5` — chapter 1, verse 5
- `Бытие 1:5-10` — chapter 1, verses 5-10
- `Бытие 1:28-2:3` — cross-chapter: ch.1 v.28 → ch.2 v.3
- `Бытие 1-2:3` — from ch.1 v.1 → ch.2 v.3
- `Бытие 1; Матфея 1` — multiple books (semicolon-separated)

## Bible Data (data/)

**Full files** (for bulk operations):
- `synodal.json`, `nrt.json` — all 66 books (~6MB each)
- Format: `[{"abbrev": "gn", "chapters": [["verse1", ...], ...]}, ...]`

**Per-book files** (for viewer, optimized loading):
- `synodal/{abbrev}.json`, `nrt/{abbrev}.json` — individual books (50-300KB each)
- Format: `[["verse1", "verse2", ...], ...]` (just chapters array)

**Book abbreviations:** gn, ex, lv, nm, dt, js, jud, rt, 1sm, 2sm, 1kgs, 2kgs, 1ch, 2ch, ezr, ne, et, job, ps, prv, ec, so, is, jr, lm, ez, dn, ho, jl, am, ob, jn, mi, na, hk, zp, hg, zc, ml, mt, mk, lk, jo, act, rm, 1co, 2co, gl, eph, ph, cl, 1ts, 2ts, 1tm, 2tm, tt, phm, hb, jm, 1pe, 2pe, 1jo, 2jo, 3jo, jd, re

## Deployment (GAS)

1. Copy `src/Code.gs` to Apps Script editor
2. Set `TELEGRAM_TOKEN` and `CHAT_ID`
3. Save (Ctrl+S)
4. Create daily trigger for `sendReadingFromSheet`

No web deployment needed — runs via time trigger only.

## External APIs

- **bolls.life:** `GET https://bolls.life/get-chapter/{SYNOD|NRT}/{book}/{chapter}/` — Free Bible API
- **only.bible:** URL buttons link here for reading
- **ODB API:** Used by `GET_BIBLE_PLAN` spreadsheet function

## Configuration

In `Code.gs`:
- `TELEGRAM_TOKEN` — Bot token from @BotFather
- `CHAT_ID` — Target chat/channel ID (negative for groups/channels)
- Timezone hardcoded: `GMT+6`

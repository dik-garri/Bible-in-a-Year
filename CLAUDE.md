# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"Библия за год" (Bible in a Year) — Telegram bot that sends daily Bible reading schedules with inline buttons linking to two translations (Synodal and NRP). Also includes an HTML viewer for browsing Bible texts locally.

## Architecture

```
├── src/
│   └── Code.gs              # Main bot code (Google Apps Script)
├── viewer/
│   ├── index.html           # HTML viewer for Bible texts (GitHub Pages)
│   └── data/
│       ├── synodal.json     # Synodal translation — full (66 books, ~6MB, for search)
│       ├── nrt.json         # NRP translation — full (66 books, ~6MB, for search)
│       ├── synodal/         # Synodal per-book files (for chapter display)
│       └── nrt/             # NRP per-book files (for chapter display)
├── data/                    # Source data & additional translations (not used by viewer)
│   ├── RST+.SQLite3         # Synodal — SQLite source (with Strong's numbers)
│   ├── NRT.SQLite3          # NRP — SQLite source
│   ├── JBL.SQLite3          # Jubilee edition — SQLite source
│   ├── KYB.SQLite3          # Kyrgyz Bible — SQLite source
│   ├── jbl.json + jbl/      # Jubilee edition — JSON (full + per-book)
│   ├── kyb.json + kyb/      # Kyrgyz Bible — JSON (full + per-book)
│   └── verse_count_diff.csv # Verse count differences across translations
└── scripts/
    ├── download_nrt_incremental.py  # Download NRP via bolls.life API
    ├── download_jbl.py              # Download Jubilee edition from bible.by
    └── fix_formatting.py            # Fix typography issues (legacy, data now from SQLite)
```

## Bot (src/Code.gs)

**Platform:** Google Apps Script
**Trigger:** Daily time-based trigger on `sendReadingFromSheet()`

**Key functions:**
- `sendReadingFromSheet()` — Finds today's reading, sends message with 2 buttons
- `buildReadingKeyboard(readingText)` — Creates 2 inline URL buttons (Синодальный / НРП)
- `getViewerUrl(query, translation)` — Generates GitHub Pages viewer URL with Latin abbreviations
- `queryToLatin(query)` — Converts Cyrillic book names to Latin abbreviations for URLs
- `GET_BIBLE_PLAN(dateString)` — Custom spreadsheet function fetching from ODB API

**Inline buttons link to:** `https://dik-garri.github.io/Bible-in-a-Year/viewer/?q={query}&t={translation}`
- Synodal: `t=synod`
- NRP: `t=nrt`

## HTML Viewer (viewer/index.html)

**GitHub Pages:** https://dik-garri.github.io/Bible-in-a-Year/viewer/

Local development (requires server due to CORS):
```bash
python3 -m http.server 8000
# Open: http://localhost:8000/viewer/
```

**URL parameters:**
- `q` — query using Latin abbreviations (e.g., `?q=gn 1-3;mt 1`) or Cyrillic names (`?q=Бытие 1-3`). Both formats supported, Latin preferred for shorter URLs. Viewer converts to Cyrillic for display.
- `t` — translation (`synod` or `nrt`, e.g., `?t=nrt`)

**Single-panel UI:**
- Testament selection (Ветхий Завет / Новый Завет)
- Books grid (39 OT + 27 NT books), chapters grid, breadcrumb navigation
- Manual query input with "?" help button (popup with format examples), "Показать тексты" button
- Auto-loads on input (debounced 400ms) and on translation change

**Settings gear (⚙️) in top-right corner:**
- Translation: Синодальный / НРП
- Font size (A−/A+, range 12–28px, localStorage key `bible-font-size`)
- Font family: serif/sans-serif/mono (localStorage key `bible-font-family`)
- Dark/light theme (localStorage key `bible-dark-theme`)

**Reader features:**
- Sticky chapter header with short book names: "Быт. 1:14" on scroll, full name "Бытие — Глава 1" when static (BOOK_SHORT map)
- Chapter progress bar (thin blue line under sticky header)
- Dynamic page title (shows current query, e.g., "Бытие 1 — Библия")
- Verse selection & copy: click verses to select, floating bar with "Копировать" button
  - Smart references: `5:1-3` (range), `5:1,4` (non-consecutive), `Бытие 1:5; Матфея 1:17` (cross-book)
  - Copy includes translation name, e.g., `Бытие 1:2 (Синодальный)`
- Verse comparison: clicking a verse shows the same verse from the other translation inline below it
- Full Bible search (🔍 button or Ctrl+F): loads full translation file (~6MB, cached), inline translation switcher (СИН/НРП), 3 tiers: exact phrase → all words → partial; click result to open chapter with auto-scroll to verse
- Chapter navigation: prev/next buttons with short names at bottom (works across books), keyboard ←/→, swipe on mobile
- Last reading memory: auto-loads last query+translation on empty open (localStorage keys `bible-last-query`, `bible-last-translation`)

**Manual query formats:**
- `Бытие 1` — chapter, all verses
- `Бытие 1-3` — chapters 1-3, all verses
- `Бытие 1:5` — chapter 1, verse 5
- `Бытие 1:5-10` — chapter 1, verses 5-10
- `Бытие 1:28-2:3` — cross-chapter: ch.1 v.28 → ch.2 v.3
- `Бытие 1-2:3` — from ch.1 v.1 → ch.2 v.3
- `Бытие 1; Матфея 1` — multiple books (semicolon-separated)

## Bible Data

**Data source:** SQLite databases in `data/` (RST+, NRT, JBL, KYB). JSON files are generated from SQLite using a conversion script that strips markup (Strong's numbers `<S>`, footnotes `<f>`, paragraph breaks `<pb/>`, emphasis `<i>/<e>/<J>` tags).

**Viewer data (viewer/data/):**
- `synodal.json`, `nrt.json` — full translations for search (~6MB each)
- `synodal/`, `nrt/` — per-book files for chapter display (50-300KB each)
- Format: `[{"abbrev": "gn", "chapters": [["verse1", ...], ...]}, ...]`
- Per-book format: `[["verse1", "verse2", ...], ...]` (just chapters array)

**Additional translations (data/):**
- `jbl.json` + `jbl/` — Jubilee edition (Юбилейное издание, Свет на Востоке, 2008)
- `kyb.json` + `kyb/` — Kyrgyz Bible (Кыргыз тилиндеги Библия, 2004)

**All translations:** 66 books, 1189 chapters, ~31162 verses each.

**SQLite schema:** `books` (book_number, short_name, long_name), `verses` (book_number, chapter, verse, text). Book numbers are multiples of 10 (10=Gen, 20=Exo, ..., 730=Rev).

**Book abbreviations:** gn, ex, lv, nm, dt, js, jud, rt, 1sm, 2sm, 1kgs, 2kgs, 1ch, 2ch, ezr, ne, et, job, ps, prv, ec, so, is, jr, lm, ez, dn, ho, jl, am, ob, jn, mi, na, hk, zp, hg, zc, ml, mt, mk, lk, jo, act, rm, 1co, 2co, gl, eph, ph, cl, 1ts, 2ts, 1tm, 2tm, tt, phm, hb, jm, 1pe, 2pe, 1jo, 2jo, 3jo, jd, re

## Data Quality

Current data is sourced from SQLite databases (verified against print editions). Previous bolls.life data had 5229 text issues (3171 missing spaces, 1659 punctuation errors) — all resolved by switching to SQLite source.

Legacy script `fix_formatting.py` is kept for reference but no longer needed.

## Deployment (GAS)

1. Copy `src/Code.gs` to Apps Script editor
2. Set `TELEGRAM_TOKEN` and `CHAT_ID`
3. Save (Ctrl+S)
4. Create daily trigger for `sendReadingFromSheet`

No web deployment needed — runs via time trigger only.

## External APIs

- **bolls.life:** `GET https://bolls.life/get-chapter/{SYNOD|NRT}/{book}/{chapter}/` — Free Bible API (used by download_nrt_incremental.py)
- **bible.by:** `GET https://bible.by/jbl/{book}/{chapter}/` — Jubilee edition HTML (used by download_jbl.py; book numbering differs in NT: general epistles before Pauline)
- **ODB API:** Used by `GET_BIBLE_PLAN` spreadsheet function

## Configuration

In `Code.gs`:
- `TELEGRAM_TOKEN` — Bot token from @BotFather
- `CHAT_ID` — Target chat/channel ID (negative for groups/channels)
- `VIEWER_URL` — GitHub Pages viewer URL
- Timezone hardcoded: `GMT+6`

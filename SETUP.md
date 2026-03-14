# 🚀 SALSHAI Bot2 — Stoch(14,4,13) | רמות 10/90 | 1H · 2H · 4H

## מה הבוט הזה עושה
- עוקב אחרי **50 קריפטו + זהב + כסף + נפט + DAX + ES + NQ**
- על **3 טיימפריימים במקביל**: 1H, 2H, 4H
- מתריע כשהסטוכסטי מגיע ל-**10 (BUY)** או **90 (SELL)**
- רץ אוטומטית **כל שעה** דרך GitHub Actions

---

## התקנה ב-GitHub (5 דקות)

### 1. צור Repository חדש
- github.com → **New** → שם: `salshai-bot2` → **Private** → **Create**

### 2. העלה קבצים
העלה את 3 הקבצים:
- `bot.py`
- `requirements.txt`

### 3. צור את קובץ ה-Workflow
- לחץ **Create new file**
- שם: `.github/workflows/stoch_bot2.yml`
- הדבק את תוכן הקובץ `stoch_bot2.yml`
- לחץ **Commit changes**

### 4. הוסף Secrets
Settings → Secrets and variables → Actions → **New repository secret**

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | `8645590537:AAFPAc8CoUCIYaPAMe4KRydmxiYwTBuAxZg` |
| `TELEGRAM_CHAT_ID` | `5069834520` |

### 5. הרץ לבדיקה
Actions → **Stoch Bot2** → **Run workflow** → חכה ~2 דקות

---

## דוגמה להתראה

```
🟢 Oversold → BUY

💎 נכס: BTCUSDT
💰 מחיר: $67,420.50
📊 אינדיקטור: Stoch(14,4,13)
📏 רמות: 10 / 90
⏱ טיימפריים: 4H
🕐 זמן: 14/03/2026 12:00 UTC
📐 K: 9.45 | D: 11.30

📈 פתח גרף ב-TradingView
```

---

## 50 מטבעות קריפטו

BTC, ETH, BNB, SOL, XRP, ADA, AVAX, DOGE, LINK, DOT,
MATIC, SHIB, LTC, UNI, XLM, ATOM, XMR, ETC, FIL, NEAR,
AAVE, APT, ARB, BCH, CKB, CRV, EOS, FET, FTM, GRT,
ICP, INJ, IOST, IOTA, KAVA, LDO, MKR, OP, PENDLE, QNT,
RENDER, RUNE, SAND, STX, SUI, THETA, TIA, TON, TRX, VET

## נכסים נוספים
זהב · כסף · נפט · DAX · S&P500 Futures · Nasdaq Futures

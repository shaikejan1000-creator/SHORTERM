import requests
import pandas as pd
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

# ── Stochastic params ─────────────────────────────────────────────────────────
K_PERIOD = 14
D_PERIOD = 4
SLOWING  = 13
OB_LEVEL = 90
OS_LEVEL = 10

# ── Timeframes ────────────────────────────────────────────────────────────────
# Binance interval strings
TIMEFRAMES = {
    "1h":  "1H",
    "2h":  "2H",
    "4h":  "4H",
}

# ── Assets ────────────────────────────────────────────────────────────────────
CRYPTO_SYMBOLS = [
    "BTCUSDT",  "ETHUSDT",  "BNBUSDT",  "SOLUSDT",  "XRPUSDT",
    "ADAUSDT",  "AVAXUSDT", "DOGEUSDT", "LINKUSDT", "DOTUSDT",
    "MATICUSDT","SHIBUSDT", "LTCUSDT",  "UNIUSDT",  "XLMUSDT",
    "ATOMUSDT", "XMRUSDT",  "ETCUSDT",  "FILUSDT",  "NEARUSDT",
    "AAVEUSDT", "APTUSDT",  "ARBUSDT",  "BCHUSDT",  "CKBUSDT",
    "CRVUSDT",  "EOSUSDT",  "FETUSDT",  "FTMUSDT",  "GRTUSDT",
    "ICPUSDT",  "INJUSDT",  "IOSTUSDT", "IOTAUSDT", "KAVAUSDT",
    "LDOUSDT",  "MKRUSDT",  "OPUSDT",   "PENDLEUSDT","QNTUSDT",
    "RENDERUSDT","RUNEUSDT","SANDUSDT", "STXUSDT",  "SUIUSDT",
    "THETAUSDT","TIAUSDT",  "TONUSDT",  "TRXUSDT",  "VETUSDT",
]

OTHER_SYMBOLS = {
    "XAUUSD": ("GC=F",   "זהב (Gold)"),
    "XAGUSD": ("SI=F",   "כסף (Silver)"),
    "OIL":    ("CL=F",   "נפט (Oil)"),
    "DAX":    ("^GDAXI", "DAX"),
    "ES":     ("ES=F",   "S&P 500 Futures"),
    "NQ":     ("NQ=F",   "Nasdaq Futures"),
}

# ── Stochastic ────────────────────────────────────────────────────────────────
def stochastic(high, low, close):
    lowest_low   = low.rolling(K_PERIOD).min()
    highest_high = high.rolling(K_PERIOD).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    k = raw_k.rolling(D_PERIOD).mean()
    d = k.rolling(SLOWING).mean()
    return k, d

def check_signals(k, d):
    if len(k) < 2:
        return []
    signals = []
    k_prev, k_curr = k.iloc[-2], k.iloc[-1]
    d_prev, d_curr = d.iloc[-2], d.iloc[-1]

    if k_prev <= OS_LEVEL and k_curr > OS_LEVEL:
        signals.append(("Oversold → BUY", "🟢"))
    if k_prev >= OB_LEVEL and k_curr < OB_LEVEL:
        signals.append(("Overbought → SELL", "🔴"))
    if k_prev <= d_prev and k_curr > d_curr:
        signals.append(("K cross D → Bullish", "📈"))
    if k_prev >= d_prev and k_curr < d_curr:
        signals.append(("K cross D → Bearish", "📉"))
    return signals

# ── Data fetching ─────────────────────────────────────────────────────────────
def fetch_binance(symbol, interval, limit=150):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote_volume","trades","taker_buy_base",
            "taker_buy_quote","ignore"
        ])
        df["high"]  = df["high"].astype(float)
        df["low"]   = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        return df
    except Exception as e:
        print(f"  Binance error {symbol} {interval}: {e}")
        return None

def fetch_yahoo(ticker, limit=150):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"interval": "1h", "range": "30d"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        highs  = result["indicators"]["quote"][0]["high"]
        lows   = result["indicators"]["quote"][0]["low"]
        df = pd.DataFrame({"high": highs, "low": lows, "close": closes}).dropna()
        return df
    except Exception as e:
        print(f"  Yahoo error {ticker}: {e}")
        return None

# ── Telegram ──────────────────────────────────────────────────────────────────
def fmt_price(price):
    try:
        p = float(price)
        if p > 1000:  return f"${p:,.2f}"
        elif p > 1:   return f"${p:,.4f}"
        else:         return f"${p:.6f}"
    except:
        return str(price)

def build_tv_link(symbol, tf):
    tf_map = {"1h": "60", "2h": "120", "4h": "240"}
    interval = tf_map.get(tf, "60")
    sym_map = {
        "XAUUSD": "OANDA:XAUUSD",
        "XAGUSD": "OANDA:XAGUSD",
        "OIL":    "NYMEX:CL1!",
        "DAX":    "TVC:DEU40",
        "ES":     "CME_MINI:ES1!",
        "NQ":     "CME_MINI:NQ1!",
    }
    tv_sym = sym_map.get(symbol, f"BINANCE:{symbol}")
    return f"https://www.tradingview.com/chart/?symbol={tv_sym.replace(':', '%3A')}&interval={interval}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.ok
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def format_alert(symbol, display_name, signal, emoji, price, k_val, d_val, tf_label):
    now = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    tv_link = build_tv_link(symbol, tf_label)
    return (
        f"{emoji} <b>{signal}</b>\n"
        f"\n"
        f"💎 <b>נכס:</b> <code>{display_name}</code>\n"
        f"💰 <b>מחיר:</b> <code>{fmt_price(price)}</code>\n"
        f"📊 <b>אינדיקטור:</b> <code>Stoch({K_PERIOD},{D_PERIOD},{SLOWING})</code>\n"
        f"📏 <b>רמות:</b> <code>{OS_LEVEL} / {OB_LEVEL}</code>\n"
        f"⏱ <b>טיימפריים:</b> <code>{tf_label.upper()}</code>\n"
        f"🕐 <b>זמן:</b> <code>{now}</code>\n"
        f"📐 <b>K:</b> <code>{k_val:.2f}</code> | <b>D:</b> <code>{d_val:.2f}</code>\n"
        f"\n"
        f'<a href="{tv_link}">📈 פתח גרף ב-TradingView</a>'
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    alerts_sent = 0
    print(f"🚀 SALSHAI Bot2 — {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}")
    print(f"Checking {len(CRYPTO_SYMBOLS)} crypto + {len(OTHER_SYMBOLS)} other | TFs: 1H, 2H, 4H\n")

    # ── Crypto (Binance) ──
    for symbol in CRYPTO_SYMBOLS:
        for tf, tf_label in TIMEFRAMES.items():
            print(f"  {symbol} [{tf_label}]...")
            df = fetch_binance(symbol, tf)
            if df is None or len(df) < K_PERIOD + D_PERIOD + SLOWING:
                continue
            k, d = stochastic(df["high"], df["low"], df["close"])
            signals = check_signals(k, d)
            price = df["close"].iloc[-1]
            for signal, emoji in signals:
                msg = format_alert(symbol, symbol, signal, emoji, price, k.iloc[-1], d.iloc[-1], tf)
                if send_telegram(msg):
                    print(f"  ✅ {symbol} [{tf_label}] — {signal}")
                    alerts_sent += 1

    # ── Other assets (Yahoo Finance) ──
    for symbol, (ticker, display_name) in OTHER_SYMBOLS.items():
        print(f"  {display_name} [{ticker}]...")
        df = fetch_yahoo(ticker)
        if df is None or len(df) < K_PERIOD + D_PERIOD + SLOWING:
            continue
        # Check all 3 TFs by resampling
        for tf, tf_label in TIMEFRAMES.items():
            resample_map = {"1h": "1h", "2h": "2h", "4h": "4h"}
            try:
                df_tf = df.copy()
                df_tf.index = pd.RangeIndex(len(df_tf))
                # For Yahoo hourly data, resample manually
                if tf == "2h":
                    df_tf = df.groupby(df.index // 2).agg({"high": "max", "low": "min", "close": "last"}).dropna()
                elif tf == "4h":
                    df_tf = df.groupby(df.index // 4).agg({"high": "max", "low": "min", "close": "last"}).dropna()

                if len(df_tf) < K_PERIOD + D_PERIOD + SLOWING:
                    continue
                k, d = stochastic(df_tf["high"], df_tf["low"], df_tf["close"])
                signals = check_signals(k, d)
                price = df_tf["close"].iloc[-1]
                for signal, emoji in signals:
                    msg = format_alert(symbol, display_name, signal, emoji, price, k.iloc[-1], d.iloc[-1], tf)
                    if send_telegram(msg):
                        print(f"  ✅ {display_name} [{tf_label}] — {signal}")
                        alerts_sent += 1
            except Exception as e:
                print(f"  Error {display_name} {tf}: {e}")

    if alerts_sent == 0:
        print("\n✅ No signals this run.")
    else:
        print(f"\n📨 {alerts_sent} alerts sent.")

if __name__ == "__main__":
    run()

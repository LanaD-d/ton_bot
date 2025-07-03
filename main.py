import requests
import pandas as pd
import ta
import time

# === Твої дані ===
BOT_TOKEN = '7748017684:AAGmC11tDSQLyao6cVld_lYGnYWwRvKpAxU'
CHAT_ID = '589929505'
SYMBOL = 'TONUSDT'
INTERVAL = '1h'
LIMIT = 200

# === Надсилання повідомлень у Telegram ===
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        response = requests.post(url, data=payload)
        print("✅ Відповідь Telegram API:", response.status_code, response.text)
    except Exception as e:
        print("❌ Помилка надсилання:", e)

# === Отримання даних з Binance ===
def get_data():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit={LIMIT}"
    response = requests.get(url)
    print("📊 Дані отримані з Binance:", response.status_code)
    df = pd.DataFrame(response.json(), columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# === Аналіз графіку ===
def analyze(df):
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
    df['sma'] = ta.trend.SMAIndicator(close=df['close'], window=14).sma_indicator()
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd_diff()

    last = df.iloc[-1]
    print(f"🔍 RSI={last['rsi']:.2f}, MACD={last['macd']:.4f}, Close={last['close']:.3f}, SMA={last['sma']:.3f}")

    msg = f"{SYMBOL} | Ціна: {last['close']:.3f}\nRSI: {last['rsi']:.2f} | SMA: {last['sma']:.2f} | MACD: {last['macd']:.4f}\n"

    if last['rsi'] < 30 and last['macd'] > 0 and last['close'] > last['sma']:
        msg += "🟢 Сигнал: Купувати"
    elif last['rsi'] > 70 and last['macd'] < 0 and last['close'] < last['sma']:
        msg += "🔴 Сигнал: Продавати"
    else:
        msg += "ℹ️ Сигналу немає"

    send_message(msg)

# === Головний цикл ===
def main():
    while True:
        try:
            print("🔁 Новий цикл аналізу")
            df = get_data()
            analyze(df)
        except Exception as e:
            print(f"⚠️ Помилка: {e}")
            send_message(f"⚠️ Помилка: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

PAIR_FLAG = {
    'GBPUSD': '🇬🇧🇺🇸',
    'GBPJPY': '🇬🇧🇯🇵',
    'USDJPY': '🇺🇸🇯🇵',
}


def send_telegram(text: str) -> None:
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
    }, timeout=10)


@app.route('/webhook', methods=['POST'])
def webhook():
    raw = request.get_data(as_text=True).strip()
    print(f'[webhook] received: {raw}')

    try:
        # Format from Pine Script alert():
        # DIRECTION|PAIR|ENTRY|SL|TP|SESSION|RR
        direction, pair, entry, sl, tp, session, rr = raw.split('|')

        emoji = '🟢' if direction == 'BUY' else '🔴'
        arrow = '📈' if direction == 'BUY' else '📉'
        flag  = PAIR_FLAG.get(pair, '💱')

        msg = (
            f"{emoji} <b>{direction} SIGNAL — {flag} {pair}</b>\n\n"
            f"📍 <b>Entry:</b>       <code>{entry}</code>\n"
            f"🛑 <b>Stop Loss:</b>   <code>{sl}</code>\n"
            f"🎯 <b>Take Profit:</b> <code>{tp}</code>\n"
            f"📊 <b>R:R Ratio:</b>   1:{rr}\n"
            f"⏰ <b>Session:</b>     {session}\n"
            f"{arrow} Volume confirmed + PA setup\n\n"
            f"⚠️ <i>Verify price action before entry. Manage your risk.</i>"
        )

        send_telegram(msg)
        return jsonify({'status': 'ok'}), 200

    except Exception as exc:
        print(f'[webhook] error: {exc}')
        return jsonify({'error': str(exc)}), 400


@app.route('/', methods=['GET'])
def health():
    return 'FxBreezy Bot is live! 🚀', 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

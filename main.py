from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *

import os

app = Flask(__name__)

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']

client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = 'https://fapi.binance.com'

symbol = "SOLUSDT"
leverage = 10
client.futures_change_leverage(symbol=symbol, leverage=leverage)

@app.route("/")
def home():
    return "Bot is online and ready to trade!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received data:", data)

    signal = data.get("signal", "").upper()

    if signal not in ["LONG", "SHORT"]:
        return jsonify({"error": "Invalid signal"}), 400

    quantity = calculate_quantity()
    side = SIDE_BUY if signal == "LONG" else SIDE_SELL

    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            positionSide="BOTH"
        )
        return jsonify({"status": "success", "order": order})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_quantity():
    balance_info = client.futures_account_balance()
    usdt = next(x for x in balance_info if x['asset'] == 'USDT')
    balance = float(usdt['balance'])
    price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    quantity = round((balance * leverage) / price, 2)
    return quantity

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
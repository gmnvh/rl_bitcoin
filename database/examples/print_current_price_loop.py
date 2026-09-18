"""Example: poll and print the current BTC/USD price every 5 minutes."""

import time
from datetime import datetime

import ccxt

POLL_INTERVAL_SECONDS = 5 * 60

exchange = ccxt.kraken()

while True:
    ticker = exchange.fetch_ticker("BTC/USD")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] BTC/USD last price: ${ticker['last']:,.2f}")
    time.sleep(POLL_INTERVAL_SECONDS)

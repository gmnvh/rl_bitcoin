"""Example: fetch yesterday's BTC/USD daily candle with ccxt."""

from datetime import datetime, timezone

import ccxt

exchange = ccxt.kraken()
candles = exchange.fetch_ohlcv("BTC/USD", timeframe="1d", limit=2)
timestamp, open_, high, low, close, volume = candles[0]  # candles[1] is today, still in progress
date = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date()

print(f"BTC/USD close for {date} (UTC): ${close:,.2f}")

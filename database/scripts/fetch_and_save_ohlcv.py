"""Fetch BTC/USD OHLCV history via ccxt and save/update a Parquet file.

Incremental: if the Parquet file already exists, only candles newer than the
last stored timestamp are fetched and appended. The most recent candle is
always dropped if it hasn't closed yet, so it gets re-fetched (complete) next run.

Defaults to Bitstamp because Kraken's public OHLCV endpoint only keeps the
last ~720 daily candles and ignores `since` beyond that, unlike Bitstamp which
supports paginating back to at least 2012.

Usage:
    python3 database/scripts/fetch_and_save_ohlcv.py [--exchange bitstamp] [--symbol BTC/USD]
                                                      [--timeframe 1d] [--since 2012-01-01T00:00:00Z]
"""

import argparse
import time
from pathlib import Path

import ccxt
import pandas as pd

DB_DIR = Path(__file__).resolve().parent.parent / "BTC_USD"
COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
FETCH_LIMIT = 1000


def parquet_path(timeframe: str) -> Path:
    return DB_DIR / f"{timeframe}.parquet"


def load_existing(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame(columns=COLUMNS)


def fetch_new_candles(exchange, symbol: str, timeframe: str, since_ms: int):
    all_candles = []
    now_ms = exchange.milliseconds()
    while since_ms < now_ms:
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=FETCH_LIMIT)
        if not candles:
            break
        all_candles.extend(candles)
        next_since = candles[-1][0] + 1
        if next_since <= since_ms:
            break
        since_ms = next_since
        time.sleep(exchange.rateLimit / 1000)
    return all_candles


def drop_in_progress_candle(candles, exchange, timeframe):
    if not candles:
        return candles
    duration_ms = exchange.parse_timeframe(timeframe) * 1000
    now_ms = exchange.milliseconds()
    if candles[-1][0] + duration_ms > now_ms:
        return candles[:-1]
    return candles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exchange", default="bitstamp")
    parser.add_argument("--symbol", default="BTC/USD")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--since", default="2012-01-01T00:00:00Z",
                         help="Start date, used only when no existing Parquet file is found")
    args = parser.parse_args()

    DB_DIR.mkdir(parents=True, exist_ok=True)
    path = parquet_path(args.timeframe)
    existing = load_existing(path)

    exchange = getattr(ccxt, args.exchange)()
    since_ms = int(existing["timestamp"].max()) + 1 if not existing.empty else exchange.parse8601(args.since)

    candles = fetch_new_candles(exchange, args.symbol, args.timeframe, since_ms)
    candles = drop_in_progress_candle(candles, exchange, args.timeframe)

    if not candles:
        print(f"No new {args.timeframe} candles to add for {args.symbol}.")
        return

    new_df = pd.DataFrame(candles, columns=COLUMNS)
    combined = (
        pd.concat([existing, new_df], ignore_index=True)
        .drop_duplicates(subset="timestamp", keep="last")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    combined.to_parquet(path, index=False)

    print(f"Added {len(new_df)} new {args.timeframe} candles for {args.symbol}. "
          f"Total rows: {len(combined)}. Saved to {path}")


if __name__ == "__main__":
    main()

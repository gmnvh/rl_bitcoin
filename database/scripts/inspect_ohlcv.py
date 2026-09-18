"""Inspect a Parquet OHLCV file: size, date range, and any missing candles.

Usage:
    python3 database/scripts/inspect_ohlcv.py [--timeframe 1d] [--symbol BTC_USD]
"""

import argparse
from pathlib import Path

import pandas as pd

DB_DIR = Path(__file__).resolve().parent.parent

TIMEFRAME_FREQ = {"1h": "1h", "1d": "1D"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="BTC_USD")
    parser.add_argument("--timeframe", default="1d")
    args = parser.parse_args()

    path = DB_DIR / args.symbol / f"{args.timeframe}.parquet"
    if not path.exists():
        print(f"No such file: {path}")
        return

    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    size_kb = path.stat().st_size / 1024
    start, end = df["date"].min(), df["date"].max()

    print(f"File: {path}")
    print(f"Size: {size_kb:,.1f} KB")
    print(f"Rows: {len(df)}")
    print(f"Start: {start}")
    print(f"End: {end}")

    freq = TIMEFRAME_FREQ.get(args.timeframe)
    if freq is None:
        print(f"Don't know how to check gaps for timeframe '{args.timeframe}'.")
        return

    expected = pd.date_range(start=start, end=end, freq=freq)
    missing = expected.difference(df["date"])

    if missing.empty:
        print("No missing candles.")
    else:
        print(f"Missing {len(missing)} candle(s):")
        for ts in missing:
            print(f"  {ts}")


if __name__ == "__main__":
    main()

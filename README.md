# rl_bitcoin

# Bitcoin Data History Access

## Examples

Example scripts live in [database/examples](database/examples):

- `print_yesterday_btc.py` — fetches yesterday's completed BTC/USD daily candle (Kraken via `ccxt`) and prints its UTC close price.
  ```
  python3 database/examples/print_yesterday_btc.py
  ```
- `print_current_price_loop.py` — polls the current BTC/USD ticker price via `ccxt` every 5 minutes and prints a timestamped log line.
  ```
  python3 database/examples/print_current_price_loop.py
  ```

Kraken is used instead of Binance because Binance returns a `451` geo-restriction error in this dev container.

## Historical Data Storage

`database/scripts/fetch_and_save_ohlcv.py` fetches BTC/USD OHLCV history via `ccxt` and persists it as Parquet files under `database/BTC_USD/`, for use in RL training.

```
python3 database/scripts/fetch_and_save_ohlcv.py [--exchange bitstamp] [--symbol BTC/USD] [--timeframe 1d] [--since 2012-01-01T00:00:00Z]
```

1. Fetches OHLCV candles in paginated batches (`fetch_ohlcv` with `since`/`limit`), going back as far as the exchange allows. Defaults to **Bitstamp**, not Kraken — Kraken's public OHLCV endpoint only keeps the last ~720 daily candles and ignores `since` beyond that, while Bitstamp supports full history back to 2012.
2. Data is partitioned by timeframe, e.g. `database/BTC_USD/1d.parquet`, `database/BTC_USD/1h.parquet` (`1d`/`1h` are the `ccxt` timeframe codes for daily/hourly candles — one row per day and one row per hour, respectively). One file per `(symbol, timeframe)`, not one file per day, since the data is small enough to load in full.
3. Incremental: on each run, only candles newer than the last stored timestamp are fetched and merged in, deduplicating by `timestamp`. The most recent (still in-progress) candle is always dropped so it gets re-fetched complete next run. Re-running the script when already up to date fetches 0 new candles.
4. Load the Parquet files with `pandas.read_parquet` when preparing training data for the RL environment.

**Columns**: `timestamp` (candle open time, ms since epoch UTC — used as the dedup key), `open`, `high`, `low`, `close`, `volume`.

`database/scripts/inspect_ohlcv.py` prints a Parquet file's size, row count, start/end date range, and any missing candles (gaps).

```
python3 database/scripts/inspect_ohlcv.py [--symbol BTC_USD] [--timeframe 1d]
```
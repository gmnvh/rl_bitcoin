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
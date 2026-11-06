"""Market data in: raw trades -> closed 1-minute OHLCV bars, aggregated inside QuestDB."""
import pandas as pd

from qdb import sql

from .config import BAR, EXCHANGE, MARKET, SYMBOL

BARS_SQL = f"""
SELECT timestamp,
       first(price) AS open, max(price) AS high, min(price) AS low, last(price) AS close,
       sum(qty) AS volume, count() AS trades
FROM crypto_trades
WHERE symbol = '{SYMBOL}' AND exchange = '{EXCHANGE}' AND market = '{MARKET}'
  AND timestamp IN today()                      -- today only (UTC)
  AND timestamp < timestamp_floor('m', now())   -- closed bars only
SAMPLE BY {BAR}
"""
# Older QuestDB without today(): use  AND timestamp >= timestamp_floor('d', now())


def load_bars():
    bars = sql(BARS_SQL)
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    return bars.sort_values("timestamp").reset_index(drop=True)

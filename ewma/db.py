"""Everything that touches the signals table. Connection itself lives in qdb.py."""
import pandas as pd

from qdb import sql, write

from .config import EXCHANGE, STRATEGY, SYMBOL

SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
  timestamp TIMESTAMP,   -- when the signal appeared (close of the 1m bar)
  strategy  SYMBOL,      -- e.g. ewma_9_21
  exchange  SYMBOL,
  symbol    SYMBOL,
  side      SYMBOL,      -- BUY / SELL
  price     DOUBLE,      -- close of the bar that made the signal
  ema_fast  DOUBLE,
  ema_slow  DOUBLE
) TIMESTAMP(timestamp) PARTITION BY YEAR WAL
  DEDUP UPSERT KEYS(timestamp, strategy, symbol);
"""
COLS = ["timestamp", "strategy", "exchange", "symbol", "side", "price", "ema_fast", "ema_slow"]


def create_table():
    sql(SCHEMA)


def save_signals(signals):
    """Append signals; DEDUP makes re-sending the same signal harmless."""
    if signals.empty:
        return
    out = signals.assign(strategy=STRATEGY, exchange=EXCHANGE, symbol=SYMBOL)[COLS]
    for c in ("strategy", "exchange", "symbol", "side"):
        out[c] = out[c].astype("category")  # -> SYMBOL
    write("signals", out, at="timestamp")


def load_signals():
    """Today's signals of this strategy, oldest first."""
    df = sql(f"""
        SELECT * FROM signals
        WHERE strategy = '{STRATEGY}' AND symbol = '{SYMBOL}' AND timestamp IN today()
        ORDER BY timestamp
    """)
    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df

"""Pure strategy: bars in, signals out. No database, no clock, so it is easy to test and swap."""
import pandas as pd

from .config import FAST, SLOW

SIGNAL_COLS = ["timestamp", "side", "price", "ema_fast", "ema_slow"]


def ewma_strategy(bars, fast=FAST, slow=SLOW):
    """Long only EMA cross.

    EMA_t = a*P_t + (1-a)*EMA_{t-1},  a = 2/(N+1)   (pandas: ewm(span=N, adjust=False))
    BUY when flat and EMA fast crosses above slow; SELL when long and it crosses below.
    Returns (df with EMAs, signals). A signal is stamped at bar close (bar start + 1 bar).
    """
    df = bars[["timestamp", "close"]].copy()
    df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
    df["above"] = df["ema_fast"] > df["ema_slow"]
    df["cross"] = df["above"].astype(int).diff().fillna(0)  # +1 up, -1 down
    df.loc[df.index < slow, "cross"] = 0                     # EMA warm-up

    step = df["timestamp"].diff().median() if len(df) > 1 else pd.Timedelta(minutes=1)
    rows, holding = [], False
    for r in df.itertuples():
        if r.cross == 1 and not holding:
            side, holding = "BUY", True
        elif r.cross == -1 and holding:
            side, holding = "SELL", False
        else:
            continue
        rows.append((r.timestamp + step, side, r.close, r.ema_fast, r.ema_slow))
    signals = pd.DataFrame(rows, columns=SIGNAL_COLS)
    signals["timestamp"] = pd.to_datetime(signals["timestamp"], utc=True)  # keep dtype when empty
    return df, signals


def position(signals):
    return "LONG" if len(signals) and signals["side"].iloc[-1] == "BUY" else "FLAT"

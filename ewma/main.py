"""Wire the modules together: data -> strategy -> db, once per closed minute."""
import argparse
import time

import pandas as pd

from . import db
from .config import DELAY, FAST, SLOW, STRATEGY, SYMBOL, TZ
from .data import load_bars
from .strategy import ewma_strategy, position


def log(*a):
    print(pd.Timestamp.now(tz=TZ).strftime("%H:%M:%S"), *a, flush=True)


def wait_next_minute():
    time.sleep(60 - time.time() % 60 + DELAY)


def step(seen, plot_path=None):
    """One pass: query bars, run the strategy, save signals not seen before."""
    bars = load_bars()
    if len(bars) <= SLOW:
        log(f"{len(bars)} bars today, need more than {SLOW} for EMA {SLOW}")
        return
    df, signals = ewma_strategy(bars)
    new = signals[~signals["timestamp"].isin(seen)]
    db.save_signals(new)
    seen.update(new["timestamp"])

    last = df.iloc[-1]
    line = (f"close {last.close:,.2f} | EMA{FAST} {last.ema_fast:,.2f} | EMA{SLOW} {last.ema_slow:,.2f} | "
            f"EMA{FAST} {'>' if last.above else '<'} EMA{SLOW} | vị thế {position(signals)}")
    if len(new) > 3:  # first run of the day: summarise the backlog
        line += f"  >>> {len(new)} signals saved, last {new['side'].iloc[-1]} @ {new['price'].iloc[-1]:,.2f}"
    elif len(new):
        line += "  >>> " + ", ".join(f"{r.side} @ {r.price:,.2f}" for r in new.itertuples())
    log(line)
    if plot_path:
        from .plot import plot  # matplotlib only when asked
        plot(df, signals, plot_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--once", action="store_true", help="one pass over today's bars, then exit")
    ap.add_argument("--plot", metavar="PNG", help="save a chart after every pass")
    args = ap.parse_args()

    db.create_table()
    seen = set(db.load_signals().get("timestamp", []))  # resume: don't re-announce today's signals
    log(f"{STRATEGY} on {SYMBOL}, {len(seen)} signals already saved today")
    try:
        step(seen, args.plot)
        while not args.once:
            wait_next_minute()
            try:
                step(seen, args.plot)
            except Exception as e:  # a failed query must not kill the loop
                log(f"!! {e!r}")
    except KeyboardInterrupt:
        log("stopped")


if __name__ == "__main__":
    main()

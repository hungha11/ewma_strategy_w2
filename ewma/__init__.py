"""EMA 9/21 signal module: crypto_trades -> 1m bars -> EMA cross -> signals table.

    python -m ewma.main                  # realtime: one pass per closed minute, until Ctrl+C
    python -m ewma.main --once           # one pass over today's bars, then exit
    python -m ewma.main --plot today.png # also save a chart after every pass
"""

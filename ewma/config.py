"""All settings in one place. Change the strategy here, not in the code."""
SYMBOL, EXCHANGE, MARKET = "BTCUSDT", "binance", "spot"
FAST, SLOW = 9, 21                 # EMA spans, in 1-minute bars
STRATEGY = f"ewma_{FAST}_{SLOW}"   # name stored with every signal
BAR = "1m"                         # bar size for SAMPLE BY
DELAY = 5                          # seconds after the minute closes before querying (let the recorder flush)
TZ = "Asia/Ho_Chi_Minh"            # display only; the database stores UTC

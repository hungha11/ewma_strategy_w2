"""Optional chart: close, both EMAs and the signals, in the deck's colours."""
import matplotlib

matplotlib.use("Agg")  # save to file; no window needed
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from .config import FAST, SLOW, SYMBOL, TZ


def plot(df, signals, path, title_extra=""):
    t = df["timestamp"].dt.tz_convert(TZ)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(t, df["close"], color="#8A8D84", lw=1, label="Giá đóng cửa 1 phút")
    ax.plot(t, df["ema_fast"], color="#B85C38", lw=1.8, label=f"EMA {FAST}")
    ax.plot(t, df["ema_slow"], color="#1F4E5F", lw=1.8, label=f"EMA {SLOW}")
    for side, marker, color in (("BUY", "^", "#4A6B2A"), ("SELL", "v", "#B85C38")):
        s = signals[signals["side"] == side]
        if not s.empty:
            ax.scatter(s["timestamp"].dt.tz_convert(TZ), s["price"], marker=marker, s=110,
                       color=color, edgecolor="white", linewidth=0.8, zorder=3, label=side)
    ax.set_title(f"{SYMBOL} · EMA {FAST}/{SLOW} · long only · {pd.Timestamp.now(tz=TZ):%d/%m/%Y}{title_extra}",
                 loc="left", fontsize=13, color="#3F4B2C", fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=TZ))
    ax.set_xlabel("Giờ Việt Nam (UTC+7)")
    ax.set_ylabel("USDT")
    ax.grid(alpha=0.25)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False, ncol=5)
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)

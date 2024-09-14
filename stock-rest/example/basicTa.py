from pandas_ta.overlap import ema
from pandas_ta.utils import get_offset, verify_series, signals


def macdScx(close, fast=None, slow=None, signal=None, talib=None, offset=None, **kwargs):
    """Indicator: Moving Average, Convergence/Divergence (MACD)"""
    # Validate arguments
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    signal = int(signal) if signal and signal > 0 else 9
    if slow < fast:
        fast, slow = slow, fast
    close = verify_series(close, max(fast, slow, signal))
    if close is None: return
    fastma = ema(close, length=fast)
    slowma = ema(close, length=slow)

    macd = fastma - slowma
    return fastma,slowma,macd
from datetime import datetime

def unix_to_datetime(unix_time: float, is_milliseconds=False):
    """Convert Unix timestamp to formatted datetime string with milliseconds."""
    if is_milliseconds:
        unix_time = unix_time / 1000
    dt = datetime.fromtimestamp(unix_time)
    return dt.strftime('%b %d, %Y at %I:%M:%S.') + f'{dt.microsecond // 1000:03d}'

def pair_ticker(base_ticker: str, quote_ticker: str):
    if base_ticker == quote_ticker:
        return None
    return base_ticker + quote_ticker

def extract_base_ticker(pair: str, quote_ticker: str):
    return pair[:-len(quote_ticker)]

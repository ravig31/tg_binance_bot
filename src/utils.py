from datetime import datetime

def unix_to_datetime(unix_time, is_milliseconds=False):
    """Convert Unix timestamp to formatted datetime string with milliseconds."""
    if is_milliseconds:
        unix_time = unix_time / 1000
    dt = datetime.fromtimestamp(unix_time)
    return dt.strftime('%b %d, %Y at %I:%M:%S.')[:-1] + f'{dt.microsecond:03d} %p'
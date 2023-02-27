from datetime import datetime

import pytz


def get_date_time_now() -> datetime:
    current_timezone = pytz.timezone("Asia/Novosibirsk")
    current_datetime = datetime.now(current_timezone)
    return current_datetime

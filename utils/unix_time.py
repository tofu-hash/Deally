import datetime
import time
from utils import *

months = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа', 9: 'сентября',
    10: 'октября', 11: 'ноября', 12: 'декабря'
}


def format_hour_to_timestamp(hour: int, timestamp: int = 2):
    __hour = hour + timestamp
    if hour in [22, 23, 24]:
        __hour = (hour - 24) + timestamp
    return __hour


def dates_to_text(__datetime: datetime.datetime) -> str:
    date = '%s %s %s года в ' % (__datetime.day,
                                 months[__datetime.month],
                                 __datetime.year)
    __time = '{:02}:{:02}'.format(format_hour_to_timestamp(__datetime.hour), __datetime.minute)
    __datetime = date + __time
    return __datetime


def now_unix_time():
    return int(time.time())


def get_datetime(unix_time: int, __format: bool = True):
    __datetime = datetime.datetime.fromtimestamp(unix_time)

    if __format:
        return dates_to_text(__datetime)
    return __datetime

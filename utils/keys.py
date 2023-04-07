import random
from string import (ascii_lowercase,
                    ascii_uppercase)


def key(groups_count: int = 5, group_length: int = 5):
    """
        Генерация ключей.
        ::param groups_count: Количество групп в ключе.
    """

    def group_key():
        nums = ''.join(map(str, range(10)))
        __key = ''.join([random.choice(ascii_lowercase + ascii_lowercase + nums)
                         for _ in range(group_length)])
        return __key

    __key = '-'.join([group_key() for _ in range(groups_count)])
    return __key

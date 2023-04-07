from aiogram.dispatcher.filters.state import StatesGroup, State


class MarketStatesGroup(StatesGroup):
    select_tokens_count = State()
    buy = State()

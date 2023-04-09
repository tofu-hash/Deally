from aiogram.dispatcher.filters.state import StatesGroup, State


class MarketStatesGroup(StatesGroup):
    select_tokens_count = State()
    buy = State()


class WalletStatesGroup(StatesGroup):
    select_wallet = State()
    select_tokens_count = State()


class GamesStatesGroup(StatesGroup):
    clicker = State()

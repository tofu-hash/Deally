from handlers.callback_query import *
from handlers.messages import *
from handlers.init import *

dp.register_message_handler(start_cmd_handler, commands=['start'], state='*')
dp.register_message_handler(start_cmd_handler, commands=['wallet'], state='*')
dp.register_message_handler(help_cmd_handler, commands=['help'], state='*')
dp.register_message_handler(top_cmd_handler, commands=['top'], state='*')
dp.register_message_handler(get_sticker_id_handler, content_types=['sticker'], state='*')

# == WALLET ==
dp.register_message_handler(send_tokens_select_wallet_handler, state=WalletStatesGroup.select_wallet)
dp.register_callback_query_handler(send_tokens_select_wallet_cq_handler, state=WalletStatesGroup.select_wallet)

dp.register_callback_query_handler(confirm_send_tokens_handler, lambda msg: msg.data == 'confirm_send',
                                   state=WalletStatesGroup.select_tokens_count)
dp.register_callback_query_handler(wallet_cmd_handler, lambda msg: msg.data == 'wallet', state='*')
dp.register_callback_query_handler(send_tokens_cmd_handler, lambda msg: msg.data == 'send_tokens', state='*')
dp.register_callback_query_handler(send_tokens_select_tokens_count_handler, state=WalletStatesGroup.select_tokens_count)
# == == == ==

# == MARKET ==
dp.register_callback_query_handler(market_cmd_handler, lambda msg: msg.data == 'market', state='*')
dp.register_callback_query_handler(buy_next_cmd_handler, lambda msg: msg.data == 'next', state=MarketStatesGroup.buy)
dp.register_callback_query_handler(buy_previous_cmd_handler, lambda msg: msg.data == 'previous',
                                   state=MarketStatesGroup.buy)
dp.register_callback_query_handler(buy_tokens_handler, lambda msg: msg.data.isdigit(), state=MarketStatesGroup.buy)
dp.register_callback_query_handler(confirm_buy_handler, lambda msg: msg.data == 'confirm_buy',
                                   state=MarketStatesGroup.buy)
dp.register_callback_query_handler(buy_cmd_handler, lambda msg: msg.data == 'buy', state='*')
dp.register_callback_query_handler(sell_cmd_handler, lambda msg: msg.data == 'sell', state='*')
dp.register_callback_query_handler(select_sell_tokens_count_handler, state=MarketStatesGroup.select_tokens_count)
# == == == ==


# == GAMES ==
dp.register_callback_query_handler(clicker_cmd_handler, lambda msg: msg.data == 'clicker', state='*')
dp.register_callback_query_handler(collect_diamonds_cmd_handler, lambda msg: msg.data == 'collect_diamonds',
                                   state=GamesStatesGroup.clicker)
dp.register_callback_query_handler(click_cmd_handler, lambda msg: msg.data == 'click', state=GamesStatesGroup.clicker)
# == == == ==


# == GLOBAL ==
dp.register_callback_query_handler(cancel_handler, lambda msg: msg.data == 'cancel', state='*')
dp.register_callback_query_handler(callback, state='*')


# == == == ==

async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand('wallet', 'Открыть кошелёк'),
            BotCommand('top', 'Топ игроков'),
            BotCommand('start', 'Перезапуск бота'),
        ]
    )


async def start(dispatcher) -> None:
    bot_name = dict(await dispatcher.bot.get_me()).get('username')
    await set_default_commands(dispatcher)
    print(f'#    start on @{bot_name}')


async def end(dispatcher) -> None:
    bot_name = dict(await dispatcher.bot.get_me()).get('username')
    print(f'#    end on @{bot_name}')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           on_startup=start,
                           on_shutdown=end)

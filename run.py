from handlers.callback_query import *
from handlers.messages import *
from handlers.init import *

dp.register_message_handler(start_cmd_handler, commands=['start'], state='*')
dp.register_message_handler(wallet_cmd_msg_handler, commands=['wallet'], state='*')
dp.register_message_handler(help_cmd_handler, commands=['help'], state='*')
dp.register_message_handler(get_sticker_id_handler, content_types=['sticker'], state='*')

dp.register_callback_query_handler(market_cmd_handler, lambda msg: msg.data == 'market', state='*')
dp.register_callback_query_handler(buy_next_cmd_handler, lambda msg: msg.data == 'next', state='*')
dp.register_callback_query_handler(buy_previous_cmd_handler, lambda msg: msg.data == 'previous', state='*')
dp.register_callback_query_handler(buy_cmd_handler, lambda msg: msg.data == 'buy', state='*')
dp.register_callback_query_handler(sell_cmd_handler, lambda msg: msg.data == 'sell', state='*')

dp.register_callback_query_handler(select_sell_tokens_count_handler, state=MarketStatesGroup.select_tokens_count)
dp.register_callback_query_handler(wallet_cmd_handler, lambda msg: msg.data == 'wallet', state='*')
dp.register_callback_query_handler(cancel_handler, lambda msg: msg.data == 'cancel', state='*')

dp.register_callback_query_handler(callback, state='*')

async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand('wallet', 'Открыть кошелёк'),
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

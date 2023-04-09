from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)

wallet_button = InlineKeyboardButton(text='• Открыть кошелёк •',
                                     callback_data='wallet')
market_button = InlineKeyboardButton(text='• Маркет •',
                                     callback_data='market')



cancel_reply_markup = InlineKeyboardMarkup()
cancel_reply_markup.add(InlineKeyboardButton(text='⏪ Отмена',
                                             callback_data='cancel'))



start_menu_reply_markup = InlineKeyboardMarkup()
start_menu_reply_markup.add(wallet_button)
start_menu_reply_markup.add(market_button)
start_menu_reply_markup.add(InlineKeyboardButton(text='• Кликер •',
                                                 callback_data='clicker'))



wallet_reply_markup = InlineKeyboardMarkup()
wallet_reply_markup.add(InlineKeyboardButton(text='• Обновить курс •',
                                             callback_data='wallet'))
wallet_reply_markup.add(InlineKeyboardButton(text='• Отправить •',
                                             callback_data='send_tokens'),
                        InlineKeyboardButton(text='• Запросить •',
                                             callback_data='request_tokens'))
wallet_reply_markup.add(market_button, InlineKeyboardButton(text='• Кликер •',
                                                            callback_data='clicker'))



market_reply_markup = InlineKeyboardMarkup()
market_reply_markup.add(InlineKeyboardButton(text='• Продать •',
                                             callback_data='sell'),
                        InlineKeyboardButton(text='• Купить •',
                                             callback_data='buy')
                        )
market_reply_markup.add(wallet_button)



select_tokens_count_reply_markup = InlineKeyboardMarkup()
select_tokens_count_reply_markup.row(
    InlineKeyboardButton(text='-10',
                         callback_data='-10'),
    InlineKeyboardButton(text='-5',
                         callback_data='-5'),
    InlineKeyboardButton(text='-1',
                         callback_data='-1'),
    InlineKeyboardButton(text='+1',
                         callback_data='+1'),
    InlineKeyboardButton(text='+5',
                         callback_data='+5'),
    InlineKeyboardButton(text='+10',
                         callback_data='+10')
)
select_tokens_count_reply_markup.row(
    InlineKeyboardButton(text='-1000',
                         callback_data='-1000'),
    InlineKeyboardButton(text='-100',
                         callback_data='-100'),
    InlineKeyboardButton(text='+100',
                         callback_data='+100'),
    InlineKeyboardButton(text='+1000',
                         callback_data='+1000')
)
select_tokens_count_reply_markup.add(InlineKeyboardButton(text='• Продать •',
                                                          callback_data='confirm_sell'))
select_tokens_count_reply_markup.add(market_button)



buy_tokens_reply_markup = InlineKeyboardMarkup()
buy_tokens_reply_markup.add(InlineKeyboardButton(text='• Купить •',
                                                 callback_data='confirm_buy'))
buy_tokens_reply_markup.add(market_button)



clicker_reply_markup = InlineKeyboardMarkup()
clicker_reply_markup.add(InlineKeyboardButton(text='• Клик •',
                                              callback_data='click'))
clicker_reply_markup.add(InlineKeyboardButton(text='• Собрать алмазы •',
                                              callback_data='collect_diamonds'))
clicker_reply_markup.add(wallet_button)



send_tokens_select_count_reply_markup = InlineKeyboardMarkup()
send_tokens_select_count_reply_markup.row(
    InlineKeyboardButton(text='-10',
                         callback_data='-10'),
    InlineKeyboardButton(text='-5',
                         callback_data='-5'),
    InlineKeyboardButton(text='-1',
                         callback_data='-1'),
    InlineKeyboardButton(text='+1',
                         callback_data='+1'),
    InlineKeyboardButton(text='+5',
                         callback_data='+5'),
    InlineKeyboardButton(text='+10',
                         callback_data='+10')
)
send_tokens_select_count_reply_markup.row(
    InlineKeyboardButton(text='-1000',
                         callback_data='-1000'),
    InlineKeyboardButton(text='-100',
                         callback_data='-100'),
    InlineKeyboardButton(text='+100',
                         callback_data='+100'),
    InlineKeyboardButton(text='+1000',
                         callback_data='+1000')
)
send_tokens_select_count_reply_markup.add(InlineKeyboardButton(text='• Отправить •',
                                                          callback_data='confirm_send'))
send_tokens_select_count_reply_markup.add(wallet_button)
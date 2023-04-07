from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)

cancel_reply_markup = InlineKeyboardMarkup()
cancel_reply_markup.add(InlineKeyboardButton(text='⏪ Отмена',
                                             callback_data='cancel'))

start_menu_reply_markup = InlineKeyboardMarkup()
start_menu_reply_markup.add(InlineKeyboardButton(text='• Открыть кошелёк •',
                                                 callback_data='wallet'))
start_menu_reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                                 callback_data='market'))

market_reply_markup = InlineKeyboardMarkup()
market_reply_markup.add(InlineKeyboardButton(text='• Продать •',
                                             callback_data='sell'),
                        InlineKeyboardButton(text='• Купить •',
                                             callback_data='buy')
                        )
market_reply_markup.add(InlineKeyboardButton(text='• Открыть кошелёк •',
                                             callback_data='wallet'))

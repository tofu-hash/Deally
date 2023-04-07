from handlers.init import *


async def cancel_handler(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.finish()
    if cq.message.text:
        first_line = cq.message.text.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_text(text=answer)
    else:
        first_line = cq.message.caption.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_caption(caption=answer)


async def wallet_cmd_handler(msg: CallbackQuery):
    await msg.answer()

    wallet_id, tokens, diamonds = execute(
        ('SELECT id, tokens, diamonds '
         'FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )
    diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds).word
    tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens).word

    answer = ('👛 *Ваш кошелёк*\n\n'
              '🌎 Адрес для перевода токенов: \n`%s`\n\n'
              '🔘 *%s* %s\n\n'
              '💠 *%s* %s') % \
             (wallet_id, tokens, tokens_word, diamonds, diamonds_word)
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=start_menu_reply_markup)


async def market_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await state.finish()
    await msg.answer()

    await msg.message.edit_text('🛒 *Маркет*', parse_mode='markdown',
                                reply_markup=market_reply_markup)


async def sell_cmd_handler(msg: CallbackQuery):
    await msg.answer()
    await MarketStatesGroup.select_tokens_count.set()

    wallet_tokens_count = execute(
        ('SELECT tokens FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )[0]
    last_rate = execute(
        ('SELECT now_rate FROM rates '
         'ORDER BY id DESC LIMIT 1;'),
        fetchone=True
    )[0]

    rows = int(wallet_tokens_count / 5)
    reply_markup = InlineKeyboardMarkup()

    if rows > 0:
        sep = 25
        counts = [_ * int(wallet_tokens_count / sep) for _ in range(1, sep + 1)]
        buttons = []
        for _ in counts:
            buttons.append(InlineKeyboardButton(text='%s' % _,
                                                callback_data=str(_)))

        btn_count = 0
        cols = 5
        for _ in range(rows):
            reply_markup.row(*buttons[btn_count:btn_count + cols])
            btn_count += cols

        reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                              callback_data='market'))
        answer = ('🛒 *Продажа токенов*\n\n'
                  '📊 *Курс:*\n'
                  '1 токен = %s алмазов\n\n'
                  '💵 Укажите, какое количество токенов вы хотите продать:') % last_rate
    else:
        answer = '❗ Недостаточно токенов для продажи. Минимальное количество: 4'
        reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                              callback_data='market'))

    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=reply_markup)


async def select_sell_tokens_count_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    await state.finish()

    last_rate = execute(
        ('SELECT now_rate FROM rates '
         'ORDER BY id DESC LIMIT 1;'),
        fetchone=True
    )[0]
    execute(
        ('INSERT INTO sells (user_id, amount, now_rate, created) '
         'VALUES (%s, %s, %s, %s);') %
        (msg.from_user.id, msg.data, last_rate, now_unix_time())
    )
    execute(
        ('UPDATE wallets SET tokens=tokens-%s '
         'WHERE user_id=%s') %
        (msg.data, msg.from_user.id)
    )
    execute(
        ('INSERT INTO rates (user_id, now_rate, created) '
         'VALUES (%s, %s, %s);') % (msg.from_user.id,
                                    last_rate - int(msg.data),
                                    now_unix_time())
    )

    tokens_word = morph.parse('токен')[0].make_agree_with_number(int(msg.data)).word

    answer = ('💵 Ваше обьявление выставлено на '
              'маркет\n\n'
              '🔘 Продажа *%s %s*\n\n'
              '❗ Обьявление нельзя удалить') % \
             (msg.data, tokens_word)

    reply_markup = InlineKeyboardMarkup()

    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))

    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=start_menu_reply_markup)


async def buy_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    await MarketStatesGroup.buy.set()

    wallet_diamonds_count = execute(
        ('SELECT diamonds FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )[0]

    sells = execute(
        ('SELECT * FROM sells '
         'WHERE now_rate<=%s') %
        wallet_diamonds_count,
        fetchall=True
    )
    pages_count = int(len(sells) / 10) + 1

    step = 10
    reply_markup = InlineKeyboardMarkup()
    for _ in sells[:step]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2]),
                                              callback_data=_[0]))
    if len(sells) >= 10:
        reply_markup.add(InlineKeyboardButton(text=' - ',
                                              callback_data='-'),
                         InlineKeyboardButton(text='%s/%s ➡️' % (1, pages_count),
                                              callback_data='next')
                         )
    # ⬅️
    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))

    answer = '🛒 *Покупка токенов*\n\n' \
             '❗ Показываются только те обьявления, ' \
             'курс которых не превышает ваш баланс ' \
             'алмазов.'
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=reply_markup)

    await state.set_state(MarketStatesGroup.buy)
    data = {
        'page': 0,
        'sells': sells,
        'pages_count': pages_count
    }
    await state.update_data(data=data)


async def buy_next_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    sells = state_data.get('sells', [])
    page = state_data.get('page', 0) + 1
    pages_count = state_data.get('pages_count', 1)

    step = page * 10
    reply_markup = InlineKeyboardMarkup()
    for _ in sells[step:step + 10]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2]),
                                              callback_data=_[0]))
    if len(sells[step:step + 10]) < 10:
        reply_markup.add(InlineKeyboardButton(text='⬅️ %s/%s' % (page - 1, pages_count),
                                              callback_data='previous'),
                         InlineKeyboardButton(text=' - ',
                                              callback_data='-')
                         )
    else:
        reply_markup.add(InlineKeyboardButton(text='⬅️ %s/%s' % (page - 1, pages_count),
                                              callback_data='previous'),
                         InlineKeyboardButton(text='%s/%s ➡️' % (page + 1, pages_count),
                                              callback_data='next')
                         )
    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))
    await msg.message.edit_reply_markup(reply_markup=reply_markup)

    data = {
        'sells': sells,
        'page': page
    }
    await state.update_data(data=data)


async def buy_previous_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    sells = state_data.get('sells', [])
    page = abs(state_data.get('page', 0) - 1)
    pages_count = state_data.get('pages_count', 1)

    step = page * 10
    reply_markup = InlineKeyboardMarkup()
    for _ in sells[step:step + 10]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2]),
                                              callback_data=_[0]))

    if page != 0:
        reply_markup.add(InlineKeyboardButton(text='⬅️ %s/%s' % (page - 1, pages_count),
                                              callback_data='previous'),
                         InlineKeyboardButton(text='%s/%s ➡️' % (page + 1, pages_count),
                                              callback_data='next')
                         )
    else:
        reply_markup.add(InlineKeyboardButton(text=' - ',
                                              callback_data='-'),
                         InlineKeyboardButton(text='%s/%s ➡️' % (page + 1, pages_count),
                                              callback_data='next')
                         )

    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))
    await msg.message.edit_reply_markup(reply_markup=reply_markup)

    data = {
        'sells': sells,
        'page': page
    }
    await state.update_data(data=data)


async def callback(msg: CallbackQuery, state: FSMContext):
    print(msg.data)

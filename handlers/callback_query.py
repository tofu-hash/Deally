from handlers.init import *
from config import MARKET_SELLS_STEP


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
    last_rate = execute(
        ('SELECT now_rate FROM rates '
         'ORDER BY id DESC LIMIT 1;'),
        fetchone=True
    )[0]

    last_rate_word = morph.parse('алмаз')[0].make_agree_with_number(last_rate).word
    diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds).word
    tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens).word

    answer = ('👛 *Ваш кошелёк*\n\n'
              '📈 Курс: 1 токен = %s %s\n\n'
              '🌎 Адрес для перевода токенов: \n`%s`\n\n'
              '🔘 *%s* %s\n\n'
              '💠 *%s* %s') % \
             (last_rate, last_rate_word, wallet_id, tokens, tokens_word, diamonds, diamonds_word)
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=wallet_reply_markup)


async def market_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await state.finish()
    await msg.answer()

    await msg.message.edit_text('🛒 *Маркет*', parse_mode='markdown',
                                reply_markup=market_reply_markup)


async def sell_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    await state.set_state(MarketStatesGroup.select_tokens_count)

    tokens, diamonds = execute(
        ('SELECT tokens, diamonds FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )
    last_rate = execute(
        ('SELECT now_rate FROM rates '
         'ORDER BY id DESC LIMIT 1;'),
        fetchone=True
    )[0]

    rate_diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(last_rate).word
    diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds).word
    tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens).word

    answer = ('🛒 *Продажа токенов*\n\n'
              '📊 *Курс:* *1 токен* = *%s %s*\n\n'
              '💵 *Ваш баланс:*\n'
              '🔘 *%s %s*\n'
              '💠 *%s %s*') % \
             (last_rate, rate_diamonds_word, tokens,
              tokens_word, diamonds, diamonds_word)

    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=select_tokens_count_reply_markup)


async def select_sell_tokens_count_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    tokens_count = state_data.get('tokens_count', 0)

    if '+' in msg.data or '-' in msg.data:
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

        if '+' in msg.data:
            num = int(msg.data.split('+')[1])
            tokens_count += num
        elif '-' in msg.data:
            num = int(msg.data.split('-')[1])
            tokens_count -= num

        if tokens_count > wallet_tokens_count:
            tokens_count = wallet_tokens_count
        elif tokens_count <= 1:
            tokens_count = 1

        rate_diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(last_rate).word
        tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens_count).word

        answer = ('🛒 *Продажа токенов*\n\n'
                  '📊 *Курс:* *1 токен* = *%s %s*\n\n'
                  '💵 *Ваш баланс:*\n'
                  '🔘 *%s %s*\n\n'
                  '🔘 %s') % \
                 (last_rate, rate_diamonds_word, wallet_tokens_count,
                  tokens_word, tokens_count)

        await msg.message.edit_text(text=answer, parse_mode='markdown',
                                    reply_markup=select_tokens_count_reply_markup)

        await state.update_data(data={'tokens_count': tokens_count})

    elif msg.data == 'confirm_sell':
        if tokens_count > 0:
            last_rate = execute(
                ('SELECT now_rate FROM rates '
                 'ORDER BY id DESC LIMIT 1;'),
                fetchone=True
            )[0]
            execute(
                ('INSERT INTO sells (user_id, amount, now_rate, created) '
                 'VALUES (%s, %s, %s, %s);') %
                (msg.from_user.id, tokens_count, last_rate, now_unix_time())
            )
            execute(
                ('UPDATE wallets SET tokens=tokens-%s '
                 'WHERE user_id=%s') %
                (tokens_count, msg.from_user.id)
            )
            all_tokens_count = execute(
                'SELECT SUM(tokens) FROM wallets',
                fetchone=True
            )[0]
            all_users_count = execute(
                'SELECT COUNT(*) FROM users',
                fetchone=True
            )[0]
            execute(
                ('INSERT INTO rates (user_id, now_rate, created) '
                 'VALUES (%s, %s, %s);') % (msg.from_user.id,
                                            all_tokens_count / all_users_count,
                                            now_unix_time())
            )

            diamonds_count = tokens_count * last_rate

            tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens_count).word
            diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds_count).word

            answer = ('💵 Ваше обьявление выставлено на '
                      'маркет\n\n'
                      '🔘 Продажа *%s %s*\n'
                      '💠 Цена: *%s %s*\n\n'
                      '❗ Обьявление нельзя удалить\n\n'
                      'ℹ Когда кто-то купит ваше обьявление, '
                      'вам придёт уведомление и алмазы будут '
                      'зачислены.') % \
                     (tokens_count, tokens_word, diamonds_count, diamonds_word)

            reply_markup = InlineKeyboardMarkup()

            reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                                  callback_data='market'))

            await msg.message.edit_text(text=answer, parse_mode='markdown',
                                        reply_markup=start_menu_reply_markup)
            await state.finish()
        else:
            answer = '❗ *Укажите количество токенов для продажи*'
            await msg.message.edit_text(text=answer, parse_mode='markdown',
                                        reply_markup=select_tokens_count_reply_markup)


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
         'WHERE now_rate<=%s AND completed=0 LIMIT %s OFFSET 0') %
        (wallet_diamonds_count, MARKET_SELLS_STEP * 2),
        fetchall=True
    )
    pages_count = int(len(sells) / MARKET_SELLS_STEP) + 1

    step = MARKET_SELLS_STEP
    reply_markup = InlineKeyboardMarkup()
    for _ in sells[:step]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2] * _[1]),
                                              callback_data=_[0]))
    if len(sells) >= MARKET_SELLS_STEP:
        reply_markup.add(InlineKeyboardButton(text='  ',
                                              callback_data='-'),
                         InlineKeyboardButton(text='• %s •' % 0,
                                              callback_data='-'),
                         InlineKeyboardButton(text='➡️',
                                              callback_data='next')
                         )

    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))

    answer = '🛒 *Покупка токенов*\n\n' \
             '❗ Показываются только те обьявления, ' \
             'курс которых не превышает ваш баланс ' \
             'алмазов.\n\n'
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=reply_markup)

    await state.set_state(MarketStatesGroup.buy)
    data = {
        'page': 0,
        'pages_count': pages_count,
        'wallet_diamonds_count': wallet_diamonds_count
    }
    await state.update_data(data=data)


async def buy_next_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    page = state_data.get('page', 0) + 1
    wallet_diamonds_count = state_data.get('wallet_diamonds_count', 0)
    step = page * MARKET_SELLS_STEP

    sells = execute(
        ('SELECT * FROM sells '
         'WHERE now_rate<=%s AND completed=0 LIMIT %s OFFSET %s;') %
        (wallet_diamonds_count, MARKET_SELLS_STEP * 2, step),
        fetchall=True
    )

    reply_markup = InlineKeyboardMarkup()
    for _ in sells[:MARKET_SELLS_STEP]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2] * _[1]),
                                              callback_data=_[0]))
    print(len(sells[:MARKET_SELLS_STEP]))
    if len(sells[:MARKET_SELLS_STEP]) < MARKET_SELLS_STEP:
        for _ in range(MARKET_SELLS_STEP - len(sells[:MARKET_SELLS_STEP])):
            reply_markup.add(InlineKeyboardButton(text='  ',
                                                  callback_data='emptySells'))

        reply_markup.add(InlineKeyboardButton(text='⬅️',
                                              callback_data='previous'),
                         InlineKeyboardButton(text='• %s •' % page,
                                              callback_data='emptyButton'),
                         InlineKeyboardButton(text='  ',
                                              callback_data='emptyButton')
                         )
    else:
        reply_markup.add(InlineKeyboardButton(text='⬅️',
                                              callback_data='previous'),
                         InlineKeyboardButton(text='• %s •' % page,
                                              callback_data='emptyButton'),
                         InlineKeyboardButton(text='➡️',
                                              callback_data='next')
                         )
    reply_markup.add(InlineKeyboardButton(text='• Маркет •',
                                          callback_data='market'))
    await msg.message.edit_reply_markup(reply_markup=reply_markup)

    data = {
        'page': page,
        'wallet_diamonds_count': wallet_diamonds_count
    }
    await state.update_data(data=data)


async def buy_previous_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    wallet_diamonds_count = state_data.get('wallet_diamonds_count', 0)
    page = abs(state_data.get('page', 1) - 1)
    step = page * MARKET_SELLS_STEP

    sells = execute(
        ('SELECT * FROM sells '
         'WHERE now_rate<=%s AND completed=0 LIMIT %s OFFSET %s') %
        (wallet_diamonds_count, MARKET_SELLS_STEP * 2, step),
        fetchall=True
    )

    reply_markup = InlineKeyboardMarkup()
    for _ in sells[:MARKET_SELLS_STEP]:
        reply_markup.add(InlineKeyboardButton(text='%s 🔘 | %s 💠' % (_[1], _[2] * _[1]),
                                              callback_data=_[0]))

    if page != 0:
        reply_markup.add(InlineKeyboardButton(text='⬅️',
                                              callback_data='previous'),
                         InlineKeyboardButton(text='• %s •' % page,
                                              callback_data='emptyButton'),
                         InlineKeyboardButton(text='➡️',
                                              callback_data='next')
                         )
    else:
        reply_markup.add(InlineKeyboardButton(text='  ',
                                              callback_data='emptyButton'),
                         InlineKeyboardButton(text='• %s •' % page,
                                              callback_data='emptyButton'),
                         InlineKeyboardButton(text='➡️',
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


async def buy_tokens_handler(msg: CallbackQuery, state: FSMContext):
    sell = execute(
        ('SELECT * FROM sells '
         'WHERE id=%s') % msg.data,
        fetchone=True
    )
    sell_owner_wallet = execute(
        ('SELECT id FROM wallets '
         'WHERE user_id=%s') % sell[3],
        fetchone=True
    )[0]
    diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(sell[2]).word
    tokens_word = morph.parse('токен')[0].make_agree_with_number(sell[1]).word

    answer = ('🔘 * Покупка токенов*\n\n'
              '🆔 Обьявление #%s\n\n'
              '🔘 Количество: *%s %s*\n'
              '💠 Цена: *%s %s*\n\n'
              '📅 *%s*\n\n'
              '👛 Кошелёк владельца:\n'
              '`%s`') % \
             (sell[0], sell[1], tokens_word,
              sell[2] * sell[1], diamonds_word,
              get_datetime(sell[4]), sell_owner_wallet)
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=buy_tokens_reply_markup)

    await state.update_data(data={'sell_id': sell[0]})


async def confirm_buy_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    state_data = await state.get_data()
    sell_id = state_data.get('sell_id', 0)
    tokens_count, sell_rate, sell_owner_id, created = execute(
        ('SELECT amount, now_rate, user_id, created FROM sells '
         'WHERE id=%s') % sell_id,
        fetchone=True
    )
    sell_owner_wallet = execute(
        ('SELECT id FROM wallets '
         'WHERE user_id=%s') % sell_owner_id,
        fetchone=True
    )[0]
    current_user_wallet, current_user_diamonds_count = execute(
        ('SELECT id, tokens FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )
    if current_user_diamonds_count >= int(tokens_count * sell_rate):
        execute(
            ('UPDATE sells SET completed=1 '
             'WHERE id=%s') % sell_id
        )

        diamonds_count = tokens_count * sell_rate

        diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds_count).word
        tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens_count).word

        execute(
            ('UPDATE wallets SET tokens=tokens+%s, diamonds=diamonds-%s '
             'WHERE user_id=%s') % (tokens_count, diamonds_count, msg.from_user.id)
        )
        execute(
            ('UPDATE wallets SET diamonds=diamonds+%s '
             'WHERE user_id=%s') % (diamonds_count, sell_owner_id)
        )

        current_user_answer = ('✅ *Сделка *#%s* завершена*\n\n'
                               '🔘 *+ %s %s*\n'
                               '💠 *- %s %s*\n\n'
                               '👛 Кошелёк продавца:\n'
                               '`%s`\n\n'
                               '📅 *%s*') % \
                              (sell_id, tokens_count, tokens_word,
                               diamonds_count, diamonds_word,
                               sell_owner_wallet, get_datetime(created))

        sell_owner_answer = ('✅ *Сделка *#%s* завершена*\n\n'
                             '🔘 *- %s %s*\n'
                             '💠 *+ %s %s*\n\n'
                             '👛 Кошелёк покупателя:\n'
                             '`%s`\n\n'
                             '📅 *%s*') % \
                            (sell_id, tokens_count, tokens_word,
                             diamonds_count, diamonds_word,
                             current_user_wallet, get_datetime(created))

        await msg.message.edit_text(text=current_user_answer, parse_mode='markdown',
                                    reply_markup=start_menu_reply_markup)
        await bot.send_message(chat_id=sell_owner_id, text=sell_owner_answer, parse_mode='markdown')

    else:
        await msg.message.edit_text(text='🎯 Недостаточно алмазов',
                                    reply_markup=start_menu_reply_markup)
    await state.finish()


async def clicker_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await state.set_state(GamesStatesGroup.clicker)

    answer = '⛏ *Кликер алмазов*\n\n' \
             '💠 Заработано: *0 алмазов*'
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=clicker_reply_markup)


async def click_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    diamonds_count = state_data.get('diamonds_count', 0)
    diamonds_count += 1

    diamonds_word = morph.parse('алмаз')[0].make_agree_with_number(diamonds_count).word

    answer = ('⛏ *Кликер алмазов*\n\n'
              '💠 Заработано: *%s %s*') % (diamonds_count, diamonds_word)

    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=clicker_reply_markup)

    await state.update_data(data={'diamonds_count': diamonds_count})


async def collect_diamonds_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    diamonds_count = state_data.get('diamonds_count', 0)

    execute(
        ('UPDATE wallets SET diamonds=diamonds+%s '
         'WHERE user_id=%s') % (diamonds_count, msg.from_user.id)
    )

    answer = ('⛏ *Кликер алмазов*\n\n'
              '💠 *Алмазы собраны*')

    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=clicker_reply_markup)

    await state.update_data(data={'diamonds_count': 0})


async def send_tokens_cmd_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    last_recipient_wallets = execute(
        ('SELECT recipient_wallet_id '
         'FROM transactions LIMIT 5'),
        fetchall=True
    )
    reply_markup = InlineKeyboardMarkup()
    for recipient_wallet in last_recipient_wallets:
        reply_markup.add(InlineKeyboardButton(text=recipient_wallet[0],
                                              callback_data=recipient_wallet[0]))
    reply_markup.add(wallet_button)

    answer = ('🔘 *Отправка токенов на другой кошелёк*\n\n'
              '👛 Отправь адрес кошелька, или выбери из списка. (Если есть)\n\n'
              '💠 *Формат адреса кошелька:*\n'
              '`xxxxx-xxxxx-xxxxx-xxxxx`\n\n'
              '❗ Если указать неверный адрес, токены сгорят '
              'без возможности возврата.')
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=reply_markup)
    await WalletStatesGroup.select_wallet.set()


async def send_tokens_select_tokens_count_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

    state_data = await state.get_data()
    tokens_count = state_data.get('tokens_count', 0)

    if '+' in msg.data or '-' in msg.data:
        wallet_tokens_count = execute(
            ('SELECT tokens FROM wallets '
             'WHERE user_id=%s') % msg.from_user.id,
            fetchone=True
        )[0]

        if '+' in msg.data:
            num = int(msg.data.split('+')[1])
            tokens_count += num
        elif '-' in msg.data:
            num = int(msg.data.split('-')[1])
            tokens_count -= num

        if tokens_count > wallet_tokens_count:
            tokens_count = wallet_tokens_count
        elif tokens_count <= 1:
            tokens_count = 1

        tokens_word = morph.parse('токен')[0].make_agree_with_number(wallet_tokens_count).word
        send_tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens_count).word

        answer = ('🔘 *Укажи количество токенов для отправки*\n\n'
                  '💵 *Ваш баланс: %s %s*\n\n'
                  '🔘 %s %s для отправки') % \
                 (wallet_tokens_count,
                  tokens_word, tokens_count, send_tokens_word)

        await msg.message.edit_text(text=answer, parse_mode='markdown',
                                    reply_markup=send_tokens_select_count_reply_markup)

        await state.update_data(data={'tokens_count': tokens_count})


async def confirm_send_tokens_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    state_data = await state.get_data()
    wallet = state_data.get('wallet')
    tokens_count = state_data.get('tokens_count', 0)

    execute(
        ('UPDATE wallets SET tokens=tokens+%s '
         'WHERE id="%s"') % (tokens_count, wallet)
    )
    execute(
        ('UPDATE wallets SET tokens=tokens-%s '
         'WHERE user_id=%s') % (tokens_count, msg.from_user.id)
    )
    last_rate = execute(
        ('SELECT now_rate FROM rates '
         'ORDER BY id DESC LIMIT 1;'),
        fetchone=True
    )[0]
    current_user_wallet = execute(
        ('SELECT id FROM wallets '
         'WHERE user_id=%s') % msg.from_user.id,
        fetchone=True
    )[0]
    wallet_owner_id = execute(
        ('SELECT user_id FROM wallets '
         'WHERE id="%s"') % wallet,
        fetchone=True
    )[0]
    execute(
        ('INSERT INTO transactions (id, amount, now_rate, '
         'sender_wallet_id, recipient_wallet_id, created) '
         'VALUES ("%s", %s, %s, "%s", "%s", %s);') %
        (key(6), tokens_count, last_rate,
         current_user_wallet, wallet, now_unix_time())
    )
    tokens_word = morph.parse('токен')[0].make_agree_with_number(tokens_count).word

    current_user_answer = '✅ *Токены переведены*\n\n' \
                          '🔘 Количество: %s %s\n' \
                          '👛 Кошелёк:\n`%s`\n\n' \
                          '📅 *%s*' % (tokens_count, tokens_word, wallet,
                                      get_datetime(now_unix_time()))
    wallet_owner_answer = '✅ *Получен перевод токенов*\n\n' \
                          '🔘 Количество: %s %s\n' \
                          '👛 Кошелёк:\n`%s`\n\n' \
                          '📅 *%s*' % (tokens_count, tokens_word, current_user_wallet,
                                      get_datetime(now_unix_time()))

    await msg.message.edit_text(text=current_user_answer, parse_mode='markdown',
                                reply_markup=start_menu_reply_markup)
    await bot.send_message(chat_id=wallet_owner_id, text=wallet_owner_answer, parse_mode='markdown')
    await state.finish()


async def send_tokens_select_wallet_cq_handler(msg: CallbackQuery, state: FSMContext):
    await state.update_data(data={'wallet': msg.data})

    answer = '🔘 *Укажи количество токенов для отправки*'
    await msg.message.edit_text(text=answer, parse_mode='markdown',
                                reply_markup=select_tokens_count_reply_markup)
    await WalletStatesGroup.select_tokens_count.set()


async def callback(msg: CallbackQuery, state: FSMContext):
    await msg.answer()

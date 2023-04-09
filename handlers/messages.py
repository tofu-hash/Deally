import aiogram.utils.exceptions
from handlers.init import *


async def start_cmd_handler(msg: Message, state: FSMContext):
    await state.finish()

    # Create user
    execute(
        ('INSERT OR IGNORE INTO users '
         '(user_id, username, created) '
         'VALUES (%s, "%s", %s);') %
        (msg.from_user.id, msg.from_user.username,
         now_unix_time())
    )
    execute(
        ('INSERT OR IGNORE INTO wallets '
         '(id, user_id, created) '
         'VALUES ("%s", %s, %s);') %
        (key(), msg.from_user.id, now_unix_time())
    )

    answer = (
        'Привет, *{}*!👋\n\n'
        'Я - симуляция торговли криптовалютой.\n\n'
        '💵 Моя валюта - *токены* и *алмазы*.\n'
        'Токены выступают в качестве криптовалюты, '
        'а алмазы - в качестве стандартной валюты.\n\n'
        '👥 Обменивай *алмазы *по более выгодному '
        'курсу и зарабатывай *токены*.\n\n'
        '🏆 Пользователи с наибольшим количеством '
        '*токенов* смогу попасть в *топ-10.*\n\n'
    ).format(msg.from_user.first_name)

    if msg.get_args():
        callback_data = msg.get_args().split('callbackData')[1]
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(InlineKeyboardButton(text='• Открыть •',
                                              callback_data=callback_data))
        await msg.answer(text='⛓ *Ссылка на функционал*', parse_mode='markdown',
                         reply_markup=reply_markup)
    else:
        await msg.answer(text=answer, parse_mode='markdown',
                         reply_markup=start_menu_reply_markup)


async def wallet_cmd_msg_handler(msg: Message):
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
    await msg.answer(text=answer, parse_mode='markdown',
                     reply_markup=start_menu_reply_markup)


async def help_cmd_handler(msg: Message, state: FSMContext):
    await state.finish()
    await state.finish()

    answer = ('🚑 Помощь '
              '...')
    await msg.answer(answer, parse_mode='markdown')


async def get_sticker_id_handler(msg: Message):
    await msg.answer_sticker(sticker=msg.sticker.file_id)
    print(msg.sticker.file_id)


async def send_tokens_select_wallet_handler(msg: Message, state: FSMContext):
    await state.update_data(data={'wallet': msg.text})

    answer = '🔘 *Укажи количество токенов для отправки*'
    await msg.answer(text=answer, parse_mode='markdown',
                     reply_markup=select_tokens_count_reply_markup)
    await WalletStatesGroup.select_tokens_count.set()


async def top_cmd_handler(msg: Message):
    top_wallets = execute(
        ('SELECT id, tokens, diamonds '
         'FROM wallets ORDER BY tokens'),
        fetchall=True
    )[::-1]
    answer = '📊 Топ-10 кошельков на сегодня\n\n'

    for num, wallet in enumerate(top_wallets, start=1):
        if num == 1:
            num = '1 🏆'
        answer += '%s. `%s`\n' \
                  '├ 🎯 *%s токенов*\n' \
                  '└ 💠 *%s алмазов*\n\n' % (num, wallet[0], wallet[1], wallet[2])
    await msg.answer(text=answer, parse_mode='markdown')

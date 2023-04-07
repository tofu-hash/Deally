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
    execute(
        ('UPDATE wallets SET tokens=50, diamonds=50 '
         'WHERE user_id=%s') % msg.from_user.id
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
        '📖 *Комиссии и пополнения:*\n'
        '• Каждую неделю тебе даётся 50 токенов\n'
        '• За каждую сделку мы забираем 5% от суммы'
    ).format(msg.from_user.first_name)

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

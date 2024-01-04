import logging
from datetime import datetime, timedelta
from pathlib import Path
import decouple
import telegram
from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ChatJoinRequestHandler, \
    CallbackContext
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler, filters
from translations import translations
from group_message_conv import message_conv_handler

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

GROUP_CHAT_ID = decouple.config('GROUP_CHAT_ID')
BUSINESS_CLUB_TITLE = decouple.config('BUSINESS_CLUB_TITLE')

[QUESTION1, QUESTION2, QUESTION3, ACTION_SUCCESS, CHOOSING_LANGUAGE] = range(5)

greeting = """
Вітаю 👋!\nПеред тим, як ми вишлемо Вам посилання на групу *бізнес клубу Millionario* дайте відповідь\
 на 4 запитання.\nЩоб продовжити, оберіть мову спілкування.\nАбо натисніть /cancel, щоб вийти з режиму діалогу

Hello 👋!\nBefore we send you a link to the group of *Business Club Millionario*, answer 4 questions.\nTo continue, \
select your language of communication.\nOr press /cancel to quit the dialog"""


async def start_conversation(update: Update, context: CallbackContext):
    """Обработчик запроса пользователя на добавление в группу"""
    keyboard = [[]]
    # Не забудь указать языки в entry_points conversation handler
    keyboard[0].append(InlineKeyboardButton('Українська', callback_data='uk'))
    keyboard[0].append(InlineKeyboardButton('English', callback_data='en'))
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=BASE_DIR / 'millionario_photo.jpg',
        caption=greeting,
        reply_markup=reply_markup,
        parse_mode='markdown'
    )
    return CHOOSING_LANGUAGE


async def set_language(update: Update, context: CallbackContext):
    """
    Стартуем разговор.
    Тут мы обрабатываем нажатие на кнопку выбора языка.
    Показываем пользователю первый вопрос.
    """
    query = update.callback_query
    await query.answer()
    lang = context.user_data['lang'] = query.data

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(translations['question1'][lang]),
        parse_mode='markdown'
    )

    return QUESTION1


async def show_question2(update: Update, context: CallbackContext):
    # Тут мы запоминаем ответ на вопрос 1. Показываем пользователю вопрос 2.
    context.user_data['question1'] = update.effective_message.text
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question2'][lang])

    return QUESTION2


async def show_question3(update: Update, context: CallbackContext):
    # Запоминаем ответ на вопрос 2. Показываем пользователю вопрос 3.
    context.user_data['question2'] = update.effective_message.text
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question3'][lang])

    return QUESTION3


async def show_question4(update: Update, context: CallbackContext):
    # Запоминаем ответ на вопрос 3. Показываем пользователю вопрос 4.
    context.user_data['question3'] = update.effective_message.text
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question4'][lang])

    return ACTION_SUCCESS


async def show_success_message(update: Update, context: CallbackContext):
    """
    Запоминаем ответ пользователя на вопрос 4.
    Показываем пользовалю сообщение об успешном заполнении анкеты.
    Рассылаем админам анкеты на рассмотрение.
    Заканчиваем разговор.
    """
    context.user_data['question4'] = update.effective_message.text
    lang = context.user_data['lang']
    group_link = await context.bot.create_chat_invite_link(
        chat_id=GROUP_CHAT_ID,
        expire_date=datetime.now() + timedelta(hours=24),
        member_limit=1
    )
    new_success_message = translations['success_message'][lang].replace('GROUP_LINK', group_link.invite_link)

    try:
        await update.message.reply_text(text=new_success_message)
    except BadRequest:
        pass

    ADMINS_CHAT_ID_LIST = decouple.config('ADMINS_CHAT_ID_LIST', cast=lambda v: [s.strip() for s in v.split(',')])

    if len(ADMINS_CHAT_ID_LIST):
        user_first_name = update.effective_message.chat.first_name
        user_last_name = update.effective_message.chat.last_name
        hello_text = f"Вітаю! Користувач *{user_first_name} {user_last_name}* хоче приєднатися до " \
                     f"бізнес клубу Millionario *{BUSINESS_CLUB_TITLE}*. Ознайомтесь з його анкетою."
        answers = f"{hello_text}\n*{translations['question1'][lang]}*: {context.user_data['question1']}\n"
        answers += f"*{translations['question2'][lang]}*: {context.user_data['question2']}\n"
        answers += f"*{translations['question3'][lang]}*: {context.user_data['question3']}\n"
        answers += f"*{translations['question4'][lang]}*: {context.user_data['question4']}"

        for chat_id in ADMINS_CHAT_ID_LIST:
            await context.bot.send_message(chat_id=chat_id, text=answers, parse_mode='markdown')

    return ConversationHandler.END


async def send_message_to_group(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text='Hola!', parse_mode='markdown')


async def show_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводим админу его chat_id, чтобы использовать для рассылки анкет"""
    await update.message.reply_text(str(update.effective_chat.id))


async def show_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать id группы"""
    await update.message.reply_text(str(update.effective_chat.id))


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(decouple.config('BOT_TOKEN')).build()

    application.add_handler(conv_handler)
    application.add_handler(message_conv_handler)
    application.add_handler(CommandHandler("show_my_id", show_my_id))

    application.add_handler(CommandHandler("show_group_id", show_group_id))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    reply_text = "Bye!\nYou quited the conversation."
    await update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='markdown',
    )

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start_conversation),
    ],
    states={
        CHOOSING_LANGUAGE: [
            CallbackQueryHandler(set_language, pattern='(uk|en)'),
        ],
        QUESTION1: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, show_question2),
        ],
        QUESTION2: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, show_question3),
        ],
        QUESTION3: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, show_question4),
        ],
        ACTION_SUCCESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, show_success_message),
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

if __name__ == "__main__":
    main()

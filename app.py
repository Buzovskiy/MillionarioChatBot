import logging
from pathlib import Path
import decouple
from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ChatJoinRequestHandler, \
    CallbackContext
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler, filters
from translations import translations


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

[QUESTION1, QUESTION2, QUESTION3, ACTION_SUCCESS] = range(4)


greeting = """
Здравствуйте! Вы отправили заявку на добавление в бизнес клуб Millionario. Прежде чем мы ее \
рассмотрим, ответьте, пожалуйста, на 4 вопроса.\n\n
Hello! You have sent an application to be added to the Millionario business club. Before we consider it, please answer\
4 questions.
"""


async def set_language(update: Update, context: CallbackContext):
    """
    Стартуем разговор.
    Тут мы обрабатываем нажатие на кнопку выбора языка.
    Показываем пользователю первый вопрос.
    """
    query = update.callback_query
    await query.answer()
    lang = context.user_data['lang'] = query.data
    reply_markup = InlineKeyboardMarkup([])
    await query.edit_message_caption(reply_markup=reply_markup)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=translations['question1'][lang])

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
    await update.message.reply_text(text=translations['success_message'][lang])
    ADMINS_CHAT_ID_LIST = decouple.config('ADMINS_CHAT_ID_LIST', cast=lambda v: [s.strip() for s in v.split(',')])
    if len(ADMINS_CHAT_ID_LIST):
        user_first_name = update.effective_message.chat.first_name
        user_last_name = update.effective_message.chat.last_name
        hello_text = f"Здравствуйте! Пользователь *{user_first_name} {user_last_name}* хочет присоединиться к " \
                     "бизнес клубу Millionario. Ознакомьтесь с его анкетой."
        answers = f"{hello_text}\n*{translations['question1'][lang]}*: {context.user_data['question1']}\n"
        answers += f"*{translations['question2'][lang]}*: {context.user_data['question2']}\n"
        answers += f"*{translations['question3'][lang]}*: {context.user_data['question3']}\n"
        answers += f"*{translations['question4'][lang]}*: {context.user_data['question4']}"

        for chat_id in ADMINS_CHAT_ID_LIST:
            await context.bot.send_message(chat_id=chat_id, text=answers, parse_mode='markdown')

    return ConversationHandler.END


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик запроса пользователя на добавление в группу"""
    user_chat_id = update.chat_join_request.user_chat_id
    keyboard = [[]]
    # Не забудь указать языки в entry_points conversation handler
    keyboard[0].append(InlineKeyboardButton('русский', callback_data='ru'))
    keyboard[0].append(InlineKeyboardButton('english', callback_data='en'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=user_chat_id,
        photo=BASE_DIR / 'millionario_photo.jpg',
        caption=greeting,
        reply_markup=reply_markup
    )


async def show_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводим админу его chat_id, чтобы использовать для рассылки анкет"""
    await update.message.reply_text(str(update.effective_chat.id))


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(decouple.config('BOT_TOKEN')).build()

    application.add_handler(ChatJoinRequestHandler(join_request))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("show_my_id", show_my_id))

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
        CallbackQueryHandler(set_language, pattern='(ru|en)'),
    ],
    states={
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

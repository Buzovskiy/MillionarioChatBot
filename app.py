#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


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
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ChatJoinRequestHandler, \
    CallbackContext
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler, filters
from translations import translations

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

[QUESTION1, QUESTION2, QUESTION3, ACTION_SUCCESS] = range(4)



# # Define a few command handlers. These usually take the two arguments update and
# # context.
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Hi {user.mention_html()}!",
#         reply_markup=ForceReply(selective=True),
#     )


# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /help is issued."""
#     await update.message.reply_text("Help!")

greeting = """
Здравствуйте! Вы отправили заявку на добавление в бизнес клуб Millionario. Прежде чем мы ее \
рассмотрим, ответьте, пожалуйста, на 4 вопроса.
"""

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # user_chat_id = update.chat_join_request.user_chat_id
    # user_first_name = update.chat_join_request.from_user.first_name
    # user_last_name = update.chat_join_request.from_user.last_name
    user_chat_id = update.effective_chat.id
    user_first_name = 'Vitalii'
    user_last_name = 'Buzovskyi'
    """Echo the user message."""
    keyboard = [[]]
    # Не забудь указать языки в entry_points conversation handler
    keyboard[0].append(InlineKeyboardButton('українська', callback_data='uk'))
    keyboard[0].append(InlineKeyboardButton('english', callback_data='en'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=user_chat_id,
        photo=BASE_DIR / 'millionario_photo.jpg',
        caption=greeting
    )
    # await update.message.reply_text('Hi!\nPlease choose language.\nOr enter /cancel to quit', reply_markup=reply_markup)


async def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    lang = context.user_data['lang'] = query.data
    reply_markup = InlineKeyboardMarkup([])
    await query.edit_message_text(text=translations['question1'][lang], reply_markup=reply_markup, parse_mode='markdown')

    return QUESTION1


async def show_question2(update: Update, context: CallbackContext):
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question2'][lang])

    return QUESTION2


async def show_question3(update: Update, context: CallbackContext):
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question3'][lang])

    return QUESTION3


async def show_question4(update: Update, context: CallbackContext):
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['question4'][lang])

    return ACTION_SUCCESS


async def show_success_message(update: Update, context: CallbackContext):
    lang = context.user_data['lang']
    await update.message.reply_text(text=translations['success_message'][lang])

    return ConversationHandler.END



async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.chat_join_request.user_chat_id
    # user_first_name = update.chat_join_request.from_user.first_name
    # user_last_name = update.chat_join_request.from_user.last_name
    #
    # update.message.reply_text('Hi!\nPlease choose language.\nOr enter /cancel to quit', reply_markup=reply_markup)
    # await context.bot.send_message(chat_id=user_chat_id, text='helloooooo')
    # # await context.bot.approve_chat_join_request(
    # #     chat_id=update.effective_chat.id, user_id=update.effective_user.id
    # # )
    keyboard = [[]]
    # Не забудь указать языки в entry_points conversation handler
    keyboard[0].append(InlineKeyboardButton('українська', callback_data='uk'))
    keyboard[0].append(InlineKeyboardButton('english', callback_data='en'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text('Hi!\nPlease choose language.\nOr enter /cancel to quit', reply_markup=reply_markup)
    await context.bot.send_message(
        chat_id=user_chat_id,
        text='Hi!\nPlease choose language.\nOr enter /cancel to quit',
        reply_markup=reply_markup
    )

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6387846707:AAHFDXEl7wV8-Ib21Aic82gjMFMSGIl_CzI").build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # application.add_handler(MessageHandler(None, echo))
    application.add_handler(CommandHandler("go", echo))
    application.add_handler(ChatJoinRequestHandler(join_request))
    application.add_handler(conv_handler)
    # application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    reply_text = "Bye!\nYou quited.\nIn order to start again enter */go*"
    await update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='markdown',
    )

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[
        # CommandHandler('start', show_languages_buttons),
        # CommandHandler('manager', show_languages_buttons),
        CallbackQueryHandler(set_language, pattern='(uk|en)'),
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
        # MAIN_MENU: [
        #     MessageHandler(Filters.text & ~Filters.command, cancel),
        #     CallbackQueryHandler(show_shops_to_bind, pattern='^show_shops_to_bind$'),
        #     CallbackQueryHandler(show_shops_to_unbind, pattern='^show_shops_to_unbind$'),
        # ],
        # PASS_CODE: [MessageHandler(Filters.text & ~Filters.command, pass_code)],
        # BIND_SHOP_TO_MANAGER: [
        #     MessageHandler(Filters.text & ~Filters.command, cancel),
        #     CallbackQueryHandler(show_main_menu, pattern='^return_to_previous_menu$'),
        #     CallbackQueryHandler(bind_shop),
        # ],
        # UNBIND_SHOP_FROM_MANAGER: [
        #     MessageHandler(Filters.text & ~Filters.command, cancel),
        #     CallbackQueryHandler(show_main_menu, pattern='^return_to_previous_menu$'),
        #     CallbackQueryHandler(unbind_shop),
        # ],
        # CHECK_PASS_CODE_FOR_SHOP: [
        #     MessageHandler(Filters.text & ~Filters.command, check_pass_code_for_shop),
        #     CallbackQueryHandler(show_main_menu, pattern='^return_to_previous_menu$'),
        # ],

    },
    fallbacks=[CommandHandler('cancel', cancel)],
)


if __name__ == "__main__":
    main()
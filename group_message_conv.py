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


GROUP_CHAT_ID = decouple.config('GROUP_CHAT_ID')

[MESSAGE_SENT] = [1]


async def start_conversation(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Нашипіть повідомлення в групу',
        parse_mode='markdown'
    )
    return MESSAGE_SENT


async def show_success_message(update: Update, context: CallbackContext):

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=update.message.text, parse_mode='markdown')

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    reply_text = "Bye!\nYou quited the conversation."
    await update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='markdown',
    )

    return ConversationHandler.END


message_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('send_message_to_group', start_conversation),
    ],
    states={
        MESSAGE_SENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, show_success_message),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

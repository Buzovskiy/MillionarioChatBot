import logging

from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ChatJoinRequestHandler, CallbackContext
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler

[SET_LANGUAGE, PASS_CODE, BIND_SHOP_TO_MANAGER, UNBIND_SHOP_FROM_MANAGER, MAIN_MENU, CHECK_PASS_CODE_FOR_SHOP,
 ACTION_SUCCESS] = range(7)


async def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    # query.answer()
    print(988787878787)
    # translation.activate(query.data)
    # return show_main_menu(update=update, context=context)


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    # reply_text = str(_("Bye!\nYou quited.\nIn order to start again enter */manager* or */start*"))
    # update.message.reply_text(
    #     reply_text,
    #     reply_markup=ReplyKeyboardRemove(),
    #     parse_mode='markdown',
    # )

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[
        # CommandHandler('start', show_languages_buttons),
        # CommandHandler('manager', show_languages_buttons),
        CallbackQueryHandler(set_language, pattern='(uk|en)'),
    ],
    states={
        SET_LANGUAGE: [
            # CallbackQueryHandler(set_language),
            # MessageHandler(Filters.text & ~Filters.command, cancel),
        ],
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
        # ACTION_SUCCESS: [
        #     MessageHandler(Filters.text & ~Filters.command, cancel),
        #     CallbackQueryHandler(show_main_menu, pattern='^return_to_previous_menu$'),
        # ]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)


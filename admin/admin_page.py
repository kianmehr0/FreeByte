import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText
from admin.admin_utilities import admin_access
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from crud import crud
from database_sqlalchemy import SessionLocal

@admin_access
async def admin_page(update, context):
    user_detail = update.effective_chat

    keyboard = [
        [InlineKeyboardButton('VPN Section', callback_data=f"admin_vpn"),
         InlineKeyboardButton('Manage Users', callback_data=f"admin_manage_users__1")]
    ]
    text = '<b>Select Section who you want manage:</b>'

    if update.callback_query:
        return await update.callback_query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    return await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


@admin_access
async def add_credit_for_user(update, context):
    user_detail = update.effective_chat
    ft_instance = FindText(None, None)
    try:
        with SessionLocal() as session:
            with session.begin():

                amount, user_chat_id = context.args

                finacial_report = crud.create_financial_report(
                    session, 'recive',
                    chat_id=user_chat_id,
                    amount=int(amount),
                    action='increase_balance_by_admin',
                    service_id=None,
                    payment_status='not paid',
                    payment_getway='wallet',
                    currency='IRT'
                )

                crud.add_credit_to_wallet(session, finacial_report)
                text = await ft_instance.find_from_database(user_chat_id, 'amount_added_to_wallet_successfully')
                text = text.format(f"{int(amount):,}")

                await context.bot.send_message(chat_id=user_chat_id, text=text)
                await context.bot.send_message(chat_id=user_detail.id, text=f'+ successfully Add {int(amount):,} IRT to user wallet.')

    except Exception as e:
        await context.bot.send_message(chat_id=user_detail.id, text=f'- failed to add credit to user wallet.\n{str(e)}')

from typing import TYPE_CHECKING

from telegram import Update
from telegram.ext import CallbackContext


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreCheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Repairs-Filter-payment":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")

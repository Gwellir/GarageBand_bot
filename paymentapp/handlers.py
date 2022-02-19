from telegram import Update
from telegram.ext import CallbackContext

from paymentapp.constants import DonationParams
from paymentapp.models import Donation
from tgbot.bot.utils import extract_user_data_from_update


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreCheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != DonationParams.PAYMENT_ID:
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    payment = update.effective_message.successful_payment
    if payment.invoice_payload == DonationParams.PAYMENT_ID:
        user_data = extract_user_data_from_update(update)
        Donation.create(user_data, payment.total_amount, payment.currency)
        update.message.reply_text("Спасибо за пожертвование на развитие проекта!")
    else:
        update.message.reply_text("Спасибо за оплату!")

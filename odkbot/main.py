import json
import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

# Prepare the logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
odklog = logging.getLogger("odkbot")


def sanitize_str(str: str) -> str:
    return str.replace("/", "\\/").replace("!", "\\!")


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,  # type:ignore
        text="Ci manca la sicura!",
    )


def radio_check(update: Update, context: CallbackContext) -> None:

    if not context.args:
        odklog.warn("radiocheck_no_title")
        context.bot.send_message(
            chat_id=update.effective_chat.id,  # type:ignore
            parse_mode=ParseMode.MARKDOWN_V2,
            text=sanitize_str(
                "BOOM! \U0001F4A5 Hai perso una granata per caso?\nComunque, ho bisogno di una domanda per funzionare, ad esempio:\n```\n/radiocheck stasera 21.30?```"
            ),
        )
        odklog.warn("radiocheck_no_title - info message sent.")
    else:
        odklog.info("radiocheck")
        question = " ".join(context.args).capitalize()
        context.bot.send_poll(
            chat_id=update.effective_chat.id,  # type:ignore
            question=question,
            options=["\u2705 Sì", "\u2B55 No", "\u2754 Forse"],
            is_anonymous=False,
        )
        odklog.info("radiocheck - Poll sent!")


def run() -> None:
    """This is the function that the script will run."""

    try:
        with open("credentials.json", "r") as f:
            data = json.load(f)
            token = data["token"]
    except FileNotFoundError:
        print(
            "[ERR] You need a 'credentials.json' file with a key called 'token'. This should be your bot api token."
        )
        exit(1)
    except KeyError:
        print("[ERR] The 'credentials.json' file should contain a key called 'token'.")
        exit(1)

    odklog.info("Credentials file read. Starting bot...")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    radio_check_handler = CommandHandler("radiocheck", radio_check)
    dispatcher.add_handler(radio_check_handler)

    updater.start_polling()

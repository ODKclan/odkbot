import json
import logging
import subprocess
from functools import reduce
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

# Prepare the logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
odklog = logging.getLogger("odkbot")
command_help_messages = []


def add_command_help_message(command: str, description: str) -> None:
    command_help_messages.append(f"`{command}`\n*>* {description}")


def get_git_revision_short_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


def sanitize_str(string: str) -> str:
    for char in ["/", "!", ".", "<", ">"]:
        string = string.replace(char, f"\\{char}")
    return string


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,  # type:ignore
        text="Ci manca la sicura!",
    )


def print_help(update: Update, context: CallbackContext) -> None:
    odklog.info("help")
    help_header = "Bravo! L'uomo saggio cerca la conoscenza e pensa prima di agire... aspetta un momento... sicuro di essere un ODK?!\n"
    help_msg = sanitize_str(
        reduce(lambda x, y: x + "\n" + y, command_help_messages, help_header)
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,  # type:ignore
        parse_mode=ParseMode.MARKDOWN_V2,
        text=help_msg,
    )
    odklog.info("help - Given!")


def radio_check(update: Update, context: CallbackContext) -> None:
    if not context.args:
        odklog.warn("radiocheck_no_title")
        context.bot.send_message(
            chat_id=update.effective_chat.id,  # type:ignore
            parse_mode=ParseMode.MARKDOWN_V2,
            text=sanitize_str(
                "*BOOM!* \U0001F4A5 Hai perso una granata per caso?\nComunque, ho bisogno di una domanda per funzionare, ad esempio:\n```\n/radiocheck stasera 21.30?```"
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
    version = get_git_revision_short_hash()
    odklog.info("-------------------------------")
    odklog.info(f"Starting ODKBot version {version}")

    try:
        with open("settings.json", "r") as f:
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

    odklog.info("Credentials file read.")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    radio_check_handler = CommandHandler("radiocheck", radio_check)
    dispatcher.add_handler(radio_check_handler)
    add_command_help_message(
        "/radiocheck <domanda>",
        "Crea un sondaggio con la _domanda_ fornita, offrendo come possibili risposte _sì_, _no_, _forse_",
    )

    help_handler = CommandHandler("help", print_help)
    dispatcher.add_handler(help_handler)
    add_command_help_message("/help", "Mostra questo messaggio")

    command_help_messages.append(f"\n_ODKBot versione {version}_")

    updater.start_polling()

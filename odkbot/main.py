import logging
import json

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)

from odkbot.utils import (
    get_git_revision_short_hash,
    HelpPrinter,
    add_command,
    send_msg,
)

#
# LOGGER
#
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
odklog = logging.getLogger("odkbot")


#
# HANDLERS
#


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_msg("Ci manca la sicura!", update, context)


async def print_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    odklog.info("help")
    await send_msg(HelpPrinter.build_help_message(), update, context)
    odklog.info("help - Given!")


async def radio_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        odklog.warning("radiocheck_no_title")
        await send_msg(
            "*BOOM!* \U0001F4A5 Hai perso una granata per caso?\nComunque, ho bisogno di una domanda per funzionare,"
            " ad esempio:\n```\n/radiocheck stasera 21.30?```",
            update,
            context,
        )
        odklog.warning("radiocheck_no_title - info message sent.")
    else:
        odklog.info("radiocheck")
        question = " ".join(context.args).capitalize()
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,  # type:ignore
            message_thread_id=update.effective_message.message_thread_id,
            question=question,
            options=["\u2705 Sì", "\u2B55 No", "\u2754 Forse"],
            is_anonymous=False,
        )
        odklog.info("radiocheck - Poll sent!")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_msg(
        "Non capisco! Usa  `/help`  per vedere la lista dei comandi che supporto.",
        update,
        context,
    )


#
# ENTRYPOINTS
#
def run_dev():
    """This is the function that the odkbot_dev script will run."""
    run("dev")


def run_prod():
    """This is the function that the odkbot_prod script will run."""
    run("prod")


def run(env: str = "prod"):
    """Launch the bot with the given environment."""

    version = get_git_revision_short_hash()
    odklog.info("-------------------------------")
    odklog.info(f"Starting ODKBot version {version}")

    HelpPrinter.set_version(version)

    try:
        with open("settings.json", "r") as f:
            data = json.load(f)
            token = data[f"token_{env}"]
    except FileNotFoundError:
        print(
            "[ERR] You need a 'settings.json' file with a key called 'token'. This should be your bot api token."
        )
        exit(1)
    except KeyError:
        print("[ERR] The 'settings.json' file should contain a key called 'token'.")
        exit(1)

    odklog.info("Credentials file read.")

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    add_command(
        application=application,
        name="radiocheck",
        hook=radio_check,
        help_header="/radiocheck <domanda>",
        help_message="Crea un sondaggio con la _domanda_ fornita, offrendo come possibili risposte _sì_, _no_, _forse_",
    )

    add_command(
        application=application,
        name="help",
        hook=print_help,
        help_header="/help",
        help_message="Mostra questo messaggio",
    )

    # This handler MUST be registered last to catch all unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

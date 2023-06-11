import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)

from odkbot.utils import (
    add_command,
    send_msg,
    State,
    handle_handler_errors,
    CommandUsage,
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


@handle_handler_errors
async def print_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    odklog.info("help")
    message = (
        "Bravo! L'uomo saggio cerca la conoscenza e pensa prima di agire... aspetta un momento..."
        " sicuro di essere un ODK?!\n\n"
        + "\n".join(State.help_messages)
        + f"\n\n_ODKBot versione {State.version}_"
    )
    await send_msg(message, update, context)
    odklog.info("help - Given!")


@handle_handler_errors
async def radio_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    odklog.info("radiocheck")

    if not context.args:
        question = "Stasera?"
    else:
        question = " ".join(context.args).capitalize()

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,  # type:ignore
        message_thread_id=update.effective_message.message_thread_id,
        question=question,
        options=["\u2705 Sì", "\u2B55 No", "\u2754 Forse"],
        is_anonymous=False,
    )
    odklog.info("radiocheck - Poll sent!")


@handle_handler_errors
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

    State.init(env=env, logger=odklog)

    application = ApplicationBuilder().token(State.token).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    add_command(
        application=application,
        command="radiocheck",
        hook=radio_check,
        command_usage_list=[
            CommandUsage(
                usage="/radiocheck",
                description="Crea un sondaggio che recita 'Stasera?', offrendo come possibili risposte _sì_,"
                " _no_, _forse_",
            ),
            CommandUsage(
                usage="/radiocheck <domanda>",
                description="Crea un sondaggio con la _domanda_ fornita, offrendo come possibili risposte _sì_,"
                " _no_, _forse_",
            ),
        ],
    )

    add_command(
        application=application,
        command="help",
        hook=print_help,
        command_usage_list=[
            CommandUsage(
                usage="/help",
                description="Mostra questo messaggio",
            )
        ],
    )

    # This handler MUST be registered last to catch all unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

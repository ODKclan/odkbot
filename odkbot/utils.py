import functools
import json
import subprocess
from logging import Logger
from typing import Callable, List, NamedTuple

from telegram import Update
from telegram.constants import ParseMode

from telegram.ext import CommandHandler, Application, ContextTypes


class State:
    """Container used to describe the global application state."""

    settings_file_name: str = "settings.json"
    changelog_file_name: str = "changelog.md"
    changelog: str = "empty"
    logger: Logger
    token: str
    version: str
    support_nicks: []
    help_messages = []

    @classmethod
    def init(cls, env: str, logger: Logger) -> None:
        """Set the initial application state."""
        cls.logger = logger
        cls.version = cls._get_bot_version()

        cls.logger.info("-------------------------------")
        cls.logger.info(f"Starting ODKBot version {cls.version}")

        token_key_name = f"token_{env}"

        try:
            with open(cls.settings_file_name, "r") as f:
                data = json.load(f)
            # mandatory
            cls.token = data[token_key_name]
            # optionals
            cls.support_nicks = data.get("support_nicks", [])
            cls.logger.info("Credentials file read.")
        except FileNotFoundError:
            cls.logger.error(
                f"You need a '{cls.settings_file_name}' file with a key called '{token_key_name}'. "
                f"This should be your bot api token."
            )
            exit(1)
        except KeyError as key_name:
            cls.logger.error(
                f"The '{cls.settings_file_name}' file should contain a key called {key_name}."
            )
            exit(1)

        try:
            with open(cls.changelog_file_name, "r") as f:
                cls.changelog = f.read()
        except FileNotFoundError:
            cls.logger.warning(f"Changelog file '{cls.changelog_file_name}' not found!")

    @classmethod
    def add_command_help_message(cls, command: str, description: str) -> None:
        """Save the command help message in the global state, useful to print them all later."""
        cls.help_messages.append(f"*>* `{command}`\n{description}")

    @classmethod
    def _get_bot_version(cls) -> str:
        """Return the current bot version as git revision short hash."""
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
                .decode("ascii")
                .strip()
            )
        except (Exception,):
            return "none"


def sanitize_str(string: str) -> str:
    """Make sure no forbidden character gets printed."""
    for char in ["/", "!", ".", "<", ">", "(", ")", "#", "-"]:
        string = string.replace(char, f"\\{char}")
    return string


class CommandUsage(NamedTuple):
    """Tuple used to describe a command usage option."""

    usage: str
    description: str


def add_command(
    application: Application,
    command: str,
    hook: Callable,
    command_usage_list: List[CommandUsage],
) -> None:
    """Add a command to the bot."""
    handler = CommandHandler(command, hook)
    application.add_handler(handler)
    for command_help in command_usage_list:
        State.add_command_help_message(command_help.usage, command_help.description)


async def send_msg(message: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper used to send a message from a handler hook."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        text=sanitize_str(message),
        disable_web_page_preview=True,
    )


def handle_handler_errors(func: Callable):
    """Async decorator used on handlers to catch and remedy certain kinds of error."""

    @functools.wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message.text
        if (
            update.effective_chat.is_forum
            and not update.effective_message.message_thread_id
            and (message.endswith("@ODKDEV_BOT") or message.endswith("@ODKBOT"))
        ):
            #
            # When sending a bot command in the form of '/command@BOTNAME' in a topic, the message will not be
            # delivered to the right topic, but appear in the '#general' default chat instead.
            # This message has the 'message_thread_id' field set to none, even if it was sent in a topic.
            #
            # Related issue: https://bugs.telegram.org/c/28921
            # Confirmed affected client: Telegram Web A version 1.61.20
            #
            State.logger.warning("Thread id missing in a topic message!")
            cmd = update.effective_message.text.replace("@ODKDEV_BOT", "").replace(
                "@ODKBOT", ""
            )
            message = (
                f"@{update.effective_message.from_user.username}! Hai trovato un bug nel tuo client Telegram, "
                "peggio che beccare una pietruzza di spigolo con un veicolo su Arma! \U0001F4A5\n\n"
                f"Come workaround, prova a scrivere soltanto `{cmd}` (occhio a farlo *nel topic in cui desideravi "
                f"lanciare il comando*)."
            )
            if State.support_nicks:
                message += "\n\ncc: " + " ".join(
                    (f"@{nick}" for nick in State.support_nicks)
                )

            await send_msg(message, update, context)

        else:
            # Nothing went wrong, call the handler
            return await func(update, context)

    return wrapped

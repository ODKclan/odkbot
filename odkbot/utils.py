import subprocess
from typing import Callable

from telegram import Update
from telegram.constants import ParseMode

from telegram.ext import CommandHandler, Application, ContextTypes


class HelpPrinter:
    """Dummy container class used to build the help message."""

    _messages = []
    _bot_version = ""

    @classmethod
    def add_command_help_message(cls, command: str, description: str) -> None:
        cls._messages.append(f"`{command}`\n*>* {description}")

    @classmethod
    def set_version(cls, version: str) -> None:
        cls._bot_version = version

    @classmethod
    def build_help_message(cls) -> str:
        return (
            "Bravo! L'uomo saggio cerca la conoscenza e pensa prima di agire... aspetta un momento..."
            " sicuro di essere un ODK?!\n\n"
            + "\n".join(HelpPrinter._messages)
            + f"\n\n_ODKBot versione {cls._bot_version}_"
        )


def sanitize_str(string: str) -> str:
    """Make sure no forbidden character gets printed."""
    for char in ["/", "!", ".", "<", ">"]:
        string = string.replace(char, f"\\{char}")
    return string


def get_git_revision_short_hash() -> str:
    """Recover the current bot version as git revision short hash."""
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


def add_command(
    application: Application,
    name: str,
    hook: Callable,
    help_header: str,
    help_message: str,
) -> None:
    """Add a command to the bot."""
    handler = CommandHandler(name, hook)
    application.add_handler(handler)
    HelpPrinter.add_command_help_message(help_header, help_message)


async def send_msg(message: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convenient way to send a message from a handler hook."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        text=sanitize_str(message),
    )

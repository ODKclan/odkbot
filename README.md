A simple telegram bot used to plan our evenings.

### Dependencies

- Python 3.8+
- git
- [Poetry](https://python-poetry.org/)

### Installation

Clone the repo:

```
git clone https://github.com/ODKclan/odkbot.git
```

Run:

```console
cd odkbot
poetry install
```

Create a file called `settings.json`:

```json
{
  "token_prod": "your-telegram-token-goes-here",
  "support_nicks": ["User123"]
}
```

`token_prod` is mandatory, it's the string given by Telegram's BotFather. `support_nicks` is an optional list of Telegram
user that will be pinged if a bug is encountered.


### Launch the bot

Run:

```console
poetry run odkbot_prod
```

or, on Windows:

```console
.\run.bat
```

### Install as a Windows service

Add these fields to the `settings.json` file:

```json
{
  "service_name": "ODKBot",
  "service_user": ".\\user",
  "service_password": "password",
  "nssm_version": "2.24"
}
```
`service_user` and `service_password` are optional: if both are present, the service will be run with that user.

Open a powershell console as Administrator and launch:

```console
.\install_service.ps1 -env prod
```

This will download `nssm.exe` and install, enable and start a Windows service for the bot using [nssm](https://nssm.cc/).

You can control the service like this:

```console
.\nssm.exe status ODKBot
.\nssm.exe stop ODKBot
.\nssm.exe start ODKBot
...
```

If you need to remove the service, launch:

```console
.\remove_service.ps1
```

### Devs

If a `token_dev` key is present in `settings.json` the bot can be run with `poetry run odkbot_dev` to launch the dev
version of the bot.

String used to assign commands to BotFather:

```
radiocheck - Esegui un check presenze
changelog - Elenca le ultime modifiche al bot
help - Mostra un messaggio di aiuto
```
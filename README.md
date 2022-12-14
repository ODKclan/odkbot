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
  "token": "your-telegram-token-goes-here"
}
```

### Launch the bot

Run:

```console
poetry run odkbot
```

or, on Windows:

```console
.\run.bat
```

### Install as a Windows service

Follow this template in the `settings.json` file:

```json
{
  "token": "your-telegram-token-goes-here",
  "service_name": "ODKBot",
  "service_user": ".\\user",
  "service_password": "password",
  "nssm_version": "2.24"
}
```
`service_user` and `service_password` are optional: if both are present, the service will be run with that user.

Open a powershell console as Administrator and launch:

```console
.\install_service.ps1
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
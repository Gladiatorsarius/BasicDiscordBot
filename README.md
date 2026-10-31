# BasicDiscordBot

BasicDiscordBot is a bot harness which provides basic functionality for a
Discord bot written in Python using [`discord.py`](https://discordpy.readthedocs.io/en/stable/).

The package lives in [`src/basicdiscordbot`](./src/basicdiscordbot).

It is meant to be a useful starting point, not a framework that takes over
your whole bot. Add the cog to your own `commands.Bot`, keep your own commands
and business logic, and use only the helpers you actually need.

## Install

The package requires Python 3.14 or newer and `discord.py` 2.7 or newer.

```bash
pip install basicdiscordbot
```

If you are working on this repository itself, install the locked development
environment with:

```bash
uv sync
```

## Use the package

The package exports `BasicDiscordBot` directly:

```python
import os

import discord
from discord.ext import commands

from basicdiscordbot import BasicDiscordBot


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    await bot.add_cog(
        BasicDiscordBot(
            bot,
            dev_guild_id=int(os.environ["DEV_GUILD_ID"]),
            original_source_code_url="https://github.com/your-name/your-bot",
            testing=False,
        )
    )


bot.run(os.environ["DISCORD_BOT_TOKEN"])
```

The exact options are all optional apart from the `client`:

| Option | What it is for |
| --- | --- |
| `dev_guild_id` | The development guild used for testing and guild command syncs. |
| `original_source_code_url` | A link back to the bot's source code for the info command. |
| `testing` | Uses the testing command-sync flow and file-based restart helper. |
| `systemctl_name` | The systemd service name used when automatic restarts are enabled. |
| `auto_restart` | Restarts the systemd service after a Git update. |
| `auto_pull` | Pulls a newer Git version automatically. |
| `send_developer_infos` | Includes developer information in the `/info` response. |
| `developer_announcment_channel_id` | Channel for startup and developer announcements. If omitted, the bot DMs the team/owner. |
| `changelog_channel_id` | Channel where Git changelog updates are posted. |

The package currently adds:

- `/info` for the running bot version and source link.
- `/allservers` for an owner-only list of the servers the bot is in.
- `SyncCommands` for team/owner command syncing.
- Startup and update notifications.
- Optional changelog messages based on `CHANGELOG.md`.
- Optional Git polling, pulling, and systemd restart support.

The Git and systemd features are opt-in. If you do not need them, leave the
related options disabled or unset.

## The demo

[`Main.py`](./Main.py) is only an implementation demo. It shows one way to
wire the package into a bot using environment variables and a `.env` file; it
is not intended to be a drop-in bot for every project. For information about
creating and using cogs, see the
[discord.py Cogs documentation](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html).

For a quick look at the demo bot, you can [invite it to a Discord
server](https://discord.com/oauth2/authorize?client_id=1565396977649320129).

For a real implementation built around this package, check out
[Discord_No_Disturb_Bot](https://github.com/Gladiatorsarius/Discord_No_Disturb_Bot).

## Development

The project uses `uv` for its environment and packaging:

```bash
uv sync
uv build
```

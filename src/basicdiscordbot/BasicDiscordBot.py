import discord
import os
from discord.ext import commands, tasks
from types import SimpleNamespace
from . import git_commands
import subprocess
from discord import app_commands

class BasicDiscordBot(commands.Cog):
    def __init__(
        self,
        client,
        dev_guild_id: int= None,
        developer_id: int = None,
        original_source_code_url: str = None,
        original_author_id: int = None,
        original_author_name: str = None,
        testing: bool = False,
        version: str = None,
    ):
        self.client = client

        self.Dev_Guild_ID = dev_guild_id
        self.Developer_ID = developer_id
    
        self.Original_Source_Code_URL = original_source_code_url
        self.Original_Author_ID = original_author_id
        self.Original_Author_Name = original_author_name
        self.Version = version
    
        self.testing = testing


    def check_developer_id(self, user_id: int) -> bool:
        return user_id == self.Developer_ID

    def is_developer(self):
        async def predicate(interaction: discord.Interaction):
            return self.check_developer_id(interaction.user.id)
        return app_commands.check(predicate)

    async def cog_load(self):
        try:
            if not self.testing:
                synced_Global = await self.client.tree.sync()
                if self.Dev_Guild_ID is not None:
                    synced_Guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                    print(f"Synced {len(synced_Global)} global commands and {len(synced_Guild)} guild commands.")
                else:
                    print(f"Synced {len(synced_Global)} global commands.")
            else:
                if self.Dev_Guild_ID is None:
                    raise ValueError("In testing mode, you must provide a Dev_Guild_ID to sync commands to a specific guild.")
                self.client.tree.copy_global_to(guild=discord.Object(id=self.Dev_Guild_ID))
                synced_guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                print(f"Synced {len(synced_guild)} commands to the guild {self.Dev_Guild_ID}.")
                self.client.tree.clear_commands(guild=None)
                await self.client.tree.sync()
                print("Cleared global commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.client.user.name}')
        if self.Developer_ID is not None and self.Version is not None:
            developer_user = await self.client.fetch_user(self.Developer_ID)
            if developer_user:
                await developer_user.send(f"Bot Started Successfully. Version: {self.Version}")
        elif self.Developer_ID is not None:
            developer_user = await self.client.fetch_user(self.Developer_ID)
            if developer_user:
                await developer_user.send(f"Bot Started Successfully.")
        elif self.Version is not None:
            print(f"Bot Started Successfully. Version: {self.Version}")
        else:
            print(f"Bot Started Successfully.")
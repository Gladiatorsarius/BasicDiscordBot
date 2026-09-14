import discord
import os
from discord.ext import commands, tasks
from types import SimpleNamespace
from . import git_commands
import subprocess
from discord import app_commands
from pathlib import Path

class BasicDiscordBot(commands.Cog):
    def __init__(
        self,
        client,
        dev_guild_id: int= None,
        original_source_code_url: str = None,
        original_author_id: int = None,
        original_author_name: str = None,
        testing: bool = False,
        version: str = None,
    ):
        self.client = client

        self.Dev_Guild_ID = dev_guild_id
    
        self.Original_Source_Code_URL = original_source_code_url
        self.Original_Author_ID = original_author_id
        self.Original_Author_Name = original_author_name
        self.Version = version
    
        self.testing = testing


    async def cog_load(self):
        try:
            dev_guild = await self.client.fetch_guild(self.Dev_Guild_ID) if self.Dev_Guild_ID is not None else None
            if not self.testing:
                synced_Global = await self.client.tree.sync()
                if self.Dev_Guild_ID is not None:
                    synced_Guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                    print(f"Synced {len(synced_Global)} global commands and {len(synced_Guild)} to {dev_guild.name}.")
                else:
                    print(f"Synced {len(synced_Global)} global commands.")
            else:
                if self.Dev_Guild_ID is None:
                    raise ValueError("In testing mode, you must provide a Dev_Guild_ID to sync commands to a specific guild.")
                self.client.tree.copy_global_to(guild=discord.Object(id=self.Dev_Guild_ID))
                synced_guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                print(f"Synced {len(synced_guild)} commands to {dev_guild.name}.")
                self.client.tree.clear_commands(guild=None)
                await self.client.tree.sync()
                print("Cleared global commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")
        await self.get_Team_members()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.testing:
            if self.Version is not None:
                await self.send_team_dm(f"Bot Started Successfully. Version: {self.Version}")
                print(f'Logged in as {self.client.user.name}. Version: {self.Version }')
            elif self.Version is None:
                await self.send_team_dm(f"Bot Started Successfully.")
                print(f'Logged in as {self.client.user.name}')
            if not self.update_git.is_running():
                self.update_git.start()
        else:
            if not self.restart_helper.is_running():
                self.restart_helper.start()
            print(f'Logged in as {self.client.user.name} in testing mode.')


    def check_team_member(self, user_id: int) -> bool:
        return user_id in self.team_member_ids

    def is_team_member(self):
        async def predicate(self, interaction: discord.Interaction):
            return self.check_team_member(interaction.user.id)
        return app_commands.check(predicate)

    async def send_team_dm(self, message: str):
        for member_id in self.team_member_ids:
            member = await self.client.fetch_user(member_id)
            if member:
                try:
                    await member.send(message)
                except Exception as e:
                    print(f"Failed to send DM to {member.name}: {e}")



    async def get_Team_members(self):
        self.team_member_ids = []
        info = await self.client.application_info()
        if info.team is not None:
            team_members = info.team.members
            for member in team_members:
                self.team_member_ids.append(member.id)
        else:
            owner = info.owner
            self.team_member_ids.append(owner.id)

    
    @tasks.loop(seconds=1)
    async def restart_helper(self):
        if self.testing:
            base_dir = Path.cwd()
            shutdown_file = base_dir / "shutdown.txt"
            restart_file = base_dir / "restart.txt"
            startup_file = base_dir / "startup.txt"

            if shutdown_file.exists():
                print("Shutdown signal received. Shutting down...")
                shutdown_file.unlink()
                await self.client.close()
                return

            if restart_file.exists():
                print("Restart signal received. Restarting...")
                restart_file.unlink()
                startup_file.touch()
                await self.client.close()

    @restart_helper.before_loop
    async def before_restart_helper(self):
        if not self.testing:
            self.restart_helper.stop()
        await self.client.wait_until_ready()

    @tasks.loop(minutes=30)
    async def update_git(self):
        pass


    #else:


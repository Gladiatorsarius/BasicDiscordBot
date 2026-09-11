import discord
import os
import logging
from discord.ext import commands, tasks
from types import SimpleNamespace
from . import git_commands
import subprocess

class BasicDiscordBot(commands.cog):
    def __init__(
        self,
        dev_guild_id: int,
        developer_id: int,
        original_source_code_url: str,
        original_author_id: int,
        original_author_name: str,
        testing: bool,
        version: str,
        command_prefix: str,
        intents: discord.Intents
    ):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.Dev_Guild_ID = dev_guild_id
        self.Developer_ID = developer_id
    
        self.Original_Source_Code_URL = original_source_code_url
        self.Original_Author_ID = original_author_id
        self.Original_Author_Name = original_author_name
        self.Version = version
    
        self.testing = testing
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    

def BasicDiscordBot(dev_guild_id: int,
            developer_id: int,
            original_source_code_url: str,
            original_author_id: int,
            original_author_name: str,
            testing: bool,
            version: str,
            command_prefix: str = "!",
            intents: discord.Intents = discord.Intents.all()):
    class Client(commands.Bot):
        def __init__(
            self,
            dev_guild_id: int,
            developer_id: int,
            original_source_code_url: str,
            original_author_id: int,
            original_author_name: str,
            testing: bool,
            version: str,
            command_prefix: str,
            intents: discord.Intents
        ):
            super().__init__(command_prefix=command_prefix, intents=intents)
            self.Dev_Guild_ID = dev_guild_id
            self.Developer_ID = developer_id

            self.Original_Source_Code_URL = original_source_code_url
            self.Original_Author_ID = original_author_id
            self.Original_Author_Name = original_author_name
            self.Version = version

            self.testing = testing
            self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        async def setup_hook(self):
            try:
                if not self.testing:
                    synced_Global = await self.tree.sync()
                    if self.Dev_Guild_ID is not None:
                        synced_Guild = await self.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                        print(f"Synced {len(synced_Global)} global commands and {len(synced_Guild)} guild commands.")
                    else:
                        print(f"Synced {len(synced_Global)} global commands.")
                else:
                    if self.Dev_Guild_ID is None:
                        raise ValueError("In testing mode, you must provide a Dev_Guild_ID to sync commands to a specific guild.")
                    self.tree.copy_global_to(guild=discord.Object(id=self.Dev_Guild_ID))
                    synced_guild = await self.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                    print(f"Synced {len(synced_guild)} commands to the guild {self.Dev_Guild_ID.id}.")
                    self.tree.clear_commands(guild=None)
                    await self.tree.sync()
                    print("Cleared global commands.")
            except Exception as e:
                print(f"Error syncing commands: {e}")
            

        async def on_ready(self):
            print(f'Logged in as {self.user.name}')
            if self.Developer_ID is not None and self.Version is not None:
                await self.get_user(self.Developer_ID).send(f"Bot Started Sucesfully. Version: {self.Version}")
            elif self.Version is not None:
                print(f"Bot Started Sucesfully.")
            

    client = Client(command_prefix, intents , dev_guild_id, developer_id, original_source_code_url, original_author_id, original_author_name, testing, version)

    if client.testing: 
        @client.tree.command(name="restart", description="Restarts the bot" , guild=client.Dev_Guild_ID)
        async def restart(interaction: discord.Interaction):
            await interaction.response.send_message("Restarting the bot...", ephemeral=True)
            print("/restart command received.Shutting down...")
            with open("startup.txt", "w") as f:
                pass
            await interaction.client.close()

        @client.tree.command(name="shutdown", description="Shuts down the bot", guild=client.Dev_Guild_ID)
        async def shutdown(interaction: discord.Interaction):
            await interaction.response.send_message("Shutting down the bot...", ephemeral=True)
            print("/shutdown command received. Shutting down...")
            await client.close()

        @tasks.loop(seconds=1)
        async def status_task():
            if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt")):
                print("Shutdown signal received. Shutting down...")
                os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt"))
                await client.close()
            if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "restart.txt")):
                print("Restart signal received. Restarting...")
                os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "restart.txt"))
                with open("startup.txt", "w") as f:
                    pass
                await client.close()

    else:
        @tasks.loop(minutes=30)
        async def status_task():
            behind_Main = git_commands.git_differences("commit_count")

            if behind_Main != "0":
                Developer = client.get_user(client.Developer_ID)
                dm_channel = Developer.dm_channel or await Developer.create_dm()
                last_message = None
                async for msg in dm_channel.history(limit=50):
                    if msg.author == client.user:
                        last_message = msg
                        break
                embed = discord.Embed(title=f"Current Version: {client.Version}", description=f"The current version is not up to date with the latest version on [GitHub]({git_commands.git_url_origin()}).", color=discord.Color.red())
                embed.add_field(name="GitHub Version", value=f"{git_commands.get_remote_version()}", inline=False)
                embed.add_field(name="Behind Commits", value=f"The Bot is {behind_Main} commits behind.", inline=False)
                if not last_message or not last_message.embeds == embed:
                    await Developer.send(embed=embed, view=show_commitsView())

    @status_task.before_loop
    async def before_status_task():
        await client.wait_until_ready()            
    return client
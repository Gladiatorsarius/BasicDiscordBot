import discord
import os
from discord.ext import commands, tasks
from types import SimpleNamespace

from . import git_commands
import subprocess
from discord import app_commands
from pathlib import Path
import asyncio

class BasicDiscordBot(commands.Cog):
    def __init__(
        self,
        client: commands.Bot,
        dev_guild_id: int= None,
        original_source_code_url: str = None,
        testing: bool = False,
        systemctl_name: str = None,
        auto_restart: bool = False,
        auto_pull: bool = False,
        send_developer_infos: bool = True,
        developer_announcment_channel_id: int = None,
        changelog_channel_id: int = None
    ):
        self.client = client

        self.Dev_Guild_ID = dev_guild_id
        self.Developer_Announcment_Channel_ID = developer_announcment_channel_id
        self.Changelog_Channel_ID = changelog_channel_id

        self.Original_Source_Code_URL = original_source_code_url
        self.BotVersion = git_commands.get_version("Local")
        self.GitVersion = self.BotVersion
        self.Testing = testing

        self.systemctl_name = systemctl_name
        self.auto_restart = auto_restart
        self.auto_pull = auto_pull

        self.send_developer_infos = send_developer_infos
        self.git_url_origin = git_commands.git_url_origin()


    async def cog_load(self):
        await self.get_Team_members()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.Testing:
            if self.BotVersion is not None:
                await self.send_developer_anouncment(f"Bot Started Successfully. Version: {self.BotVersion}")
                print(f'Logged in as {self.client.user.name}. Version: {self.BotVersion }')
            elif self.BotVersion is None:
                await self.send_developer_anouncment(f"Bot Started Successfully.")
                print(f'Logged in as {self.client.user.name}')
            if not self.update_git.is_running():
                self.update_git.start()
        else:
            if not self.restart_helper.is_running():
                self.restart_helper.start()
            print(f'Logged in as {self.client.user.name} in testing mode.')

    async def sync_commands(self):
        try:
            dev_guild = await self.client.fetch_guild(self.Dev_Guild_ID) if self.Dev_Guild_ID is not None else None
            if not self.Testing:
                synced_Global = await self.client.tree.sync()
                if self.Dev_Guild_ID is not None:
                    synced_Guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                    return f"Synced {len(synced_Global)} global commands and {len(synced_Guild)} to {dev_guild.name}."
                else:
                    return f"Synced {len(synced_Global)} global commands."
            else:
                if self.Dev_Guild_ID is None:
                    raise ValueError("In testing mode, you must provide a Dev_Guild_ID to sync commands to a specific guild.")
                self.client.tree.copy_global_to(guild=discord.Object(id=self.Dev_Guild_ID))
                synced_guild = await self.client.tree.sync(guild=discord.Object(id=self.Dev_Guild_ID))
                self.client.tree.clear_commands(guild=None)
                await self.client.tree.sync()
                return f"Synced {len(synced_guild)} commands to {dev_guild.name}.\nCleared global commands."
        except Exception as e:
            return f"Error syncing commands: {e}"

    
    @commands.command(name="SyncCommands", description="Syncs the bot's commands with Discord.")
    async def sync_commands_command(self, ctx: commands.Context):
        if not self.check_team_member(ctx.author.id):
            await ctx.send("You do not have permission to use this command.")
            return
        commands = await self.sync_commands()
        await ctx.send(commands)

    def check_team_member(self, user_id: int) -> bool:
        return user_id in self.team_member_ids

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

    async def send_developer_anouncment(self, message: str, embed: discord.Embed = None):
        if self.Developer_Announcment_Channel_ID is not None:
            channel = self.client.get_channel(self.Developer_Announcment_Channel_ID)
            if channel:
                try:
                    if embed:
                        await channel.send(message, embed=embed)
                    else:
                        await channel.send(message)
                except Exception as e:
                    print(f"Failed to send message to announcement channel: {e}")
        else:
            for member_id in self.team_member_ids:
                member = await self.client.fetch_user(member_id)
                if member:
                    try:
                        if embed:
                            await member.send(message, embed=embed)
                        else:
                            await member.send(message)
                    except Exception as e:
                        print(f"Failed to send DM to {member.name}: {e}")

    async def send_change_log(self, changelog_text: str = None):
        if self.Changelog_Channel_ID is not None:
            channel = self.client.get_channel(self.Changelog_Channel_ID)
            if channel:
                if changelog_text:
                    changelog = git_commands.parse_changelog_diff(changelog_text)
                else:
                    changelog = git_commands.view_changelogmd()
                print(f"Changelog: {changelog}")
                embed = discord.Embed(title=f"Changelog for Version {changelog['version']}", description=f"Release Date: {changelog['date']}", color=discord.Color.blue())
                for change in changelog["changes"]:
                    change_type = change["type"]
                    change_content = "\n".join(change["content"])
                    embed.add_field(name=change_type, value=change_content, inline=False)
                await channel.send(embed=embed)
                
                
    
    @tasks.loop(seconds=1)
    async def restart_helper(self):
        if self.Testing:
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
        if not self.Testing:
            self.restart_helper.stop()
        await self.client.wait_until_ready()

    async def _delayed_restart(self, delay: int = 10):
        await asyncio.sleep(delay)

        await asyncio.create_subprocess_exec("systemctl", "restart", self.systemctl_name)

    async def restart_systemctl_task(self):
        asyncio.create_task(self._delayed_restart(delay=10))

    @tasks.loop(minutes=30)
    async def update_git(self):
        newest_tag = git_commands.get_remote_version()
        if newest_tag is not None:
            if self.GitVersion != newest_tag:
                if self.auto_pull:
                    await self.send_change_log()
                    git_commands.git_pull()
                    GitVersion = git_commands.get_version("Local")
                    if GitVersion == newest_tag:
                        if self.systemctl_name:
                            if self.auto_restart:
                                await self.restart_systemctl_task()
                                await self.send_developer_anouncment(f"Bot pulled the latest version {newest_tag} and is restarting.")
                            else:
                                await self.send_developer_anouncment(f"Bot pulled the latest version {newest_tag}. Please restart the bot manually.")
                        else:
                            await self.send_developer_anouncment(f"Bot pulled the latest version {newest_tag}. Please restart the bot manually.")

    @update_git.before_loop
    async def before_update_git(self):
        if self.Testing:
            self.update_git.stop()
        await self.client.wait_until_ready()

    @app_commands.command(name="info", description="Get information about the current version of the bot.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Information", color=discord.Color.blue())
        if self.BotVersion is not None:
            embed.add_field(name="Bot Version", value=self.BotVersion, inline=False)
        if self.git_url_origin is not None:
            embed.add_field(name="Source Code", value=f"[Link]({self.git_url_origin})", inline=False)
        if self.send_developer_infos and self.team_member_ids:
            team_member_mentions = [f"<@{member_id}>" for member_id in self.team_member_ids]
            embed.add_field(name="Developers", value=", ".join(team_member_mentions), inline=False)
        if self.Original_Source_Code_URL is not None:
            if self.Original_Source_Code_URL != self.git_url_origin:
                embed.add_field(name="Original Source Code", value=f"This Bot was Modified you can find the Original Source Code [here]({self.Original_Source_Code_URL})", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="allservers", description="(Owner Only)Get a list of all servers the bot is in.")
    async def allservers(self, interaction: discord.Interaction):
        if not self.check_team_member(interaction.user.id):
            await interaction.response.send_message("This command is only available to the bot owner.", ephemeral=True)
            return

        if self.client.intents.guilds is None:
            await interaction.response.send_message("Pls enable the guilds intent in Discords [Developer Portal](https://discord.com/developers/applications).", ephemeral=True)
            return

        guilds = self.client.guilds
        embed = discord.Embed(title=f"The Bot is in {len(guilds)} servers :", color=discord.Color.blue())
        i = 1
        for guild in guilds:
            embed.add_field(name=f"Server {i}", value=f"Name: {guild.name}, ID: {guild.id}", inline=False)
            i += 1

        await interaction.response.send_message(embed=embed, ephemeral=True)
            
        




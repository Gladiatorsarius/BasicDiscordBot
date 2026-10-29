from src.basicdiscordbot.BasicDiscordBot import BasicDiscordBot
import os
import dotenv
import logging
import discord
from discord.ext import commands 

dotenv.load_dotenv()

testing = os.getenv("testing").lower() == 'true'

Dev_Guild_ID =int(os.getenv("Dev_Guild_ID"))
Original_Source_Code_URL = "https://github.com/Gladiatorsarius/BasicDiscordBot" #Please do not change this URL. It is used to provide credit to the original author of the bot.
Systemctl_Name = os.getenv("systemctl_name")
Auto_Restart = True
Auto_Pull = True
send_developer_infos = True
Announcment_Channel_ID = int(os.getenv("Announcment_Channel_ID"))
Changelog_Channel_ID = int(os.getenv("Changelog_Channel_ID"))


token = os.getenv("Discord_Bot_Token")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
client = commands.Bot(intents=intents, command_prefix="!")

@client.event
async def setup_hook():
    await client.add_cog(BasicDiscordBot(
        client,
        dev_guild_id=Dev_Guild_ID,
        original_source_code_url=Original_Source_Code_URL,
        testing=testing,
        systemctl_name=Systemctl_Name,
        auto_restart=Auto_Restart,
        auto_pull=Auto_Pull,
        send_developer_infos= send_developer_infos,
        developer_announcment_channel_id=Announcment_Channel_ID,
        changelog_channel_id=Changelog_Channel_ID,
    ))


client.run(token, log_handler=handler, log_level=logging.DEBUG)


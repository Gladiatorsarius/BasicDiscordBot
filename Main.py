from src.basicdiscordbot.BasicDiscordBot import BasicDiscordBot
import os
import dotenv
import logging
import discord
from discord.ext import commands 

dotenv.load_dotenv()

testing = os.getenv("testing").lower() == 'true'

Dev_Guild_ID =int(os.getenv("Dev_Guild_ID"))
Announcment_Channel_ID = int(os.getenv("Announcment_Channel_ID"))
Changelog_Channel_ID = int(os.getenv("Changelog_Channel_ID"))

Original_Source_Code_URL = "https://github.com/Gladiatorsarius/BasicDiscordBo" #Please do not change this URL. It is used to provide credit to the original author of the bot.


token = os.getenv("Discord_Bot_Token")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix="!")

@client.event
async def setup_hook():
    await client.add_cog(BasicDiscordBot(client,  dev_guild_id=Dev_Guild_ID , testing=testing, original_source_code_url=Original_Source_Code_URL, send_developer_infos=True, developer_announcment_channel_id=Announcment_Channel_ID, changelog_channel_id=Changelog_Channel_ID))
    BasicDiscordBot_instance = client.get_cog("BasicDiscordBot")


client.run(token, log_handler=handler, log_level=logging.DEBUG)


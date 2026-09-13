from src.basicdiscordbot.BasicDiscordBot import BasicDiscordBot
import os
import dotenv
import logging
import discord
from discord.ext import commands 

dotenv.load_dotenv()

Testing = os.getenv("Testing")

Dev_Guild_ID =int(os.getenv("Dev_Guild_ID"))
Developer_ID = int(os.getenv("Developer_ID"))
Original_Source_Code_URL = "https://example.com" #Please do not change this URL. It is used to provide credit to the original author of the bot.
Original_Author_ID = 1130514544960225402 #Please do not change this id. It is used to provide credit to the original author of the bot.
Original_Author_Name = "Gladiatorsarius" #Please do not change this name. It is used to provide credit to the original author of the bot.

token = os.getenv("Discord_Bot_Token")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
client = commands.Bot(intents=intents, command_prefix="!")

@client.event
async def setup_hook():
    await client.add_cog(BasicDiscordBot(client, developer_id=Developer_ID , dev_guild_id=Dev_Guild_ID))

client.run(token, log_handler=handler, log_level=logging.DEBUG)


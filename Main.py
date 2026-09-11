from src.basicdiscordbot.BasicDiscordBot import BasicDiscordBot
import os
import dotenv
import logging

dotenv.load_dotenv()

Testing = os.getenv("Testing")

Dev_Guild_ID =os.getenv("Dev_Guild_ID")
Developer_ID = os.getenv("Developer_ID")
Original_Source_Code_URL = "https://example.com" #Please do not change this URL. It is used to provide credit to the original author of the bot.
Original_Author_ID = 1130514544960225402 #Please do not change this id. It is used to provide credit to the original author of the bot.
Original_Author_Name = "Gladiatorsarius" #Please do not change this name. It is used to provide credit to the original author of the bot.


client = BasicDiscordBot(
    testing=Testing,
    dev_guild_id=Dev_Guild_ID,
    developer_id=Developer_ID,
    original_source_code_url=Original_Source_Code_URL,
    original_author_id=Original_Author_ID,
    original_author_name=Original_Author_Name,
    version="1.0.0",
    command_prefix="!",
)

client.run(os.getenv("Discord_Bot_Token"), log_handler=client.handler, log_level=logging.DEBUG)


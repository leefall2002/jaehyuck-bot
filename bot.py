import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import random
startup_extensions = ["Music"]
bot = commands.Bot("재혁아 ")
client = discord.Client()


@bot.event
async def on_ready():
    print("정상작동 중")

class Main_Commands():
    def __init__(self,bot):
        self.bot = bot
     

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))


bot.run('NDE3NTk3Mjk0NjU4MTkxMzYw.DXmHRg.07xA0_GwsHFX4B7iHTKsn-qfRbA')

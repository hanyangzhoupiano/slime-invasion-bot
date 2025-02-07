import discord
from discord.ext import commands

@bot.event
async def on_ready():
  print("ready!")
  channel = bot.get_channel(1321480987238203454)
  await channel.send("Hello, testing testing testing this new bot I coded which will be the leveling bot")

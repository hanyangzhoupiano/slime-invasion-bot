import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print("ready!")
  channel = bot.get_channel(1321480987238203454)
  await channel.send("Hello, testing testing testing this new bot I coded which will be the leveling bot")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! I am a super cool bot!")

bot.run("MTI5NjYwMTU0MDM4NzE0Nzg2OQ.GpBnjT.x7weeYWyRHXfCG6RGXsYsbGoZBNZq_WDRHAPWc")

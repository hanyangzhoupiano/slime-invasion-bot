import discord
import json
from discord.ext import commands

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print("ready!")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I am a bot programmed by Hanyang Zhou.")

bot.run("MTI5NjYwMTU0MDM4NzE0Nzg2OQ.GpBnjT.x7weeYWyRHXfCG6RGXsYsbGoZBNZq_WDRHAPWc")

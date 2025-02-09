import os
import discord
import json
import random
from discord.ext import commands
from threading import Thread

import data_functions

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

data = data_functions.load_data()

@bot.event
async def on_ready():
    print("ready!")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    id = msg.author.id
    if data["User_" + str(id)]["messages"]:
        data["User_" + str(id)]["messages"] += 1
        data_functions.save_data(data)
    else:
        data["User_" + str(id)]["messages"] = 1
        data_functions.save_data(data)

@bot.command()
async def view_messages(ctx):
    messages = data[ctx.author.id]
    if messages:
        await ctx.send("You currently have " + str(messages) + " messages.")

bot.run("MTI5NjYwMTU0MDM4NzE0Nzg2OQ.GpBnjT.x7weeYWyRHXfCG6RGXsYsbGoZBNZq_WDRHAPWc")

from flask import Flask

# Create a simple web server
app = Flask(__name__)
@app.route('/')

def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
Thread(target=run_web).start()

import os
import discord
import json
import random
from discord.ext import commands
from threading import Thread

from data_functions import setup_database, set_messages, get_messages

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

setup_database()

@bot.event
async def on_ready():
    print("ready!")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    user_id = msg.author.id
    set_messages(user_id, get_messages(user_id) + 1)
    await bot.process_commands(msg)

@bot.command()
async def view_messages(ctx):
    messages = get_messages(ctx.author.id)
    await ctx.send("You currently have " + str(messages) + " messages.")

bot.run("DISCORD_TOKEN")

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

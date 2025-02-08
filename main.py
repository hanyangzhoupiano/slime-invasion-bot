import os
import discord
import json
from discord.ext import commands
from flask import Flask
from threading import Thread

# Create a simple web server
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
Thread(target=run_web).start()

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    try:
        with open("data.json", "w") as file:
            json.load(file)
    except FileNotFoundError:
        return {}

@bot.event
async def on_ready():
    print("ready!")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    message = msg.content
    if "ok" in message.lower() or "okay" in message.lower():
        await msg.channel.send(f"Okay, too!")
    if "hi" in message.lower() or "hello" in message.lower():
        await msg.channel.send(f"Hello! I am a bot and would like to engage in this conversation.")
    if "yay" in message.lower():
        await msg.channel.send(f"Yay to you! What are you so happy about?")
    if "oh no" in message.lower():
        await msg.channel.send(f"Oh no! What has gone wrong?")
    if "work" in message.lower():
        await msg.channel.send(f"Wow, you really like working, " + msg.author.name + "!")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I am a bot programmed by Hanyang Zhou.")

bot.run("MTI5NjYwMTU0MDM4NzE0Nzg2OQ.GpBnjT.x7weeYWyRHXfCG6RGXsYsbGoZBNZq_WDRHAPWc")

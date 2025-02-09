import os
import discord
import json
import random
import asyncio
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
async def viewmessages(ctx, name: str = None):
    if not ctx.author.bot:
        if name is None:
            user = ctx.author
        else:
            matching_names = []
            for member in ctx.guild.members:
                if name.lower() in member.name.lower():
                    matching_names.append(member.name)
            if matching_names:
                msg = ""
                for i, n in enumerate(matching_names):
                    msg += str(i + 1) + ". " + n
                    if i != len(matching_names) - 1:
                        msg += ",\n"
                try:
                    await ctx.send(embed=discord.Embed(
                        color=int("87C8F5", 16),
                        description=f"Mutiple users found. Please select a user below, or type cancel:\n{msg}",
                    ).set_author(name=ctx.author.name, icon_url=ctx,author.avatar.url))

                    selection = None
                    response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=10.0)

                    if "cancel" in response.content.lower():
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="The command has been canceled.",
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                        return
                    try:
                        selection = int(response.content)
                    except ValueError:
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="Invalid selection.",
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                        return
                    else:
                        if selection is not None:
                            if (selection - 1) >= 0 and selection <= len(matching_names):
                                matching_name = matching_names[selection]
                                for member in ctx.guild.members:
                                    if member.name.lower() == matching_name.lower():
                                        user = member
                                        break
                            else:
                                await ctx.send(embed=discord.Embed(
                                    color=int("FA3939", 16),
                                    description="Invalid selection.",
                                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                                return
                except asyncio.TimeoutError:
                    await ctx.send(embed=discord.Embed(
                        color=int("FA3939", 16),
                        description="The command has been canceled because you took too long to reply.",
                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                    return
        msg = await ctx.send(embed=discord.Embed(
            color=int("87C8F5", 16),
            description="Retrieving data...",
        ).set_author(name=user.name, icon_url=user.avatar.url))

        messages = get_messages(user.id)

        await msg.edit(embed=discord.Embed(
            color=int("96F587", 16),
            description=f"**Messages:** {messages}",
        ).set_author(name=user.name, icon_url=user.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

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

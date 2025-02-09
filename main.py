import os
import discord
import json
import random
import asyncio
from discord.ext import commands
from threading import Thread

from data_functions import setup_database, set_messages, get_messages, set_prefix, get_prefix

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

intents = discord.Intents.all()
intents.messages = True

default_prefixes = {"!"}
prefixes = {}

async def prefix(bot, message):
    guild_id = message.guild.id
    return get_prefix(guild_id)

bot = commands.Bot(command_prefix=prefix, intents=intents)

setup_database()

@bot.event
async def on_ready():
    if not bot.get_guild(1292978415552434196):
        await bot.close()
    else:
        print(f"Bot is ready and connected to guild: {bot.guilds[0].name}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    user_id = msg.author.id
    set_messages(user_id, get_messages(user_id) + 1)
    await bot.process_commands(msg)

@bot.command()
async def help(ctx):
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description="**Information:**\nThe symbols *<>* around an argument indicate that the argument is required, while the symbols *[]* indicate that it is optional.\n**List of Commands:**\nsetprefix <new_prefix>\nviewmessages [user]",
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command()
async def viewprefix(ctx):
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"The current prefix is {get_prefix(ctx.guild.id)}.",
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command()
async def setprefix(ctx, new_prefix: str = None):
    if ctx.author.guild_permissions.manage_guild and new_prefix is not None:
        if len(new_prefix) > 4:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description="The prefix chosen is too long. Please try again with a shorter prefix.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        set_prefix(ctx.guild.id, new_prefix)
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"The prefix has been changed to {new_prefix}.",
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command()
async def viewmessages(ctx, name: str = None):
    if not ctx.author.bot:
        user = None
        if name is None:
            user = ctx.author
        else:
            matching_names = []
            for member in ctx.guild.members:
                if name.lower() in member.name.lower():
                    matching_names.append(member.name)
            if matching_names:
                if len(matching_names) > 1:
                    msg = ""
                    for i, n in enumerate(matching_names):
                        msg += str(i + 1) + ". " + n
                        if i != len(matching_names) - 1:
                            msg += ",\n"
                    try:
                        await ctx.send(embed=discord.Embed(
                            color=int("50B4E6", 16),
                            description=f"Mutiple users found. Please select a user below, or type cancel:\n{msg}",
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    
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
                                if (selection - 1) >= 0 and (selection - 1) <= (len(matching_names) - 1):
                                    matching_name = matching_names[selection - 1]
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
                else:
                    for member in ctx.guild.members:
                        if member.name.lower() == matching_names[0].lower():
                            user = member
                            break
        if user is not None:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description="**Retrieving data...**",
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = get_messages(user.id)
    
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"**Messages:** {messages}\n**Server Join Date:** {user.joined_at}\n**Role:** {user.top_role}",
            ).set_author(name=user.name, icon_url=user.avatar.url))

@bot.command()
async def echo(ctx, message: str = None):
    if message is not None:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=message,
        ).set_author(name=user.name, icon_url=user.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

import os
import discord
import json
import random
import asyncio
import math
import time
from discord.ext import commands
from threading import Thread

import data_functions
import helper_functions

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
user_last_experience_time = {}

bot = commands.Bot(command_prefix=lambda bot, message: data_functions.get_prefix(message.guild.id), intents=intents)

data_functions.setup_database()

@bot.event
async def on_ready():
    if not bot.get_guild(1292978415552434196):
        await bot.close()
    else:
        print(f"Bot is ready and connected to guild: {bot.guilds[0].name}")

@bot.event
async def on_disconnect():
    print("Bot disconnected! Attempting to reconnect in 5 seconds...")
    await asyncio.sleep(5)

@bot.event
async def on_resumed():
    print("Bot reconnected!")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    user_id = msg.author.id
    current_time = time.time()
    if msg.author.bot:
        return
    
    if user_id in user_last_experience_time:
        time_diff = current_time - user_last_experience_time[user_id]
        if time_diff < 10:
            return
    
    user_last_experience_time[user_id] = current_time
    data_functions.set_messages(user_id, data_functions.get_messages(user_id) + 1)
    data_functions.set_experience(user_id, data_functions.get_experience(user_id) + math.floor(random.random() * 10 + 5))
    level = data_functions.get_levels(user_id)
    experience = data_functions.get_experience(user_id)
    if ((25 * (level**2) - (25 * level))/level + 50) - experience <= 0:
        data_functions.set_levels(user_id, data_functions.get_levels(user_id) + 1)
        data_functions.set_experience(user_id, 0)
        await msg.channel.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"Congratulations! The user *'{msg.author.name}'* has leveled up to **Level {data_functions.get_levels(user_id)}**!",
        ).set_author(name=msg.author.name, icon_url=msg.author.avatar.url))

    if math.floor(random.random() * 100 + 1) < 5:
        amount = random.randint(50, 200)
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            title="Experience Drop",
            description=f"An experience drop of {amount} has started! Type 'claim' to claim it before the time runs out!",
        ))
        try:
            response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel, timeout=10.0)
            if response.content.lower() == "claim":
                if not response.author.bot:
                    await ctx.send(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        title="Experience Drop",
                        description=f"*{response.author.name}* was the first to claim the experience drop of {amount}!",
                    ))
                    data_functions.set_experience(response.author.id, data_functions.get_experience(ctx.author.id) + amount)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="Nobody claimed the experience drop in time.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
    await bot.process_commands(msg)

bot.remove_command("help")
@bot.command(help="Shows this help message.", aliases=["commands", "cmds"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def help(ctx, command_name: str = None):
    if command_name:
        command = bot.get_command(command_name)
        if command:
            await ctx.send(f"**{command.name}** - {command.help}\n**Aliases:** {', '.join(command.aliases) if command.aliases else 'None'}")
        else:
            await ctx.send("Command not found!")
    else:
        help_text = "- " + "\n- ".join([f"**{cmd.name}** - {cmd.help}\n**Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'None'}" for cmd in bot.commands])
        await ctx.send(f"Here are the available commands:\n{help_text}")

@bot.command(aliases=["vp", "viewp"], help="Shows the current prefix of this bot.")
@commands.cooldown(2, 10, commands.BucketType.user)
async def view_prefix(ctx):
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"The current prefix is '{data_functions.get_prefix(ctx.guild.id)}'.",
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["sp", "newp"], help="Changes the prefix of this bot.")
@commands.cooldown(2, 10, commands.BucketType.user)
async def set_prefix(ctx, new_prefix: str = None):
    if ctx.author.guild_permissions.manage_guild and new_prefix is not None:
        if len(new_prefix) > 32:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description="The prefix chosen is too long. Please try again with a shorter prefix.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        data_functions.set_prefix(ctx.guild.id, new_prefix)
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"The prefix has been changed to '{new_prefix}'.",
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        
@bot.command(aliases=["vs", "msgs", "lvls", "stats"], help="Shows the statistics of a user, such as levels, experience, and messages.")
@commands.cooldown(2, 10, commands.BucketType.user)
async def view_stats(ctx, name: str = None):
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
                            msg += "\n"
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
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"**Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}",
            ).set_author(name=user.name, icon_url=user.avatar.url))

@bot.command(aliases=["expdrop", "expd", "ed"], help="Create an experience drop in a channel.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def experience_drop(ctx):
    amount = random.randint(50, 200)
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        title="Experience Drop",
        description=f"An experience drop of {amount} has started! Type 'claim' to claim it before the time runs out!",
    ))
    try:
        response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel, timeout=10.0)
        if response.content.lower() == "claim":
            if not response.author.bot:
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    title="Experience Drop",
                    description=f"*{response.author.name}* was the first to claim the experience drop of {amount}!",
                ))
                data_functions.set_experience(response.author.id, data_functions.get_experience(ctx.author.id) + amount)
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="Nobody claimed the experience drop in time.",
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    
@bot.command(aliases=["s", "sy"], help="Make the bot say a specified message.")
@commands.cooldown(2, 10, commands.BucketType.user)
async def say(ctx, *, message: str = None):
    if message is not None:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=message,
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["addl", "al"], help="Adds levels to the specificed user.")
@commands.cooldown(2, 10, commands.BucketType.user)
async def add_levels(ctx, amount: int = None):
    if amount is not None and ctx.author.guild_permissions.manage_guild:
        if str(amount).isnumeric():
            if amount <= 10:
                data_functions.set_levels(ctx.author.id, int(amount))
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"Successfully {amount} levels to {ctx.author.name}.",
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="You can only add a maximum of 10 levels at a time.",
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="Invalid amount.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["addm", "am"], help="Adds messages to the specified user.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def add_messages(ctx, amount: int = None):
    if amount is not None and ctx.author.guild_permissions.manage_guild:
        if str(amount).isnumeric():
            if amount <= 10:
                data_functions.set_messages(ctx.author.id, int(amount))
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"Successfully {amount} messages to {ctx.author.name}.",
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="You can only add a maximum of 10 messages at a time.",
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="Invalid amount.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

import os
import sys
import discord
import json
import random
import asyncio
import math
import time
from discord.ext import commands
from threading import Thread

import data_functions
import resources

from flask import Flask

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
error_logs = []
never_have_i_ever_questions = resources.get_never_have_i_evers()
brain_teasers = resources.get_brain_teasers()
brain_teaser_answers = resources.get_brain_teaser_answers()
trivia_categories = resources.get_trivia_categories()

bot = commands.Bot(command_prefix=lambda bot, message: data_functions.get_prefix(message.guild.id), intents=intents)

data_functions.setup_database()

sync_text = f"Commands synced: None"

@bot.event
async def on_ready():
    bot.tree.clear_commands(guild=bot.guilds[0])
    synced = await bot.tree.sync(guild=bot.guilds[0])
    sync_text = f"Commands synced: {len(synced)}"
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

    if math.floor(random.random() * 100 + 1) <= 5:
        random_integer = random.randint(1, 100)
        type = "Common" if random_integer < 60 else "Rare" if random_integer < 80 else "Epic" if random_integer < 90 else "Legendary" if random_integer < 95 else "Mythical" if random_integer < 98 else "Celestial" 
        amount = random.randint(60, 150) if random_integer < 60 else random.randint(120, 250) if random_integer < 80 else random.randint(240, 380) if random_integer < 90 else random.randint(350, 520) if random_integer < 95 else random.randint(510, 800) if random_integer < 98 else random.randint(750, 1200) 
        await msg.channel.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            title="Experience Drop",
            description=f"🧪 A **{type}** Experience Drop of {amount} has started! Type 'claim' to claim it before the time runs out!"
        ))
        try:
            response = await bot.wait_for('message', check=lambda msg2: msg2.channel == msg.channel and msg2.content.lower() == "claim", timeout=10.0)
            if not response.author.bot:
                await msg.channel.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    title="Experience Drop",
                    description=f"✅ *{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
                ))
                data_functions.set_experience(response.author.id, data_functions.get_experience(response.author.id) + amount)
        except asyncio.TimeoutError:
            await msg.channel.send(embed=discord.Embed(
                color=int("FA3939", 16),
                title="Experience Drop",
                description="⏳ Nobody claimed the experience drop in time."
            ))
    
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
            description=f"⬆️ Congratulations! The user *'{msg.author.name}'* has leveled up to **Level {data_functions.get_levels(user_id)}**!"
        ).set_author(name=msg.author.name, icon_url=msg.author.avatar.url))
    await bot.process_commands(msg)

@bot.event
async def on_command_error(ctx, error):
    error_logs.append(error)
    if len(error_logs) > 20:
        if error_logs and 0 in error_logs:
            del error_logs[0]

bot.remove_command("help")
@bot.command(help="Shows this help message.", aliases=["commands", "cmds"])
async def help(ctx, command_name: str = None):
    if command_name is not None:
        command = bot.get_command(command_name)
        if command:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ **{command.name}** - {command.help}\n**Aliases:** {', '.join(command.aliases) if command.aliases else 'None'}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        help_text = "- " + "\n- ".join([f"**{cmd.name}** - {cmd.help}\n**Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'None'}" for cmd in bot.commands])
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"✅ {help_text}"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["vp", "viewp"], help="Shows the current prefix of this bot.")
async def view_prefix(ctx):
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"✅ The current prefix is '{data_functions.get_prefix(ctx.guild.id)}'."
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.tree.command(name="viewprefix", description="Shows the current prefix of this bot.")
async def slash_view_prefix(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        embed = discord.Embed(
            color=int("50B4E6", 16),
            description=f"✅ The current prefix is '{data_functions.get_prefix(interaction.guild.id)}'."
        ).set_author(name=interaction.member.name, icon_url=interaction.member.avatar.url)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        error_logs.append(e)
        if len(error_logs) > 20:
            if error_logs and 0 in error_logs:
                del error_logs[0]

@bot.command(aliases=["sp", "setp"], help="Changes the prefix of this bot.")
async def set_prefix(ctx, new_prefix: str = None):
    if ctx.author.guild_permissions.manage_guild:
        if new_prefix is not None:
            if len(new_prefix) > 32:
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description="❌ The prefix chosen is too long. Please try again with a shorter prefix."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
            data_functions.set_prefix(ctx.guild.id, new_prefix)
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ The prefix has successfully been changed to '{new_prefix}'."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.tree.command(name="setprefix", description="Sets the current prefix of this bot.")
async def slash_set_prefix(interaction: discord.Interaction, new_prefix: str = None):
    if interaction.member.guild_permissions.manage_guild:
        if new_prefix is not None:
            try:
                await interaction.response.defer()
                if len(new_prefix) > 32:
                    await interaction.followup.send(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description="❌ The prefix chosen is too long. Please try again with a shorter prefix."
                    ).set_author(name=interaction.member.name, icon_url=interaction.member.avatar.url))
                    return
                data_functions.set_prefix(ctx.guild.id, new_prefix)
                await interaction.followup.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"✅ The prefix has successfully been changed to '{new_prefix}'."
                ).set_author(name=interaction.member.name, icon_url=interaction.member.avatar.url))
            except Exception as e:
                error_logs.append(e)
                if len(error_logs) > 20:
                    if error_logs and 0 in error_logs:
                        del error_logs[0]
    else:
        await interaction.response.defer()
        await interaction.followup.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=interaction.member.name, icon_url=interaction.member.avatar.url))

@bot.command(aliases=["vs", "msgs", "lvls", "stats"], help="Shows the statistics of a user.")
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
                            description=f"✅ Mutiple users found. Please select a user below, or type cancel:\n{msg}"
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    
                        selection = None
                        response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=15.0)
    
                        if "cancel" in response.content.lower():
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="❌ The command has been canceled."
                            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                            return
                        try:
                            selection = int(response.content)
                        except ValueError:
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="❌ Invalid selection."
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
                                        description="❌ Invalid selection."
                                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                                    return
                    except asyncio.TimeoutError:
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="⏳ The command has been canceled because you took too long to reply."
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
                description=f"✅ **Retrieving data for {user.name}...**"
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"✅ **Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}"
            ).set_author(name=user.name, icon_url=user.avatar.url))

@bot.tree.command(name="viewstats", description="Shows the statistics of a user.")
async def slash_view_stats(interaction: discord.Interaction, member: discord.Member = None):
    if not ctx.author.bot:
        await interaction.response.defer()
        user = None
        if member is None:
            user = interaction.member
        else:
            user = member
        if user is not None:
            await interaction.followup.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ **Retrieving data for '{user.name}'...**"
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await interaction.followup.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"✅ **Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}"
            ).set_author(name=user.name, icon_url=user.avatar.url))

@bot.command(aliases=["expdrop", "expd", "ed"], help="Create an experience drop in a channel.")
async def experience_drop(ctx):
    if ctx.author.guild_permissions.manage_guild:
        random_integer = random.randint(1, 100)
        type = "Common" if random_integer < 60 else "Rare" if random_integer < 80 else "Epic" if random_integer < 90 else "Legendary" if random_integer < 95 else "Mythical" if random_integer < 98 else "Celestial" 
        amount = random.randint(60, 150) if random_integer < 60 else random.randint(120, 250) if random_integer < 80 else random.randint(240, 380) if random_integer < 90 else random.randint(350, 520) if random_integer < 95 else random.randint(510, 800) if random_integer < 98 else random.randint(750, 1200) 
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            title="Experience Drop",
            description=f"🧪 A **{type}** Experience Drop of {amount} has started! Type 'claim' to claim it before the time runs out!"
        ))
        try:
            response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.content.lower() == "claim", timeout=15.0)
            if not response.author.bot:
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    title="Experience Drop",
                    description=f"✅ *{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
                ))
                data_functions.set_experience(response.author.id, data_functions.get_experience(response.author.id) + amount)
        except asyncio.TimeoutError:
            await msg.channel.send(embed=discord.Embed(
                color=int("FA3939", 16),
                title="Experience Drop",
                description="⏳ Nobody claimed the experience drop in time."
            ))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["f"], help="Fight against a creature for rewards.")
async def fight(ctx):
    if not ctx.author.bot:
        difficulty = random.randint(1, 10)
        creature_type = random.choice(["Zombie", "Goblin", "Elf", "Angel", "Demon", "Warrior", "Knight", "Slime"])
        
        sizes = {
            "Big": random.randint(2, 4),
            "Large": random.randint(5, 7),
            "Huge": random.randint(8, 12),
            "Giant": random.randint(13, 16),
            "Colossal": random.randint(17, 22)
        }
        mutations = {
            "Possessed": random.randint(4, 9),
            "Phantom": random.randint(11, 17),
            "Ancient": random.randint(9, 16),
            "Ethereal": random.randint(14, 22),
            "Heavenly": random.randint(18, 30),
            "Galactic": random.randint(15, 26),
            "Divine": random.randint(25, 38),
            "Superior": random.randint(29, 43),
            "Exotic": random.randint(32, 50)
        }

        random_integer = random.randint(1, 100)
        creature_level = (
            random.randint(1, 5) if random_integer < 60 else
            random.randint(3, 10) if random_integer < 80 else
            random.randint(8, 18) if random_integer < 90 else
            random.randint(17, 36) if random_integer < 95 else
            random.randint(32, 65) if random_integer < 98 else
            random.randint(60, 120)
        )
        creature_level += difficulty
        
        user_level = data_functions.get_levels(ctx.author.id)
        level_difference = creature_level - user_level
        win_chance = 60
        
        if level_difference > 0:
            win_chance = math.floor(win_chance - (5 * math.log1p(level_difference)) - 5)
        else:
            win_chance = math.floor(win_chance + (5 * math.log1p(abs(level_difference))) + 5)
        
        mutation_multiplier = 1
        size_multiplier = 1
        
        mutation = random.choice(list(mutations.keys())) if random.randint(1, 5) == 1 else ""
        if mutation:
            mutation_multiplier = mutations[mutation]
            mutation_multiplier = math.ceil(mutation_multiplier / 1.5)
            win_chance -= 5 * abs(math.ceil(mutation_multiplier - 5))
            creature_level = math.ceil(creature_level * 1.5)
        
        size = random.choice(list(sizes.keys())) if random.randint(1, 5) == 1 else ""
        if size:
            size_multiplier = sizes[size]
            size_multiplier = math.ceil(size_multiplier / 1.5)
            win_chance -= 5 * abs(math.ceil(size_multiplier - 5))
            creature_level = math.ceil(creature_level * 1.5)
        
        reward = (random.randint(20, 50) * difficulty) + (random.randint(20, 50) * creature_level)
        risk = math.ceil(random.randint(20, 50) * difficulty) + creature_level * 2
        
        win_chance = max(5, min(95, win_chance))
        
        encounter_message = (
            f"⚔️ You encountered a**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type} (Level {creature_level})** in the wild."
            f"\n1. Fight\n2. Escape\n\n"
            f"*Your Level: {user_level}\nWin Chance: {win_chance}%\nDifficulty: {difficulty}/10\nRisk: {risk}*"
        )
        
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=encounter_message
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        
        try:
            response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=15.0)
            
            if "1" in response.content.lower() or "fight" in response.content.lower():
                if random.randint(1, 100) <= win_chance:
                    await ctx.send(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"✅ You defeated the**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}** and gained {reward} experience!"
                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                    data_functions.set_experience(ctx.author.id, data_functions.get_experience(ctx.author.id) + reward)
                else:
                    await ctx.send(embed=discord.Embed(
                        color=int("FA3939", 16),
                        description=f"❌ You were defeated by the**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}** and lost {risk} experience."
                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                    data_functions.set_experience(ctx.author.id, max((data_functions.get_experience(ctx.author.id) - risk), 0))
            elif "2" in response.content.lower() or "escape" in response.content.lower():
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"✅ You escaped from the**{' ' + size if size else ''} {' ' + mutation if mutation else ''} {creature_type}**."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="❌ Invalid selection."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="⏳ The command has been canceled because you took too long to reply."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

async def fight(interaction: discord.Interaction):
    if not interaction.user.bot:
        await interaction.response.defer()
    
        difficulty = random.randint(1, 10)
        creature_type = random.choice(["Zombie", "Goblin", "Elf", "Angel", "Demon", "Warrior", "Knight", "Slime"])
        
        sizes = {
            "Big": random.randint(2, 4),
            "Large": random.randint(5, 7),
            "Huge": random.randint(8, 12),
            "Giant": random.randint(13, 16),
            "Colossal": random.randint(17, 22)
        }
        mutations = {
            "Possessed": random.randint(4, 9),
            "Phantom": random.randint(11, 17),
            "Ancient": random.randint(9, 16),
            "Ethereal": random.randint(14, 22),
            "Heavenly": random.randint(18, 30),
            "Galactic": random.randint(15, 26),
            "Divine": random.randint(25, 38),
            "Superior": random.randint(29, 43),
            "Exotic": random.randint(32, 50)
        }
    
        random_integer = random.randint(1, 100)
        creature_level = (
            random.randint(1, 5) if random_integer < 60 else
            random.randint(3, 10) if random_integer < 80 else
            random.randint(8, 18) if random_integer < 90 else
            random.randint(17, 36) if random_integer < 95 else
            random.randint(32, 65) if random_integer < 98 else
            random.randint(60, 120)
        )
        creature_level += difficulty
        
        user_level = data_functions.get_levels(interaction.user.id)
        level_difference = creature_level - user_level
        win_chance = 60
        
        if level_difference > 0:
            win_chance = math.floor(win_chance - (5 * math.log1p(level_difference)) - 5)
        else:
            win_chance = math.floor(win_chance + (5 * math.log1p(abs(level_difference))) + 5)
        
        mutation_multiplier = 1
        size_multiplier = 1
        
        mutation = random.choice(list(mutations.keys())) if random.randint(1, 5) == 1 else ""
        if mutation:
            mutation_multiplier = mutations[mutation]
            mutation_multiplier = math.ceil(mutation_multiplier / 1.5)
            win_chance -= 5 * abs(math.ceil(mutation_multiplier - 5))
            creature_level = math.ceil(creature_level * 1.5)
        
        size = random.choice(list(sizes.keys())) if random.randint(1, 5) == 1 else ""
        if size:
            size_multiplier = sizes[size]
            size_multiplier = math.ceil(size_multiplier / 1.5)
            win_chance -= 5 * abs(math.ceil(size_multiplier - 5))
            creature_level = math.ceil(creature_level * 1.5)
        
        reward = (random.randint(20, 50) * difficulty) + (random.randint(20, 50) * creature_level)
        risk = math.ceil(random.randint(20, 50) * difficulty) + creature_level * 2
        
        win_chance = max(5, min(95, win_chance))
        
        encounter_message = (
            f"⚔️ You encountered a**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type} (Level {creature_level})** in the wild."
            f"\n1. Fight\n2. Escape\n\n"
            f"*Your Level: {user_level}\nWin Chance: {win_chance}%\nDifficulty: {difficulty}/10\nRisk: {risk}*"
        )
        
        embed = discord.Embed(
            color=int("50B4E6", 16),
            description=encounter_message
        ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
    
        def check(msg: discord.Message):
            return msg.channel == interaction.channel and msg.author == interaction.user
    
        try:
            response = await self.bot.wait_for('message', check=check, timeout=15.0)
            
            if "1" in response.content.lower() or "fight" in response.content.lower():
                if random.randint(1, 100) <= win_chance:
                    embed = discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"✅ You defeated the**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}** and gained {reward} experience!"
                    ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                    data_functions.set_experience(interaction.user.id, data_functions.get_experience(interaction.user.id) + reward)
                else:
                    embed = discord.Embed(
                        color=int("FA3939", 16),
                        description=f"❌ You were defeated by the**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}** and lost {risk} experience."
                    ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                    data_functions.set_experience(interaction.user.id, max((data_functions.get_experience(interaction.user.id) - risk), 0))
            elif "2" in response.content.lower() or "escape" in response.content.lower():
                embed = discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"✅ You escaped from the**{' ' + size if size else ''} {' ' + mutation if mutation else ''} {creature_type}**."
                ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            else:
                embed = discord.Embed(
                    color=int("FA3939", 16),
                    description="❌ Invalid selection."
                ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
        
        except asyncio.TimeoutError:
            embed = discord.Embed(
                color=int("FA3939", 16),
                description="⏳ The command has been canceled because you took too long to reply."
            ).set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)

@bot.command(aliases=["s", "sy"], help="Make the bot say a specified message.")
async def say(ctx, *, message: str = None):
    if message is not None:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description="✅ " + message
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["setl", "sl"], help="Sets the levels of the specificed user (up to 200).")
async def set_levels(ctx, amount: int = None, name: str = None):
    if amount is not None and ctx.author.guild_permissions.manage_guild:
        if name is not None:
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
                            description=f"✅ Mutiple users found. Please select a user below, or type cancel:\n{msg}"
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    
                        selection = None
                        response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=10.0)
    
                        if "cancel" in response.content.lower():
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="❌ The command has been canceled."
                            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                            return
                        try:
                            selection = int(response.content)
                        except ValueError:
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="❌ Invalid selection."
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
                                        description="❌ Invalid selection."
                                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                                    return
                    except asyncio.TimeoutError:
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="⏳ The command has been canceled because you took too long to reply."
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                        return
                else:
                    for member in ctx.guild.members:
                        if member.name.lower() == matching_names[0].lower():
                            user = member
                            break
        else:
            user = ctx.author 
        if str(amount).isnumeric() and user is not None:
            if amount <= 200:
                data_functions.set_levels(user.id, int(amount))
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"✅ Successfully set {user.name}'s levels to {amount}."
                ).set_author(name=user.name, icon_url=user.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="❌ You can only set levels to a maximum of 200."
                ).set_author(name=user.name, icon_url=user.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="❌ Invalid amount."
            ).set_author(name=user.name, icon_url=user.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["setm", "sm"], help="Set the messages of the specified user (up to 5000).")
async def set_messages(ctx, amount: int = None):
    if amount is not None and ctx.author.guild_permissions.manage_guild:
        if str(amount).isnumeric():
            if amount <= 5000:
                data_functions.set_messages(ctx.author.id, int(amount))
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"✅ Successfully set {ctx.author.name}'s messages to {amount}."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="❌ You can only set your messages to a maximum of 5000."
                ).seŹ_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="❌ Invalid amount."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["nhie"], help="Gives a random 'Never Have I Ever' question.")
async def never_have_i_ever(ctx):
    question = random.choice(never_have_i_ever_questions)
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description="✅ " + question
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["bt"], help="Gives a random brain teaser.")
async def brain_teaser(ctx):
    index = random.randint(0, len(brain_teasers) - 1)
    question = brain_teasers[index]
    answer = brain_teaser_answers[index]

    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description="✅ " + question
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

    try:
        response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=15.0)
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"✅ The answer to the brain teaser is: **{answer}**"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"⏳ Time's up! The answer to the brain teaser is: **{answer}**"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["quiz", "triv"], help="Gives a random trivia question.")
async def trivia(ctx):
    embed = discord.Embed(
        color=int("50B4E6", 16),
        description="✅ Choose a category:\n" + "\n".join(f"- {category}" for category in trivia_categories.keys())
    )
    
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)
    
    trivia_questions = None
    try:
        category = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.lower() in [item.lower() for item in list(trivia_categories.keys())], timeout=15.0)
        trivia_questions = trivia_categories[category]
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"⏳ The command has been canceled because you took too long to reply."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    if trivia_questions is None:
        return
    index = random.randint(0, len(trivia_questions) - 1)
    question = list(trivia_questions.keys())[index]
    answer = list(trivia_questions.values())[index]

    choices = random.sample(list(trivia_questions.values()), 4)
    choices.append(answer)
    random.shuffle(choices)

    letter_choices = ["A", "B", "C", "D", "E"]
    choice_map = {letter: choices[i] for i, letter in enumerate(letter_choices)}
    correct_choice = next(k for k, v in choice_map.items() if v == answer)

    embed = discord.Embed(
        color=int("50B4E6", 16),
        description=f"💬 *Category: {category}*\n**{question}**\n\n" + "\n".join([f"{k} - {v}" for k, v in choice_map.items()])
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_footer(text="Reply with A, B, C, D, or E!")

    await ctx.send(embed=embed)

    try:
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.upper() in letter_choices, timeout=15.0)
        if msg.content.upper() == correct_choice:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ Correct, {ctx.author.mention}! The answer was **{correct_choice}: {answer}**."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ Incorrect, {ctx.author.mention}. The correct answer was **{correct_choice}: {answer}**."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"⏳ Time's up, {ctx.author.mention}! The correct answer was **{correct_choice}: {answer}**."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["sync", "sc"], help="Shows the current state of command syncing.")
async def sync_check(ctx):
    global sync_text
    if ctx.author.guild_permissions.manage_guild:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description="✅ " + sync_text
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

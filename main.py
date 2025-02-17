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
error_logs = []
never_have_i_ever_questions = [
    "Never have I ever broken a bone.",
    "Never have I ever gotten a papercut from a book.",
    "Never have I ever stayed up all night.",
    "Never have I ever gotten lost in a mall.",
    "Never have I ever missed an important event.",
    "Never have I ever eaten something off the floor.",
    "Never have I ever been in a talent show.",
    "Never have I ever forgotten my homework.",
    "Never have I ever walked into the wrong classroom.",
    "Never have I ever sung in the shower.",
    "Never have I ever laughed so hard I cried.",
    "Never have I ever tripped in public.",
    "Never have I ever blamed a sibling for something I did.",
    "Never have I ever been on a roller coaster.",
    "Never have I ever played a prank on someone.",
    "Never have I ever gotten detention.",
    "Never have I ever made a snow angel.",
    "Never have I ever gotten caught daydreaming in class.",
    "Never have I ever been on a sports team.",
    "Never have I ever gotten stage fright.",
    "Never have I ever lost my lunch money.",
    "Never have I ever been stung by a bee.",
    "Never have I ever built a fort out of blankets.",
    "Never have I ever peed in a pool.",
    "Never have I ever forgotten a friend's birthday.",
    "Never have I ever laughed at the wrong moment.",
    "Never have I ever worn mismatched socks.",
    "Never have I ever gotten lost in a store.",
    "Never have I ever dropped my phone in water.",
    "Never have I ever waved at someone who wasn't waving at me.",
    "Never have I ever lost a library book.",
    "Never have I ever accidentally called a teacher 'Mom' or 'Dad'.",
    "Never have I ever spilled something on myself in public.",
    "Never have I ever cried during a movie.",
    "Never have I ever met a celebrity.",
    "Never have I ever been afraid of the dark.",
    "Never have I ever built a sandcastle.",
    "Never have I ever played video games all night.",
    "Never have I ever worn pajamas all day.",
    "Never have I ever watched cartoons as a teenager.",
    "Never have I ever been to a school dance.",
    "Never have I ever made a TikTok or YouTube video.",
    "Never have I ever forgotten my own phone number.",
    "Never have I ever eaten a whole pizza by myself.",
    "Never have I ever laughed so hard I snorted.",
    "Never have I ever been on a plane.",
    "Never have I ever broken a piece of furniture by sitting on it.",
    "Never have I ever had food stuck in my teeth all day.",
    "Never have I ever accidentally sent a text to the wrong person.",
    "Never have I ever won a contest.",
    "Never have I ever been outside of my country.",
    "Never have I ever accidentally worn someone else's clothes.",
    "Never have I ever gotten gum stuck in my hair.",
    "Never have I ever pulled an all-nighter for an exam.",
    "Never have I ever had a pet fish.",
    "Never have I ever walked into a glass door.",
    "Never have I ever forgotten where I parked my car.",
    "Never have I ever fallen off my bike.",
    "Never have I ever laughed during a serious moment.",
    "Never have I ever eaten something I knew was expired.",
    "Never have I ever gotten a haircut I didn't like.",
    "Never have I ever accidentally used someone else's toothbrush.",
    "Never have I ever mistaken a stranger for someone I knew.",
    "Never have I ever been on a waterslide.",
    "Never have I ever eaten a bug by accident.",
    "Never have I ever been in a parade.",
    "Never have I ever spilled water while trying to drink it.",
    "Never have I ever gotten my shoe stuck in mud.",
    "Never have I ever forgotten an important event.",
    "Never have I ever borrowed something and never returned it.",
    "Never have I ever used a fake excuse to get out of something.",
    "Never have I ever drawn on someone's face while they were sleeping.",
    "Never have I ever played hide and seek as a teenager.",
    "Never have I ever been to a sleepover.",
    "Never have I ever fallen off a chair.",
    "Never have I ever worn my clothes inside out by accident.",
    "Never have I ever tried to learn a dance from the internet.",
    "Never have I ever done a magic trick.",
    "Never have I ever accidentally deleted an important file.",
    "Never have I ever been the last one picked for a team.",
    "Never have I ever gotten sunburnt.",
    "Never have I ever been on a boat.",
    "Never have I ever broken something and blamed it on someone else.",
    "Never have I ever been scared of a movie as a kid.",
    "Never have I ever accidentally said 'I love you' to someone by mistake.",
    "Never have I ever had a funny nickname.",
    "Never have I ever forgotten my backpack at school.",
    "Never have I ever been in a food fight.",
    "Never have I ever been on a road trip.",
    "Never have I ever been chased by an animal.",
    "Never have I ever lost a bet.",
    "Never have I ever seen snow in real life.",
    "Never have I ever baked cookies from scratch.",
    "Never have I ever accidentally broken a plate or glass.",
    "Never have I ever danced in the rain.",
    "Never have I ever been scared of clowns.",
    "Never have I ever laughed at a joke I didn't get.",
    "Never have I ever made a silly face in a serious photo.",
    "Never have I ever eaten food that was meant for a pet.",
    "Never have I ever been the teacher's favorite.",
    "Never have I ever forgotten my lunch at home.",
    "Never have I ever wished on a shooting star.",
    "Never have I ever cried from laughing too hard.",
    "Never have I ever been on a Ferris wheel.",
    "Never have I ever played a board game all the way through.",
    "Never have I ever accidentally ruined a surprise.",
    "Never have I ever lost a piece of a puzzle.",
    "Never have I ever climbed a mountain.",
    "Never have I ever worn sunglasses indoors."
]

bot = commands.Bot(command_prefix=lambda bot, message: data_functions.get_prefix(message.guild.id), intents=intents)

data_functions.setup_database()

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(discord.Object(id=1292978415552434196))
    except Exception as e:
        error_logs.append(e)
        if len(error_logs) > 20:
            if error_logs and 0 in error_logs:
                del error_logs[0]
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

    if math.floor(random.random() * 100 + 1) <= 5:
        random_integer = random.randint(1, 100)
        type = "Common" if random_integer < 60 else "Rare" if random_integer < 80 else "Epic" if random_integer < 90 else "Legendary" if random_integer < 95 else "Mythical" if random_integer < 98 else "Celestial" 
        amount = random.randint(60, 150) if random_integer < 60 else random.randint(120, 250) if random_integer < 80 else random.randint(240, 380) if random_integer < 90 else random.randint(350, 520) if random_integer < 95 else random.randint(510, 800) if random_integer < 98 else random.randint(750, 1200) 
        await msg.channel.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            title="Experience Drop",
            description=f"A **{type}** Experience Drop of {amount} has started! Type 'claim' to claim it before the time runs out!"
        ))
        try:
            response = await bot.wait_for('message', check=lambda msg2: msg2.channel == msg.channel and msg2.content.lower() == "claim", timeout=10.0)
            if not response.author.bot:
                await msg.channel.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    title="Experience Drop",
                    description=f"*{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
                ))
                data_functions.set_experience(response.author.id, data_functions.get_experience(response.author.id) + amount)
        except asyncio.TimeoutError:
            await msg.channel.send(embed=discord.Embed(
                color=int("FA3939", 16),
                title="Experience Drop",
                description="Nobody claimed the experience drop in time."
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
            description=f"Congratulations! The user *'{msg.author.name}'* has leveled up to **Level {data_functions.get_levels(user_id)}**!"
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
                description=f"**{command.name}** - {command.help}\n**Aliases:** {', '.join(command.aliases) if command.aliases else 'None'}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        help_text = "- " + "\n- ".join([f"**{cmd.name}** - {cmd.help}\n**Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'None'}" for cmd in bot.commands])
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"{help_text}"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["vp", "viewp"], help="Shows the current prefix of this bot.")
async def view_prefix(ctx):
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"The current prefix is '{data_functions.get_prefix(ctx.guild.id)}'."
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.tree.command(name="viewprefix", description="Shows the current prefix of this bot.")
async def slash_view_prefix(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        embed = discord.Embed(
            color=int("50B4E6", 16),
            description=f"The current prefix is '{data_functions.get_prefix(interaction.guild.id)}'."
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
                    description="The prefix chosen is too long. Please try again with a shorter prefix."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
            data_functions.set_prefix(ctx.guild.id, new_prefix)
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"The prefix has successfully been changed to '{new_prefix}'."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
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
                        description="The prefix chosen is too long. Please try again with a shorter prefix."
                    ).set_author(name=interaction.member.name, icon_url=interaction.member.avatar.url))
                    return
                data_functions.set_prefix(ctx.guild.id, new_prefix)
                await interaction.followup.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"The prefix has successfully been changed to '{new_prefix}'."
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
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
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
                            description=f"Mutiple users found. Please select a user below, or type cancel:\n{msg}"
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    
                        selection = None
                        response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=15.0)
    
                        if "cancel" in response.content.lower():
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="The command has been canceled."
                            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                            return
                        try:
                            selection = int(response.content)
                        except ValueError:
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="Invalid selection."
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
                                        description="Invalid selection."
                                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                                    return
                    except asyncio.TimeoutError:
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="The command has been canceled because you took too long to reply."
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
                description=f"**Retrieving data for {user.name}...**"
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"**Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}"
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
                description=f"**Retrieving data for '{user.name}'...**"
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await interaction.followup.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="Statistics",
                description=f"**Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}"
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
            description=f"A **{type}** Experience Drop of {amount} has started! Type 'claim' to claim it before the time runs out!"
        ))
        try:
            response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.content.lower() == "claim", timeout=15.0)
            if not response.author.bot:
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    title="Experience Drop",
                    description=f"*{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
                ))
                data_functions.set_experience(response.author.id, data_functions.get_experience(response.author.id) + amount)
        except asyncio.TimeoutError:
            await msg.channel.send(embed=discord.Embed(
                color=int("FA3939", 16),
                title="Experience Drop",
                description="Nobody claimed the experience drop in time."
            ))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["fgt"], help="Fight against a creature for rewards.")
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
            f"You encountered a{' ' + size if size else ''}{' ' + mutation if mutation else ''} **{creature_type} (Level {creature_level})** in the wild."
            f" Choose an option below:\n1. Fight\n2. Escape\n\n"
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
                        description=f"You defeated the*{' ' + size if size else ''}{' ' + mutation if mutation else ''}* **{creature_type}** and gained {reward} experience!"
                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                    data_functions.set_experience(ctx.author.id, data_functions.get_experience(ctx.author.id) + reward)
                else:
                    await ctx.send(embed=discord.Embed(
                        color=int("FA3939", 16),
                        description=f"You were defeated by the*{' ' + size if size else ''}{' ' + mutation if mutation else ''}* **{creature_type}** and lost {risk} experience."
                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                    data_functions.set_experience(ctx.author.id, max((data_functions.get_experience(ctx.author.id) - risk), 0))
            elif "2" in response.content.lower() or "escape" in response.content.lower():
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"You escaped from the*{' ' + size if size else ''}{' ' + mutation if mutation else ''}* **{creature_type}**."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="Invalid selection."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="The command has been canceled because you took too long to reply."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["s", "sy"], help="Make the bot say a specified message.")
async def say(ctx, *, message: str = None):
    if message is not None:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=message
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
                            description=f"Mutiple users found. Please select a user below, or type cancel:\n{msg}"
                        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    
                        selection = None
                        response = await bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=10.0)
    
                        if "cancel" in response.content.lower():
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="The command has been canceled."
                            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                            return
                        try:
                            selection = int(response.content)
                        except ValueError:
                            await ctx.send(embed=discord.Embed(
                                color=int("FA3939", 16),
                                description="Invalid selection."
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
                                        description="Invalid selection."
                                    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                                    return
                    except asyncio.TimeoutError:
                        await ctx.send(embed=discord.Embed(
                            color=int("FA3939", 16),
                            description="The command has been canceled because you took too long to reply."
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
                    description=f"Successfully set {user.name}'s levels to {amount}."
                ).set_author(name=user.name, icon_url=user.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="You can only set levels to a maximum of 200."
                ).set_author(name=user.name, icon_url=user.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="Invalid amount."
            ).set_author(name=user.name, icon_url=user.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["setm", "sm"], help="Set the messages of the specified user (up to 5000).")
async def set_messages(ctx, amount: int = None):
    if amount is not None and ctx.author.guild_permissions.manage_guild:
        if str(amount).isnumeric():
            if amount <= 5000:
                data_functions.set_messages(ctx.author.id, int(amount))
                await ctx.send(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"Successfully set {ctx.author.name}'s messages to {amount}."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                await ctx.send(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="You can only set your messages to a maximum of 5000."
                ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
                return
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="Invalid amount."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["nhie"], help="Gives a random 'Never Have I Ever' question.")
async def never_have_i_ever(ctx):
    question = random.choice(never_have_i_ever_questions)
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=question
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["lgs", "lg"], help="Shows the error logs of this bot.")
async def logs(ctx):
    if ctx.author.guild_permissions.manage_guild:
        if error_logs:
            logs_text = ""
            for i, log in enumerate(error_logs):
                if i <= 20:
                    logs_text += log + "\n"
                else:
                    break
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"**Logs:**\n{logs_text}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"No logs to show!"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

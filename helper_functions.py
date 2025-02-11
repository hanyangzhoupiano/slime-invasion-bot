import asyncio
import discord

async def experience_drop(ctx, amount):
    if amount is not None and str(amount).isnumeric():
        global experience_drops
        if amount <= 10000:
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
        else:
            await ctx.send(embed=discord.Embed(
                color=int("FA3939", 16),
                description="You can only drop 10,000 experience at a time.",
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url))

import asyncio
import math
import discord
import random
from discord.ext import commands
import logging.config

from config import BOT_TOKEN
from logger import DEFAULT_CONFIG
from run import Run
from apihandler import ApiHandler

if 1 == 1:
    GENERAL_ID = 688951042498363415
else:
    GENERAL_ID = 465058736608641049 # testing pruposes

STATUSES = [
    "failing at 50 HSG",
    "resetting on 1",
    "dying on 47",
    "turning particles off",
    "Wallkicks will Work",
    "using sorcery to skip 45"
]

speedbot = commands.Bot(command_prefix='.')
api = ApiHandler()
logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("bot")

def suf(n):
    """Returns an ordinal suffix like 'st', 'rd', 'th' depending on n"""
    return "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))

def create_embed(run_id):
    """Creates a discord.py embed using a given run's ID"""
    run = api.get_run(run_id)
    verifier_name = api.get_player(run.get_verifier()).get_name()
    player = api.get_player(run.get_runner_id())
    player_name = player.get_name()

    place = api.get_place_from_run_id(run_id, run.get_category())
    time = run.get_igt_formatted()
    
    flag = player.get_flag()
    colour = player.get_colour()
    link = run.get_link()
    date = run.get_date()

    embed = discord.Embed(
        title = f"{player_name} {flag} | {suf(place)}",
        description = run.get_comment(),
        colour = discord.Colour.from_rgb(colour[0], colour[1], colour[2]), # unsure if this needs to be done
    )

    if int(place) <= 4:
        embed.set_thumbnail(url=f"https://www.speedrun.com/themes/gur1/{suf(place)}.png")

    embed.set_footer(text=f'Submitted on {date}, verified by {verifier_name}')
    embed.add_field(name='Time', value=time, inline=False)
    embed.add_field(name='Link', value=link, inline=False)

    log.info(f"Created embed for run by {player_name} in {time}, with color {colour}")
    return embed

def create_top_run_embed(category_name, n):
    """Creates an embed containing the top n runs in the given category."""
    runs = api.get_leaderboard_data(category_name)["runs"]
    n = n if len(runs) > n else len(runs)

    embed = discord.Embed(
        title = f":medal: - Top {n} {category_name} runs",
        colour = discord.Colour.blue()
    )

    for x in range(n):
        run = Run(runs[x]["run"]) # run

        player = api.get_player(run.get_runner_id())
        player_name = player.get_name()
        flag = player.get_flag()
        time = run.get_igt_formatted()
        link = run.get_link()

        embed.add_field(
            name=f"{suf(x + 1)} | {flag} {player_name} | {time}",
            value=link,
            inline=False
        )
    
    return embed

@speedbot.command()
async def run(ctx, category, name):
    """Delivers information about a user's run in a category."""
    run = api.get_run_id(category, name)
    if not run:
        log.warning(f"Could not find run for {name} in {category}!")
        await ctx.send(f"No run for `{name}` in category `{category}` found! Either they aren't on the leaderboards or are a guest user.")
        return
    
    log.info(f"Posting run by {name} in {category} after being asked")
    embed = create_embed(run)
    await ctx.send(embed=embed)

@speedbot.command()
async def top(ctx, category, n=10):
    """Returns info about the top n runs in a category."""
    if n > 20 or n < 1:
        log.warning(f"User tried to return top {n} logs, out of range!")
        await ctx.send(f'Number of runs must be <= 20 and > 1!')
        return

    log.info(f"Posting top {n} runs in {category} after being asked")
    embed = create_top_run_embed(category, n)
    await ctx.send(embed=embed)

@speedbot.command()
async def newest(ctx):
    # We can just trust that our ApiHandler has the newest one cached. 
    run_id = api.newest_cached
    if not api.newest_cached:
        await ctx.send('Not finished initializing!') # shouldn't happen, but whatevs
        log.warning("Tried to post newest run before initializing finished!")
        return

    log.info("Posting newest run after being asked!")
    embed = create_embed(run_id)
    await ctx.send(embed=embed)

async def change_presence():
    """Randomizes Speedbot's presence to somethin funny I guess."""
    while not speedbot.is_closed():
        choice = random.choice(STATUSES)
        log.info(f"Chose status '{choice}'!")
        activity = discord.Game(choice)
        await speedbot.change_presence(activity=activity)
        await asyncio.sleep(60 * 20)

async def new_run_alert():
    """Runs every 5 minutes. Will check if there has been a new run verified. If so,
    post an embed about it."""

    await speedbot.wait_until_ready()
    channel = speedbot.get_channel(GENERAL_ID)
    while not speedbot.is_closed():
        if api.check_for_new_run():
            log.info("Posting newest run automatically!")
            await channel.send(f'**A new run has been verified!**')
            embed = create_embed(api.newest_cached)
            await channel.send(embed=embed)
        else:
            log.info("No new runs found.")
        await asyncio.sleep(60 * 5)

if __name__ == "__main__":
    speedbot.loop.create_task(new_run_alert())
    speedbot.loop.create_task(change_presence())
    speedbot.run(BOT_TOKEN)

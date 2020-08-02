import asyncio
import math
import discord
import random
from discord.ext import commands
import logging.config

from config import BOT_TOKEN
from logger import DEFAULT_CONFIG
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

def format_time(secs):
    """Yes, I know strftime exists. It did not work."""
    mins = (int(secs / 60))
    lsecs = int(secs % 60)
    ms = round((secs - int(secs)) * 1000)
    if ms < 10:
        ms *= 10
    if lsecs < 10:
        return f"{mins}:0{lsecs}.{ms}"
    else:
        return f"{mins}:{lsecs}.{ms}"

def hex_to_rgb(h):
    """Converts a hexcode like `#FABD12` to an RGB triple."""
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_embed(run_id):
    """Creates a discord.py embed using a given run's ID"""
    run = api.get_run_data(run_id)
    verifier_name = api.get_user_data(run["status"]["examiner"])["names"]["international"]
    player = api.get_user_data(run["players"][0]["id"])
    player_name = player["names"]["international"]

    # lol ordinals stolen from stackoverflow
    suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
    place = api.get_place_from_run_id(run_id, run["category"])
    time = format_time(run["times"]["ingame_t"])
    
    country = player["location"]["country"]["code"]
    flag = f":flag_{country}:" # discord emote. doesn't work for some flags, like wales or quebec since they're provinces (sorta)
    colour = hex_to_rgb(player["name-style"]["color-from"]["dark"])

    if "videos" in run:
        link = run["videos"]["links"][0]["uri"]

    embed = discord.Embed(
        title = f'{player_name} {flag} | {suf(place)}',
        description = run["comment"],
        colour = discord.Colour.from_rgb(colour[0], colour[1], colour[2]), # unsure if this needs to be done
    )

    if int(place) <= 4:
        embed.set_thumbnail(url=f"https://www.speedrun.com/themes/gur1/{suf(place)}.png")

    embed.set_footer(text=f'Submitted on {run["date"]}, verified by {verifier_name}')
    embed.add_field(name='Time', value=time, inline=False)
    if link:
        embed.add_field(name='Link', value=link, inline=False)
    else:
        log.debug(f"No video link for run {run} by {player_name} found!")

    log.debug(f"Created embed for run by {player_name} in {time}, with color {colour}")
    return embed

@speedbot.command()
async def run(ctx, category, name):
    """Delivers information about a user's run in a category."""
    run = api.get_run_id(category, name)
    if not run:
        log.warning(f"Could not find run for {name} in {category}!")
        await ctx.send(f'No run for `{name}` in category `{category}` found!')
        return
    
    log.info(f"Posted run by {name} in {category} after being asked")
    embed = create_embed(run)
    await ctx.send(embed=embed)

@speedbot.command()
async def top(ctx, category, n=10):
    """Returns info about the top n runs in a category."""
    if n > 20 and n > 1:
        log.warning(f"User tried to return top {n} logs, out of range!")
        await ctx.send(f'Number of runs must be <= 20 and > 1!')
        return

    # runs = api.get_top_runs(category, n)

    log.info(f"Posted top runs to {n} after being asked")
    embed = discord.Embed(
        title = f'Top Runs in **{category}**',
        colour = discord.Colour.purple()
    )

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
            log.debug("No new runs found.")
        await asyncio.sleep(60 * 5)

if __name__ == "__main__":
    speedbot.loop.create_task(new_run_alert())
    speedbot.loop.create_task(change_presence())
    speedbot.run(BOT_TOKEN)

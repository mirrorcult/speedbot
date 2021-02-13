import asyncio
import discord
import random
import os
import markovify
from discord.ext import commands
import logging.config

import config
import logger
from secret import BOT_TOKEN
from run import Run
from apihandler import ApiHandler

speedbot = commands.Bot(command_prefix=config.PREFIX)
api = ApiHandler(config.GAME_ID)
logging.config.dictConfig(logger.DEFAULT_CONFIG)
log = logging.getLogger("bot")

botdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
assetsdir = os.path.join(botdir, "assets")

with open(os.path.join(assetsdir, "text-corpus.txt"), encoding="utf8", errors="ignore") as f:
    text_data = f.read()
text_model = markovify.NewlineText(text_data).compile()


def suf(n):
    """Returns an ordinal suffix like 'st', 'rd', 'th' depending on n"""
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}
                     .get(n if n < 20 else n % 10, "th"))


def create_embed(run_id):
    """Creates a discord.py embed using a given run's ID"""
    if run_id == -1:
        log.warning("Invalid run ID passed to create_embed")
        return

    run = api.get_run(run_id)
    verifier_name = api.get_user(run.get_verifier_id()).get_name()
    runner = api.get_user(run.get_runner_id())
    runner_name = runner.get_name()

    place = api.get_place_from_run_id(run_id, run.get_category_id())
    time = run.get_primary_time_formatted()
    category = api.categorylevel_name_from_id(run.get_category_id())

    flag = runner.get_flag()
    colour = runner.get_colour()
    link = run.get_link()
    date = run.get_date()

    embed = discord.Embed(
        title=f"{runner_name} {flag} | {suf(place)} in {category}",
        description=run.get_comment(),
        colour=discord.Colour.from_rgb(colour[0], colour[1], colour[2]),
    )

    if int(place) <= 4:
        embed.set_thumbnail(
            url=f"https://www.speedrun.com/themes/{api.game_id}/{suf(place)}.png"
        )

    embed.set_footer(text=f"Submitted on {date}, verified by {verifier_name}")
    embed.add_field(name="Time", value=time, inline=False)
    embed.add_field(name="Link", value=link, inline=False)

    log.info(f"Created embed for run by {runner_name} in {time}, with color {colour}")
    return embed


def create_top_run_embed(category_name, n):
    """Creates an embed containing the top n runs in the given category."""
    runs = api.get_category_leaderboard(category_name)["runs"]
    n = n if len(runs) > n else len(runs)

    embed = discord.Embed(
        title=f":medal: - Top {n} {category_name} runs",
        colour=discord.Colour.blue()
    )

    for x in range(n):
        run = Run(runs[x]["run"])  # run

        runner = api.get_user(run.get_runner_id())
        runner_name = runner.get_name()
        flag = runner.get_flag()
        time = run.get_primary_time_formatted()
        link = run.get_link()

        embed.add_field(
            name=f"{suf(x + 1)} | {flag} {runner_name} | {time}",
            value=link,
            inline=False
        )
    return embed


@speedbot.command()
async def game(ctx, game):
    """Changes game ID"""
    api.game_id = game
    log.info(f"Changed game to {game}")
    await ctx.send(f"Changed game to {game}!")


@speedbot.command()
async def markov(ctx):
    generated = text_model.make_sentence(max_overlap_ratio=0.85)
    generated_trim = generated.replace("@", " @ ")\
        .replace("&quot;", "\"")\
        .replace("&#39;", "'")
    await ctx.send(generated_trim)


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
        await ctx.send("Number of runs must be <= 20 and > 1!")
        return

    log.info(f"Posting top {n} runs in {category} after being asked")
    embed = create_top_run_embed(category, n)
    await ctx.send(embed=embed)


@speedbot.command()
async def newest(ctx, category=None):
    """Returns info about the newest run submitted."""
    api.check_for_new_run()

    # We can just trust that our ApiHandler has the newest one cached.
    run_id = api.newest_cached
    if not api.newest_cached:
        await ctx.send("Not finished initializing!")
        log.warning("Tried to post newest run before initializing finished!")
        return

    if category is None:
        log.info("Posting newest run in any category after being asked!")
        embed = create_embed(run_id)
        await ctx.send(embed=embed)
    else:
        log.info(f"Posting newest run in category {category} after being asked!")
        run_id = api.newest_in_categories.get(api.cat_name_to_id(category), -1)
        embed = create_embed(run_id)
        if embed is not None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No run cached for category {category} yet!")


async def change_presence():
    """Randomizes Speedbot's presence to somethin funny I guess."""
    await speedbot.wait_until_ready()
    while not speedbot.is_closed():
        choice = random.choice(config.STATUSES)
        # log.info(f"Chose status '{choice}'!")
        activity = discord.Game(choice)
        await speedbot.change_presence(activity=activity)
        await asyncio.sleep(60 * 20)


async def new_run_alert():
    """Runs every 5 minutes. Will check if there has been a new run verified.
    If so, post an embed about it."""
    await speedbot.wait_until_ready()
    channel = speedbot.get_channel(GENERAL_ID)
    while True:
        if api.check_for_new_run() and not speedbot.is_closed():
            log.info("Posting newest run automatically!")
            await channel.send("**A new run has been verified!**")
            embed = create_embed(api.newest_cached)
            await channel.send(embed=embed)
        # else:
            # log.info("No new runs found.")
        await asyncio.sleep(60 * 5)

if __name__ == "__main__":
    speedbot.loop.create_task(new_run_alert())
    speedbot.loop.create_task(change_presence())
    speedbot.run(BOT_TOKEN)

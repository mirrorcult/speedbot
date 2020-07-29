import srcomapi, srcomapi.datatypes as dt
import asyncio
import math
import discord
from discord.ext import commands
from config import BOT_TOKEN

if 1 == 1:
    GENERAL_ID = 688951042498363415
else:
    GENERAL_ID = 465058736608641049 # testing pruposes

STATUS = "failing at 50 HSG"
GUR_GAME_ID = "j1l7ojdg"
CATEGORIES = {
    'normal': 'wkp53vdr',
    'hard': '7dgm64d4'
}

speedbot = commands.Bot(command_prefix='.')
api = srcomapi.SpeedrunCom(); api.debug = 1

class LeaderboardHandler:
    """Class that handles returning info from the leaderboard, and checking for new runs."""

    def __init__(self):
        # Caches the newest run's ID on init
        self.newest_cached = None

    def get_run_from_name(self, category, name):
        """Retrieves a Give Up Robot SRC (PB) run in the given category by the given username."""
        pbs = api.get(f"users/{name}/personal-bests?embed=game,category")
        for r in pbs:
            if r["game"]["data"]["id"] == GUR_GAME_ID and r["category"]["data"]["id"] == CATEGORIES[category]:
                print(f"Found run in {category} by {name}!")
                return r["run"]["id"]  # done for compatibility reasons and also butt
        return None

    def get_place_from_run(self, run_id, category):
        """Returns a run's place given it's ID and category"""
        # This shouldn't be this hard. Why is place just not included with runs??
        board = api.get(f"leaderboards/{GUR_GAME_ID}/category/{category}")
        for r in board["runs"]:
            if r["run"]["id"] == run_id:
                return r["place"]
        return 0 # this could not possibly happen, right?

    def get_user(self, user):
        """Get a user's data based on their name."""
        return api.get(f"users/{user}")

    def check_for_new_run(self):
        """Checks if a run newer than the one cached has been created.
           If one has, then set self.newest_cached to be equal to its ID, and return true."""

        # A very.. special query
        newest_id = api.get(f"runs?status=verified&game={GUR_GAME_ID}&orderby=verify-date&direction=desc&embed=category")[0]["id"]
        print(f"Found newest run candidate {newest_id}")
        if newest_id != self.newest_cached and self.newest_cached != None: # if newest_cached is None, that means we just initialized, so there probably isn't actually a new run
            self.newest_cached = newest_id
            return True
        self.newest_cached = newest_id
        return False

    def get_top_runs(self, category, n=10):
        """Returns the top 'n' runs in the given category in a list."""
        pass

lb = LeaderboardHandler()

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

def create_embed(run_id):
    """Creates a discord.py embed using a given run's ID"""
    run = api.get(f"runs/{run_id}")
    verifier = lb.get_user(run["status"]["examiner"])
    player = lb.get_user(run["players"][0]["id"])

    # lol ordinals stolen from SO
    suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
    place = lb.get_place_from_run(run_id, run["category"])

    embed = discord.Embed(
        title = f'{player["names"]["international"]} | {suf(place)}',
        description = run["comment"],
        colour = discord.Colour.purple(),
    )

    if int(place) <= 4:
        embed.set_thumbnail(url=f"https://www.speedrun.com/themes/gur1/{suf(place)}.png")

    embed.set_footer(text=f'Submitted on {run["date"]}, verified by {verifier["names"]["international"]}')
    embed.add_field(name='Time', value=format_time(run["times"]["ingame_t"]), inline=False)
    embed.add_field(name='Link', value=run["videos"]["links"][0]["uri"], inline=False) # TODO make this not error when they dont haev a video link
    return embed

@speedbot.command()
async def run(ctx, category, name):
    """Delivers information about a user's run in a category."""
    run = lb.get_run_from_name(category, name)
    if not run:
        await ctx.send(f'No run for `{name}` in category `{category}` found!')
        return
    
    print(f"Posted run by {name} in {category} after being asked")
    embed = create_embed(run)
    await ctx.send(embed=embed)

@speedbot.command()
async def top(ctx, category, n=10):
    """Returns info about the top n runs in a category."""
    if n > 20 and n > 1:
        await ctx.send(f'Number of runs must be <= 20 and > 1!')
        return

    runs = lb.get_top_runs(category, n)

    print(f"Posted top runs to {n} after being asked")
    embed = discord.Embed(
        title = f'Top Runs in **{category}**',
        colour = discord.Colour.purple()
    )

@speedbot.command()
async def newest(ctx):
    # We can just trust that our LeaderboardHandler has the newest one cached. 
    run_id = lb.newest_cached
    if not lb.newest_cached:
        await ctx.send('Not finished initializing!') # shouldn't happen, but whatevs
        return

    print("Posted new run after being asked")
    embed = create_embed(run_id)
    await ctx.send(embed=embed)

@speedbot.event
async def on_ready():
    await speedbot.change_presence(activity=discord.Game(name=STATUS))

async def new_run_alert():
    """Runs every 5 minutes. Will check if there has been a new run verified. If so,
    post an embed about it."""

    await speedbot.wait_until_ready()
    channel = speedbot.get_channel(GENERAL_ID)
    while not speedbot.is_closed():
        if lb.check_for_new_run():
            print("Posted new run automatically!")
            await channel.send(f'**A new run has been verified!**')
            embed = create_embed(lb.newest_cached)
            await channel.send(embed=embed)

        await asyncio.sleep(60 * 5)

if __name__ == "__main__":
    speedbot.loop.create_task(new_run_alert())
    speedbot.run(BOT_TOKEN)

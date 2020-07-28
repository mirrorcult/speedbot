import srcomapi, srcomapi.datatypes as dt
import json
import discord
from discord.ext import commands
from config import BOT_TOKEN

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
        # Caches the newest run and current leaderboard on initialization
        self.lb = self.cache_lb()
        
        self.newest = None
        self.check_for_new_run()

    def get_run_from_name(self, category, name):
        """Retrieves a Give Up Robot SRC (PB) run in the given category by the given username."""
        pbs = data=api.get(f"users/{name}/personal-bests?embed=game,category")
        for r in pbs:
            if r["game"]["data"]["id"] == GUR_GAME_ID and r["category"]["data"]["id"] == CATEGORIES[category]:
                print(r)
                return r
        return None

    def get_user(self, user):
        """Get a user's data based on their name."""
        return api.get(f"users/{user}")


    def cache_lb(self):
        """Caches the leaderboard."""
        g = api.search(srcomapi.datatypes.Game, {"name": "gur1"})[0]
        assert(g.name == "Give Up, Robot")

        runs = {}
        for cat in g.categories:
            if not cat.name in runs:
                runs[cat.name] = {}
            runs[cat.name] = api.get(f"leaderboards/{g.id}/category/{cat.id}?embed=variables")
        
        return runs

    def check_for_new_run(self):
        """Checks if a run newer than the one cached has been created."""
        pass

    def get_top_runs(self, category, n=10):
        """Returns the top 'n' runs in the given category in a list."""
        pass

lb = LeaderboardHandler()

@speedbot.command()
async def run(ctx, category, name):
    run = lb.get_run_from_name(category, name)
    if not run:
        await ctx.send(f'No run for `{name}` in category `{category}` found!')
    
    # Send a pretty embed
    embed = discord.Embed(
        title = f'Place: {run["place"]}',
        description = run["run"]["comment"],
        colour = discord.Colour.green()
    )

    embed.add_field(name='Time', value=run["run"]["times"]["ingame_t"], inline=False)
    embed.add_field(name='Link', value=run["run"]["videos"]["links"][0]["uri"], inline=False) # TODO make this not error when they dont haev a video link

    await ctx.send(embed=embed)

@speedbot.command()
async def top(ctx):
    pass

@speedbot.command()
async def newest(ctx):
    pass

if __name__ == "__main__":
    speedbot.run(BOT_TOKEN)

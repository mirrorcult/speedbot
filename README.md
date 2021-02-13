# Speedbot

![Python application](https://github.com/cyclowns/speedbot/workflows/Python%20application/badge.svg) ![codecov](https://codecov.io/gh/cyclowns/speedbot/branch/master/graph/badge.svg)

Discord bot utilizing the SRC API for speedrunning-related discords.

![sc1](https://i.imgur.com/NXICU3k.png) ![sc2](https://i.imgur.com/1d5io7N.png)

It can:

- Give info about runs based on fuzzy-matched category/level and player names with fancy embeds
- Post the top `n` runs in a given category with fancy embeds
- Alert people in a given channel when new runs are posted
- Give info about games and categories, like # of runners, rules, and so on (TODO)

## Running

First, create a discord bot application.

Then create a file called `secret.py` in the `src` directory with contents like this:

```python
BOT_TOKEN = "{your bot token here}"
```

You also probably wanna change the channel IDs in src/config.py if you want newest run announcements (TODO: config to disable this)

Run these commands (assuming python3 and pip are installed and in your system PATH):

```sh
pip3 install -r requirements.txt
coverage run src/tests.py
```

If all the tests pass, you're good to run this command:

```sh
python src/main.py
```

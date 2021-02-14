# Speedbot

![Python application](https://github.com/cyclowns/speedbot/workflows/Python%20application/badge.svg) ![codecov](https://codecov.io/gh/cyclowns/speedbot/branch/master/graph/badge.svg)

Discord bot utilizing the SRC API for speedrunning-related discords.

![sc1](https://i.imgur.com/NXICU3k.png) ![sc2](https://i.imgur.com/1d5io7N.png)

Features include:

- Pretty embeds for player runs, top runs in a category, game info, etc.
- Fuzzy matching category/player names for convenient lookups
- Logging and simple configuration
- Stable & robust backend that can handle subcategories, categories, level runs, etc. (TODO)

## Commands

[] = mandatory, () = optional

### run

`run [category] [player]`

### top

`top [category] (n)`

### ginfo

`ginfo (game)`

### cinfo

`cinfo [category]`

### clist

`clist (game)`

### newest

`newest (category)`

### place

`place [category] [place]`

## Optional Commands

These commands are all optional, and must be enabled in config.py to work properly.

### game

`.game [game_id]`

Changes the current game context to the given game ID,

![game](https://i.imgur.com/nELzeIU.png)

### markov

`.markov`

Funny markov text generation.

## Running it yourself

First, create a discord bot application.

Then create a file called `secret.py` in the `src` directory with contents like this:

```python
BOT_TOKEN = "{your bot token here}"
```

You're also going to want to change a lot of stuff in `src/config.py` to match with what you're doing. Change the game ID to whatever game you're going to work with by default, enable/disable the various optional features, etc.

Run these commands (assuming python3 and pip are installed and in your system PATH):

```sh
pip3 install -r requirements.txt
coverage run src/tests.py
```

If all the tests pass, you're good to run this command:

```sh
python src/speedbot.py
```

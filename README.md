# Speedbot

Basic discord bot utilizing the SRC API for the GUR speedrunning discord

## Running

First, create a discord bot application.

Then create a file called `config.py` in the `src` directory with contents like this:

```python
BOT_TOKEN = "{your token here}"
```

You also probably wanna change the channel IDs in src/main.py to match up with whatever you're doing, I guess? I don't know who else would use this besides our discord, though.

Then run these commands (assuming python3 is installed):

```sh
pip3 install -r requirements.txt
python src/main.py
```

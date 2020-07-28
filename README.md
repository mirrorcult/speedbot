# Speedbot

Basic discord bot utilizing the SRC API for the GUR speedrunning discord

## Running

First, create a discord bot application.

Then create a file called `config.py` in the `src` directory with contents like this:

```python
BOT_TOKEN = "{your token here}"
```

Then run these commands (assuming python3 is installed):

```sh
pip3 install -r requirements.txt
python src/main.py
```

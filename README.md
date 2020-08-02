# Speedbot

![Python application](https://github.com/cyclowns/speedbot/workflows/Python%20application/badge.svg) ![codecov](https://codecov.io/gh/cyclowns/speedbot/branch/master/graph/badge.svg)

Basic discord bot utilizing the SRC API for the GUR speedrunning discord. In the future, this will be generalized to any SRC game

## Running

First, create a discord bot application.

Then create a file called `config.py` in the `src` directory with contents like this:

```python
BOT_TOKEN = "{your bot token here}"
```

You also probably wanna change the channel IDs in src/main.py to match up with whatever you're doing, I guess? I don't know who else would use this besides our discord, though.

Run these commands (assuming python3 and pip are installed and in your system PATH):

```sh
pip3 install -r requirements.txt
coverage run src/tests.py
```

If all the tests pass, you're good to run this command:

```sh
python src/main.py
```

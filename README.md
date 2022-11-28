# Telegram Duel Bot
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/Nikappa57/tg-duel-bot?style=for-the-badge) ![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Nikappa57/tg-duel-bot/python-telegram-bot?style=for-the-badge) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Nikappa57/tg-duel-bot?style=for-the-badge) ![GitHub](https://img.shields.io/github/license/Nikappa57/tg-duel-bot?style=for-the-badge)

A telegram bot that uses animated telegram emojis to compete in simple duels in groups. 

This bot uses my base 
[tg-bot-bootstrap](https://github.com/Nikappa57/tg-bot-bootstrap).
## Features
- all the basic features of [tg-bot-bootstrap](https://github.com/Nikappa57/tg-bot-bootstrap)
- dueling system
- reactions to animated emojis
- group settings
- group and global stats

## How to use
#### Config
1. add the bot to a group
2. use `/settings` to open group settings privately
#### Reaction
1. use `/addreaction (level) (text`
    
    `level = 1` the user makes the minimum of points
    `level = 2` the user makes the most
2. use `/reaction` to manage the added reactions
#### Stats
1. use `/stats` to see the group stats
2. use `/globalstats` to see the global stats or use `inline_mode`
#### Duel
1. use `/duel` to ask in general to be challenged
2. use `/duel @username` or `reply to a message` to challenge a particular person

## Installation

Clone this repo: 
```console
git clone https://github.com/Nikappa57/tg-duel-bot.git
```
Install requirements.
```console
pipenv install
pipenv shell
```

#### Setup
Create `.env` with your bot token 
```
TOKEN=yourtoken
```

Now you should be able to start your bot.
```console
python run.py
```

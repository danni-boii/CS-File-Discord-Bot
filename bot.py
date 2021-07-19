# coding=utf-8
# The file is created according to the following tutorial series:
# https://www.youtube.com/watch?v=nW8c7vT6Hl4

# This .py file includes the bot construct related and the basic functions
# Run this file to start the bot.

"""
    CS-File Discord bot
    Version Alpha 0.0.1
    TODO List:

--  > Gamerules
    > No join and leave mid-game
----> The bot should store the variables in json file according to the guild.id@channel.id (Trickly solved)
----> When game start. A text box will be sent to determine the identity of each person.    (Need to turn into private)
----> Everyone will know their identity first. Revealing each other’s clues and methods.
----> Special identity messages. 
----> The murderer select what card he want to pick as the answer. 
----> Accomplice and FS will know what murderer choose as the answer
----> The FS will then arrange the order of hints and try to guide the investigator toward the correct answer. 
    > Day time message box
----> Investigators can always browse each other’s clue and method by a command. 
    > At day time, everyone with a police badge can try to report a set and clue and method as the answer, and the FS / System will then tell the world if the answer is correct. (Not done by the bot now)
    > !!! During night time, draw and do the events card (Not done by the bot now)
    > If all the investigator ran out out police badge, the murderer team wins. (Not done by the bot now)
    > If the investigators pointed out the correct answers, but the murderer pointed out the correct witness, the murderer team wins. (Not done by the bot now)
----> Game end data wipe
    > Permission check for game master 
"""


import discord
import os
import json
from discord.ext import commands

# Load the setting.json file
with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

def get_lang(bot, message):
    with open('defaultLanguage.json', 'r') as f:
        lang = json.load(f)
    return lang[str(message.guild.id)]
    

intents = discord.Intents.default() # Allow fetching member list easier
intents.members = True

bot = commands.Bot(command_prefix = get_prefix, intents = intents)

###########################################
#                Bot Event                #
###########################################

@bot.event
async def on_ready():
    print('Bot is ready. Hello World.')

@bot.event
async def on_guild_join(guild):
    # Set a default prefix for the discord channel.
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ".CSF"

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
        
    print(f'CS-File has joined {guild.name} @ {guild.id}')
    
    #Print an easy help guide
    
    

    ############


@bot.event
async def on_guild_remove(guild):
    # Remove the prefix value for this discord channel.
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
        
    print(f'CS-File has been removed from {guild.name} @ {guild.id}')
    ############


###########################################
#              Bot Command                #
###########################################

@bot.command(name = 'changePrefix')
async def _changePrefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'The prefix for the bot has changed to [{prefix}]')
    await ctx.send(f'以後請輸入 [{prefix}] 前綴以使用指令')

@bot.command(name = 'load')
async def _load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(F'Extension *{extension}* loaded.')
    print('Cog file ',extension, ' loaded')

@bot.command(name = 'unload')
async def _unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(F'Extension *{extension}* unloaded.')
    print('Cog file ',extension, ' unloaded')

@bot.command(name = 'reload')
async def _reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(F'Extension *{extension}* reloaded.')
    print('Cog file ',extension, ' reloaded')

# To load all the cogs(extension) for this bot
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    bot.run(jdata['TOKEN'])

# coding=utf-8
import discord
import json
import random
from discord.ext import commands

# Store the clues card info
class Card:
    """
        This class is only for data generation

        Args:
            name_en,
            name_tw,
            url
    """
    def __init__(self, name_en, name_tw = '', url = ''):
        
        self.name_en = name_en
        self.name_tw = name_tw
        self.url = url

class CluesList:
    """Stores all the clues card info"""
    clueslist = []
    def __init__(self):
        with open('cards.json', 'r', encoding='utf8') as jfile:
            self.jdata = json.load(jfile)
            self.clueslist = self.jdata['Clues']
    def get(self):
        return self.clueslist.copy()
    def getBGurl(self):
        """Return the card background URL"""
        return self.jdata['CluesMethods-merge-BG']
    def get_singleBGurl(self):
        return self.jdata['Clues-BG']

class MethodList:
    """Stores all the method card info, btw 'weapon' means 'method' for legacy reason."""
    weaponslist = []
    def __init__(self):
        with open('cards.json', 'r', encoding='utf8') as jfile:
            self.jdata = json.load(jfile)
            self.weaponslist = self.jdata['Weapons']
    def get(self):
        return self.weaponslist.copy()
    def getBGurl(self):
        return self.jdata['CluesMethods-merge-BG']
    def get_singleBGurl(self):
        return self.jdata['Methods-BG']

class EventList:
    """Stores all the event card info."""
    eventList = []
    def __init__(self):
        with open('event_cards.json', 'r', encoding='utf8') as jfile:
            self.jdata = json.load(jfile)
            self.eventList = self.jdata['events']
    def get(self):
        return self.eventList.copy()
    def getBGurl(self):
        return self.jdata['event-BGurl']
        
class UtilList:
    """Stores all the utility's card info"""
    def __init__(self):
        with open('cards_options.json', 'r', encoding='utf8') as jfile:
            self.jdata = json.load(jfile)
            self.hintslist : list = self.jdata['Hints']
            self.locCard : dict = self.jdata['locationOC']
            self.codCard : dict = self.jdata['CauseOfDeath']
    def getlocCard(self):
        return self.locCard.copy()
    def getcodCard(self):
        return self.codCard.copy()
    def gethintslist(self):
        return self.hintslist.copy()
    def hintBG(self):
        return self.jdata['Hints-BG-url']
    def codBG(self):
        return self.codCard['url']
    def locBG(self):
        return self.locCard['url']

class CardData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('[CardData] module loaded.')

    # Commands
    @commands.command(name = 'cluesList')
    async def _cluesList(self, ctx):
        """Return a whole clues list for the game 

        Should be used only for debug"""
        clueslist = CluesList().get()
        for every_card in clueslist:
            output_string = '> ' + every_card['name_en']
            await ctx.send(output_string)

    @commands.command(name = 'weaponsList')
    async def _weaponsList(self, ctx):
        """Return a whole weapon list for the game 

        Should be used only for debug"""
        weaponslist = MethodList().get()
        for every_card in weaponslist:
            output_string = '> ' + every_card['name_en']
            await ctx.send(output_string)
            
    @commands.command(name = "whoissuperman", aliases=["superman"])
    async def _whoissuperman(self, ctx):
        wid = random.randint(300,1000)
        hei = random.randint(300,1000)
        url = 'https://place-puppy.com/'+str(wid)+'x'+str(hei)
        embed=discord.Embed(title="I am Superman", description="A!", color=0xff0000)
        embed.set_image(url = url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CardData(bot))
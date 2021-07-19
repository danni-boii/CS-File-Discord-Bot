# coding=utf-8
import asyncio
import json
import random
import discord

from discord.ext import commands
from core import Roles
from cogs import CardData

# Load the setting.json file
with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)


class GameCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.playerlist = []
        self.player_rolelist = []
        self.volunteerlist = []
        self.gamecardtuple = []

        self.guildDict = {} 
        self.channelDict = {}
        self.dmchannellist = {}

        self.enable_witness = True
        self.clue_count = 4
        self.method_count = 4

        self.UtilObj = CardData.UtilList()
        self.EveObj = CardData.EventList()

    ########################
    # Events
    ########################

    @commands.Cog.listener()
    async def on_ready(self):
        print('[GameCommand] module loaded.')

    @commands.Cog.listener()    # Detects the emoji added on message
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        emoji = reaction.emoji
        if user.bot:    # Ignore a bot emoji reaction
            return

        cardtype = await self.cardType(message)

        if cardtype == 'locCard':
            now_page = self.dmchannellist[str(message.id)][3]
            if emoji == '⬅️':  # Last page
                # Get the calculated page.
                if (now_page <= 1):
                    page = '1'
                else:
                    page = str(now_page - 1)
                await self.sendFSCard('', 'locCard', page, message)
                now_page = int(page)
            elif emoji == '➡️':  # Next page
                # Get the calculated page.
                if (now_page >= 4):
                    page = '4'
                else:
                    page = str(now_page + 1)
                await self.sendFSCard('', 'locCard', page, message)
                now_page = int(page)
            else:   # Number emoji
                await self.fSselectLoc(message, self.emojiToInt(emoji), False)
        elif cardtype == 'locCard_V':
            if emoji == '❌':
                nowAtPage = self.dmchannellist[str(message.id)][3]
                ctx = await self.getDefaultCtx(message)
                await self.delOldMessageinCardlist(message)
                await self.sendFSCard(ctx, 'locCard', str(nowAtPage))
            elif emoji == '✅':
                await self.fSselectLoc(message, 0, True)
        elif cardtype == 'codCard':
            await self.fSselectCod(message, self.emojiToInt(emoji), False)
        elif cardtype == 'codCard_V':
            if emoji == '❌':
                ctx = await self.getDefaultCtx(message)
                await self.sendFSCard(ctx, 'codCard', '1', message)
                await self.delOldMessageinCardlist(message)
            elif emoji == '✅':
                await self.fSselectCod(message, 0, True)
        elif cardtype == 'hintCard':
            await self.fSselectHint(message, self.emojiToInt(emoji), False)
        elif cardtype == 'hintCard_V':
            if emoji == '❌':
                nowAtPage = self.dmchannellist[str(message.id)][3]
                ctx = await self.getDefaultCtx(message)
                await self.sendFSCard(ctx, 'hintCard', str(nowAtPage), message)
                await self.delOldMessageinCardlist(message)
            elif emoji == '✅':
                await self.fSselectHint(message, 0, True)
        elif cardtype == 'MD_M1':
            await self.murdererSelectClue(message, self.emojiToInt(emoji))
        elif cardtype == 'MD_M1_V':
            if emoji == '❌':        # The murderer wanted to select the evidence clue again
                ctx = await self.getDefaultCtx(message)
                await self.delOldMessageinCardlist(message)
                await self.sendMurdererCard(ctx, True, False)
            elif emoji == '✅':      # The murderer confirmed his clue selection
                await self.murdererSelectClue(message, 0, True)
        elif cardtype == 'MD_M2':
            await self.murdererSelectMethod(message, self.emojiToInt(emoji))
        elif cardtype == 'MD_M2_V':
            if emoji == '❌':        # The murderer wanted to select the evidence clue again
                ctx = await self.getDefaultCtx(message)
                await self.delOldMessageinCardlist(message)
                await self.sendMurdererCard(ctx, False, True)
            elif emoji == '✅':      # The murderer confirmed his method of operation selection
                await self.murdererSelectMethod(message, 0, True)

    ###
    # Commands
    ###

    @commands.command(name='startNewGame', aliases=['start', 'startnewgame'])
    async def _startNewGame(self, ctx):
        """
        _startNewGame The game host start a new game
        Initialize the parameters or do something related.

        Args:
            ctx ([discord.ext.commands.Context])
        """
        self.playerlist = []
        self.player_rolelist = []
        self.volunteerlist = []
        self.gamecardtuple = []
        self.dict = {}
        # For accessing the guild and channel info
        self.dict['defaultMessage'] = ctx.message
        self.dict['playerlist'] = self.playerlist
        self.dict['player_rolelist'] = self.player_rolelist
        self.dict['volunteerlist'] = self.volunteerlist
        self.dict['gamecardtuple'] = self.gamecardtuple
        self.channelDict[str(ctx.message.channel.id)] = self.dict
        self.guildDict[str(ctx.guild.id)] = self.channelDict
        self.dmchannellist = {}

        # Force the game starter to join the game
        thisplayer = Roles.Identity(ctx, ctx.message.author, 'Player')
        self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['playerlist'].append(thisplayer)
        embed = discord.Embed(title=f'User `{ctx.message.author.display_name}` wanted to start a game of [CS File].', description=f'Type in the command **[joinGame]** to join the event.\nIf all the users are ready. Type in the command **[gameContinue]** to start the game.', colour=int(
            jdata['Embed_Theme_Colour'], 16))  # ,color=Hex code
        embed.add_field(name=f'用戶 `{ctx.message.author.display_name}` 新建了一個 [犯罪現場] 的活動請求',
                        value=f'請輸入 **[joinGame]** 以加入遊戲\n當所有玩家都加入後，請輸入**[gameContinue]**指令繼續。')
        embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
        await ctx.send(embed=embed)

    @commands.command(name='endGame', aliases=['end', 'endgame'])
    async def _endGame(self, ctx):
        """
        _endGame Force to end the game whenever this command is received.

        Args:
            ctx ([discord.ext.commands.Context])
        """
        # Clear all the data in that specific guild text channel
        self.playerlist = []
        self.player_rolelist = []
        self.volunteerlist = []
        self.gamecardtuple = []
        self.dict = {}
        self.dict['playerlist'] = self.playerlist
        self.dict['player_rolelist'] = self.player_rolelist
        self.dict['volunteerlist'] = self.volunteerlist
        self.dict['gamecardtuple'] = self.gamecardtuple
        self.channelDict[str(ctx.message.channel.id)] = self.dict
        self.guildDict[str(ctx.guild.id)] = self.channelDict
        self.dmchannellist = {}

    @commands.command(name='joinGame', aliases=['join', 'joingame'])
    async def _joinGame(self, ctx):
        """ Join a started game """
        try:
            localPL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['playerlist']
            find_player = self.checkUserInIdList(
                ctx.message.author, localPL, ctx)
            if find_player in localPL:   # If the user has not joined yet, you can comment out this 2 line to test the game easier
                self.guildDict[str(ctx.guild.id)][str(
                    ctx.message.channel.id)]['playerlist'].remove(find_player)
            self.guildDict[str(ctx.guild.id)][str(ctx.message.channel.id)]['playerlist'].append(
                find_player)   # Add the message sender into the player list
            embed = discord.Embed(title=f'User `{ctx.message.author.display_name}` joined the [CS File] game.', description=f'There are currently {len(localPL)} users joined the game.', colour=int(
                jdata['Embed_Theme_Colour'], 16))
            embed.add_field(
                name=f'用戶 `{ctx.message.author.display_name}` 已經加入 [犯罪現場] ', value=f'現在已經有 {len(localPL)} 名玩家加入了')
            embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
            await ctx.send(embed=embed)
        except:
            await self.askForCommand(ctx)

    @commands.command(name='leaveGame', aliases=['leave', 'leavegame'])
    async def _leaveGame(self, ctx):

        """Leave a joined game if the player do not want to play it anymore"""
        try:
            localPL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['playerlist']
            localVL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['volunteerlist']
            find_player = self.checkUserInIdList(
                ctx.message.author, localPL, ctx)
            if(find_player not in localPL):
                # This user is being naughty, just ignore him/her
                return
            if(find_player in localPL):
                localPL.remove(find_player)
            if(find_player in localVL):
                localVL.remove(find_player)
            embed = discord.Embed(title=f'User `{ctx.message.author.display_name}` left the [CS File] game.', description=f'There are currently {len(localPL)} users in the game.', colour=int(
                jdata['Embed_Theme_Colour'], 16))
            embed.add_field(
                name=f'用戶 `{ctx.message.author.display_name}` 已經退出 [犯罪現場] ', value=f'現在剩下 {len(localPL)} 名玩家在遊戲中')
            embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
            await ctx.send(embed=embed)
        except:
            await self.askForCommand(ctx)

    @commands.command(name='playerList', aliases=['plist', 'playerlist'])
    async def _playerList(self, ctx):
        """Show the joined player list in the text channel."""
        # try:
        localPL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['playerlist']
        playerlist_string = ''
        player_counter = 1
        for person in localPL:
            playerlist_string += "> " + \
                str(player_counter) + '. ' + person.player.display_name + "\n"
            player_counter += 1
        embed = discord.Embed(title=f'Joined players\n已加入的玩家', description=f'{playerlist_string}', colour=int(
            jdata['Embed_Theme_Colour'], 16))
        embed.add_field(
            name='--------', value=f'Total of {len(localPL)} players joined.\n合共有 {len(localPL)} 名玩家。')
        embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
        await ctx.send(embed=embed)
        # except:
        # await self.askForCommand(ctx)

    @commands.command(name='volunteerFS', aliases=['volunteer', 'volunteerfs', 'joinv', 'vjoin'])
    async def _volunteerFS(self, ctx):
        """User can join the volunteer list.

        The game would pick a user in this list to become the forensic scientist"""
        try:
            localPL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['playerlist']
            localVL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['volunteerlist']
            find_player = self.checkUserInIdList(
                ctx.message.author, self.volunteerlist, ctx)
            if(find_player not in localPL):
                await self._joinGame(ctx)   # Force the player to join the game
            localVL.append(find_player)
            await self._volunteerList(ctx)
        except:
            await self.askForCommand(ctx)

    @commands.command(name='leaveVolunteer', aliases=['leavev', 'leavevolunteer'])
    async def _leaveVolunteer(self, ctx):
        """Allow the users to quit being a forensic scientist"""
        try:
            localVL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['volunteerlist']
            find_player = self.checkUserInIdList(
                ctx.message.author, localVL, ctx)
            if(find_player in localVL):
                localVL.remove(find_player)
            else:
                return
            embed = discord.Embed(title=f'You left the volunteer list.',
                                  description=f'You are no longer a volunteer for forensic scientist.', colour=int(jdata['Embed_Theme_Colour'], 16))
            embed.add_field(name='你離開了志願者清單', value=f'你不再自願成為鑑鉦專家。')
            embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
            await ctx.send(embed=embed)
        except:
            await self.askForCommand(ctx)

    @commands.command(name='volunteerList', aliases=['vlist', 'volunteerlist'])
    async def _volunteerList(self, ctx):
        """Show the volunteer list in the text channel."""
        try:
            localVL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['volunteerlist']
            volunteerlist_string = ''
            for person in localVL:
                volunteerlist_string += "> " + person.player.display_name + "\n"
            embed = discord.Embed(title=f'Volunteers for forensic scientist. \n鑑鉦專家志願者',
                                  description=f'{volunteerlist_string}', colour=int(jdata['Embed_Theme_Colour'], 16))
            embed.add_field(
                name='--------', value=f'Total of {len(localVL)} volunteers.\n合共有 {len(localVL)} 名志願者。')
            embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
            await ctx.send(embed=embed)
        except:
            await self.askForCommand(ctx)

    @commands.command(name='gameContinue', aliases=['continue', 'gamecontinue'])
    async def _gameContinue(self, ctx):
        """TODO: Check the user count, this game support 5 to 12 people (or even more)

        Assign different roles to players and distribute cards accordingly."""

        # try:
        # if(len(playerlist) < 4): return # Not enough player and ask for more player

        # Choose all the special roles before choosing the investagator #
        localPL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['playerlist']
        localVL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['volunteerlist']
        localPRL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']
        ori_playerlist = localPL.copy()  # just a backup
        # Add a FS role from volunteer list
        if(len(localVL) > 0):
            lucky_winner = random.choice(localVL)
        else:   # Add a FS role from player list
            lucky_winner = random.choice(localPL)
        localPRL.append(Roles.ForensicScientist(
            ctx, lucky_winner.player, 'Forensic Scientist'))
        localPL.remove(lucky_winner)
        # Randomly choose a player as the murderer
        lucky_murderer = random.choice(localPL)
        localPRL.append(Roles.Murderer(ctx, lucky_murderer.player, 'Murderer'))
        localPL.remove(lucky_murderer)
        # Accomplice only appears when there are more than 6 players
        if(len(ori_playerlist) >= 6):
            lucky_accomplice = random.choice(localPL)
            localPRL.append(Roles.Accomplice(
                ctx, lucky_accomplice.player, 'Accomplice'))
            localPL.remove(lucky_accomplice)
        # Witness only appears when there are more than 6 players and the role is enabled.
        if(len(ori_playerlist) >= 6 and self.enable_witness == True):
            lucky_witness = random.choice(localPL)
            localPRL.append(Roles.Witness(
                ctx, lucky_witness.player, 'Witness'))
            localPL.remove(lucky_witness)
        # The others are all normal Investigator
        for person in localPL:
            localPRL.append(Roles.Investigator(
                ctx, person.player, 'Investigator'))
        localPL = ori_playerlist.copy()
        # Shuffle the list, this affects the order to presentations.
        random.shuffle(localPRL)
        del ori_playerlist

        embed = discord.Embed(title=f'Identity messages has beed sent though all players private message.',
                              description=f'所有玩家的身份都已經由私訊發出。', colour=int(jdata['Embed_Theme_Colour'], 16))
        embed.add_field(name=f'The Forensic Scientist please wait for murderer to pick the evidence.',
                        value=f'請鑑證專家等待兇手選擇現埸證據。', inline=True)
        # maybe add an icon later
        embed.set_footer(
            text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
        embed.set_image(url=jdata['Icon'])
        await ctx.send(embed=embed)

        await self.distributeCard(ctx)

        # except:
        # await self.askForCommand(ctx)

    @commands.command(name='showAllCard', aliases=['allcard', 'cardall', 'acard'])
    async def _showAllCard(self, ctx, toPrivate='False'):
        """This function shows all the clues and methods card."""
        player_rolelist = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']
        try:
            for person in player_rolelist:
                # Send all player's card to the public channel
                await self._showCard(ctx, person.player, str(toPrivate))
        except:
            await self.askForCommand(ctx)

    @commands.command(name='showCard', aliases=['card'])
    async def _showCard(self, ctx, sp_user: discord.Member, toPrivate: str = 'True'):
        """This function shows the clues and methods card from a specific user."""
        try:
            if sp_user == None:
                return  # The sp_user does not exist in this server
            with open('cards.json', 'r', encoding='utf8') as jfile:
                cardBGurl = json.load(jfile)['CluesMethods-merge-BG']
            en = "name_en"
            tw = "name_tw"
            localPRL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['player_rolelist']

            if self.checkUserInIdList(sp_user, localPRL, ctx, True):
                person = self.checkUserInIdList(sp_user, localPRL, ctx)
            else:
                # find_user not playing the game.
                return
        except:  # Error
            await self.askForCommand(ctx)
            return
        if(person.identityIs('Forensic Scientist') or person.identityIs('Player')):
            # This user is the Forensic Scientist which have no clues and methods card
            pass
        else:
            # Send the distributed card to the player in either private chat or public text channel.
            #   Each clues are made up from the components:
            #       > name_en
            #       > name_tw
            #       > url
            embed = discord.Embed(title=f'[{person.getPlayerName()}] Clues 線索',
                                  description=f'----------', colour=int(jdata['Embed_Theme_Colour'], 16))
            field_count = 0
            for each_clue in person.getClueList():
                embed.add_field(
                    name=f'_{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed.add_field(name='\a', value='\a', inline=True)
            embed.add_field(
                name=f'[{person.getPlayerName()}] Methods of Operation 犯案手法', value=f'----------', inline=False)
            field_count = 0
            for each_method in person.getMethodList():
                embed.add_field(
                    name=f'_{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed.add_field(name='\a', value='\a', inline=True)
            embed.set_image(url=cardBGurl)
            # maybe add an icon later
            embed.set_footer(
                text=f"犯罪現場-CS File  --@{ctx.guild.name}.{ctx.message.channel}")

            if(toPrivate.lower() in ['private', 'xpublic', 'true', 'pm', 'dm', 'secret']):
                await ctx.message.author.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        pass

    @commands.command(name='gameRules', aliases=['rules', 'gameRule', 'rule', 'gamerule', 'gamerules'])
    async def _gameRules(self, ctx, Page=1, toPrivate=True):
        try:
            p = int(Page)
        except:
            p = 1
        embed = discord.Embed(title=f'[犯罪現場-CS File] - Rules 規則說明',
                              description=f'----------', colour=int(jdata['Embed_Theme_Colour'], 16))
        embed.set_thumbnail(url=jdata['Icon'])
        # maybe add an icon later
        embed.set_footer(text=f"犯罪現場-CS File     P.{p}")
        if p == 1:
            embed.add_field(name=f'__', value=f'******')
        elif p == 2:
            embed.add_field(name=f'__', value=f'******')
        elif p == 3:
            embed.add_field(name=f'__', value=f'******')
        elif p == 4:
            embed.add_field(name=f'__', value=f'******')

        if(toPrivate):
            await ctx.send(embed=embed)  # TODO: Send private message
        else:
            await ctx.send(embed=embed)

    @commands.command(name='drawRandomScenes', aliases=['drawScene', 'drawscene', 'drawScenes', 'drawscenes'])
    async def _drawRandomScenes(self, ctx):
        """Draw an scene tile on command. In this version, the tiles might repeat itself."""
        try:
            localPRL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['player_rolelist']
            ForensicScientist: Roles.ForensicScientist = self.findIdentity(
                localPRL, 'Forensic Scientist')
            if ctx.message.author == ForensicScientist.player:
                hintlist = self.UtilObj.gethintslist()
                await self.sendFSCard(ctx, 'hintCard', random.randint(1, len(hintlist)), None, True)
        except:
            return

    @commands.command(name="drawEvents", aliases=["drawevent", 'drawevents', 'drawrandomevent'])
    async def _drawEvents(self, ctx):
        """Draw an event tile on command. In this version, the tiles might repeat itself."""
        # try:
        localPRL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')
        if ctx.message.author == ForensicScientist.player:
            en = 'name_en'
            tw = 'name_tw'
            c_en = 'content_en'
            c_tw = 'content_tw'
            Eventlist = self.EveObj.get()
            draw_event = Eventlist[random.randint(0, len(Eventlist)-1)]
            embed = discord.Embed(title=f"The event tile you drew is `{draw_event[en]}`.", description=f"你抽到的事件卡是 `{draw_event[tw]}`", color=int(
                jdata['hintCard_Colour'], 16))
            embed.add_field(
                name='\a', value=f'{draw_event[c_en]}', inline=False)
            embed.add_field(
                name='\a', value=f'{draw_event[c_tw]}', inline=False)
            embed.set_footer(
                text=f'犯罪現場-CS File  @{ctx.guild.name}.{ctx.message.channel.name}')
            embed.set_image(url=draw_event['url'])
            embed.set_thumbnail(url=self.UtilObj.hintBG())
            await ForensicScientist.player.send(embed=embed)
        # except:
            # return

    @commands.command(name="revealAnswer", aliases=["ans", 'answer', 'reveal', 'revealanswer'])
    async def _revealAnswer(self, ctx):
        await self.notifyFSEvidence(None, ctx, True)

    @commands.command(name='testStart')
    async def _testStart(self, ctx):
        """This function is for test purpose only"""
        await self._startNewGame(ctx)
        for i in range(0, 7):    # Tester play as all the character
            self.guildDict[str(ctx.guild.id)][str(ctx.message.channel.id)]['playerlist'].append(
                Roles.Identity(ctx, ctx.message.author, 'Player'))
        await self._gameContinue(ctx)
        # Show the results to all the players
        await self._showAllCard(ctx, 'False')
        # await self._endGame(ctx)

    @commands.command(name='clearMessage', aliases=['clear', 'clr', 'cls'])
    async def _clearMessage(self, ctx):
        # Clear up the message by the bot in a text channel.
        def is_me(m):
            return m.author == self.bot.user

        deleted = await self.bot.purge_from(ctx.message.channel, limit=100, check=is_me)
        await self.bot.send_message(self.bot, 'Deleted {} message(s)'.format(len(deleted)))

    @commands.command(name='forceJoin', aliases=['forcejoin', 'fj'])
    async def _forceJoin(self, ctx, args):
        """This function forces a member to join the game, please do not add any bot into the game or it would get stuck."""
        try:
            localPL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['playerlist']
            find_user = ctx.guild.get_member_named(args)
            if find_user != None:
                if(find_user.bot == True):
                    return
                thisplayer = self.checkUserInIdList(find_user, localPL, ctx)
                # If the user has not joined yet, you can comment out this 2 line to test the game easier
                if(thisplayer in localPL):
                    localPL.remove(thisplayer)
                # Add the message sender into the player list
                localPL.append(thisplayer)
                embed = discord.Embed(title=f'User `{find_user.display_name}` joined the [CS File] game.', description=f'There are currently {len(localPL)} users joined the game.', colour=int(
                    jdata['Embed_Theme_Colour'], 16))
                embed.add_field(
                    name=f'用戶 `{find_user.display_name}` 已經加入 [犯罪現場] ', value=f'現在已經有 {len(localPL)} 名玩家加入了')
                # maybe add an icon later
                embed.set_footer(text="犯罪現場-CS File")
                await ctx.send(embed=embed)
                return
            print('Person not found')
        except:
            await self.askForCommand(ctx)

    ###
    # Non command functions
    ###

    async def sendIdentityMessage(self, ctx):
        """This function sends the identity message for each player privately."""
        en = "en"
        tw = "tw"
        player_rolelist = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']
        for person in player_rolelist:
            # Send message
            # To make sure not to mistaken the data from other channel or servers
            if(person.guildId == ctx.guild.id and person.textChannelId == ctx.message.channel):
                if(person.in_murderer_team):
                    embed = discord.Embed(title=f'You have been choosen as [{person.identity}]', description=f'{person.roles_guide[en]}', colour=int(
                        jdata['Murderer_Team_Colour'], 16))
                    embed.add_field(
                        name=f'你已經被選中成為 [{person.identity_tw}]', value=f'{person.roles_guide[tw]}', inline=True)
                    # maybe add an icon later
                    embed.set_footer(
                        text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
                    embed.set_image(url=person.url)
                    await person.player.send(embed=embed)
                else:   # In investigator team
                    embed = discord.Embed(title=f'You have been choosen as [{person.identity}]', description=f'{person.roles_guide[en]}', colour=int(
                        jdata['Investigator_Team_Colour'], 16))
                    embed.add_field(
                        name=f'你已經被選中成為 [{person.identity_tw}]', value=f'{person.roles_guide[tw]}', inline=True)
                    # maybe add an icon later
                    embed.set_footer(
                        text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
                    embed.set_image(url=person.url)
                    await person.player.send(embed=embed)

        # Tell the Accomplice and the murderer who's his teammate
        try:  # For identity thats not necessarily exist
            Accomplice_player: Roles.Accomplice = self.findIdentity(
                player_rolelist, 'Accomplice')
            Murderer_player: Roles.Murderer = self.findIdentity(
                player_rolelist, 'Murderer')
            embed = discord.Embed(title=f'The `Murderer` in this game is [{Murderer_player.getPlayerName()}]',
                                  description=f'As the Accomplice, you win if the Murderer gets away with the crime.', colour=int(jdata['Murderer_Team_Colour'], 16))
            embed.add_field(name=f'本場遊戲的 `兇手` 是 [{Murderer_player.getPlayerName()}]',
                            value=f'你是兇手的同黨，當兇手逍遙法外時，你亦一同勝出遊戲。', inline=True)
            # maybe add an icon later
            embed.set_footer(
                text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
            embed.set_image(url=Murderer_player.url)

            embed2 = discord.Embed(title=f'The `Accomplice` in this game is [{Accomplice_player.getPlayerName()}]',
                                   description=f'Try to cooperate with the accomplice to get away with the crime.', colour=int(jdata['Murderer_Team_Colour'], 16))
            embed2.add_field(
                name=f'本場遊戲的 `幫兇` 是 [{Accomplice_player.getPlayerName()}]', value=f'身為兇手，請你與幫兇合作以擺脫嫌疑。', inline=True)
            # maybe add an icon later
            embed2.set_footer(
                text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
            embed2.set_image(url=Accomplice_player.url)
            await Accomplice_player.player.send(embed=embed)
            await Murderer_player.player.send(embed=embed2)

            # Tell the witness whos the culprit
            Witness_player: Roles.Witness = self.findIdentity(
                player_rolelist, 'Witness')
            shufflelist = [Accomplice_player, Murderer_player]
            random.shuffle(shufflelist)
            embed3 = discord.Embed(title=f'The `culprits` in this game are [{shufflelist[0].getPlayerName()}] and [{shufflelist[1].getPlayerName()}]',
                                   description=f'If the Murderer is arrested but can identify the Witness, the Witness is considered to be killed, allowing the Murderer team to get away and win the game. Please be careful.', colour=int(jdata['Murderer_Team_Colour'], 16))
            embed3.add_field(name=f'本場遊戲的 `嫌疑人` 是 [{shufflelist[0].getPlayerName()}] and [{shufflelist[1].getPlayerName()}]',
                             value=f'如兇手被逮捕，只要他成功找出目擊者，目擊者即遭滅口。兇手一伙此時會趁亂逃走，逍遙法外，請多加留意。', inline=True)
            # maybe add an icon later
            embed3.set_footer(
                text=f"犯罪現場-CS File @{ctx.guild.name}.{ctx.message.channel.name}")
            embed3.set_image(url=Witness_player.curpitimg)
            await Witness_player.player.send(embed=embed3)
        except:
            pass

        if True:
            await self.sendMurdererCard(ctx)
            await self.randomTilesToFS(ctx)

    async def distributeCard(self, ctx):
        """To distribute clues and methods for each player"""
        player_rolelist = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']

        clues_list = CardData.CluesList().get()
        method_list = CardData.MethodList().get()
        random.shuffle(clues_list)
        random.shuffle(method_list)

        for person in player_rolelist:
            if(person.guildId == ctx.guild.id and person.textChannelId == ctx.message.channel):
                if(person.identityIs('Forensic Scientist')):
                    continue
                else:
                    # Distribute clue_count clues to a player
                    for i in range(0, self.clue_count):
                        # increase the randomness
                        choose_clue = random.choice(clues_list)
                        person.addClue(choose_clue)
                        clues_list.remove(choose_clue)
                    # Distribute method_count methods to a player
                    for i in range(0, self.method_count):
                        choose_method = random.choice(
                            method_list)  # increase the randomness
                        person.addMethod(choose_method)
                        method_list.remove(choose_method)
        await self._showAllCard(ctx)
        await self.sendIdentityMessage(ctx)

    @commands.command(name='testCard')  # This command is only for test purpose
    async def sendFSCard(self, ctx, cardtype: str = 'locCard', page: str = '1', modify_message: discord.message = None, toPrivate=True):
        """
        Set the behaviour of the enviroment card picking. And show the card on screen

        `[read_message_history] permission is required.`
        """
        if(cardtype not in ['locCard', 'hintCard', 'codCard']):  # To prevent stupid error
            cardtype = 'locCard'

        # Create the on screen output words and the presets
        message_string = ""
        num_counter = 0
        if modify_message != None:
            MM_dl = self.dmchannellist[str(modify_message.id)]
            local_PRL = self.guildDict[str(MM_dl[0].id)][str(
                MM_dl[1].id)]['player_rolelist']
            guildname = MM_dl[0].name
            channelname = MM_dl[1].name
        else:
            local_PRL = self.guildDict[str(ctx.guild.id)][str(
                ctx.message.channel.id)]['player_rolelist']
            guildname = ctx.guild.name
            channelname = ctx.message.channel.name
            MM_dl = None

        # Create the embed object according to card type
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
        if(cardtype == 'locCard'):  # The card is 'location of crime'
            string_en = self.UtilObj.getlocCard()['string_en']
            string_tw = self.UtilObj.getlocCard()['string_tw']
            image = self.UtilObj.getlocCard()[str(page + 'url')]
            footer = f"犯罪現場-CS File     P.{page}/4"
            for every_location in self.UtilObj.getlocCard()[page]:
                message_string += "> " + \
                    emojis[num_counter] + "   " + every_location + "\n"
                num_counter += 1

        elif(cardtype == 'codCard'):    # The card is 'cause of death'
            string_en = self.UtilObj.getcodCard()['string_en']
            string_tw = self.UtilObj.getcodCard()['string_tw']
            image = self.UtilObj.getcodCard()['url']
            footer = f"犯罪現場-CS File     P.{page}/1"
            for every_location in self.UtilObj.getcodCard()['content']:
                message_string += "> " + \
                    emojis[num_counter] + "   " + every_location + "\n"
                num_counter += 1
        else:                       # The card is a 'hints' type card
            hintlist = self.UtilObj.gethintslist()
            string_en = hintlist[int(page)-1]['string_en']
            string_tw = hintlist[int(page)-1]['string_tw']
            image = hintlist[int(page)-1]['url']
            footer = f"犯罪現場-CS File     NO.{page}/{len(hintlist)}"
            for every_location in hintlist[int(page)-1]['content']:
                message_string += "> " + \
                    emojis[num_counter] + "   " + every_location + "\n"
                num_counter += 1

        embed = discord.Embed(title=f'Please select the [{string_en}] \n(Click the referred emoji)', description=f'請選擇 [{string_tw}] (按下相應的表情符號)', colour=int(
            jdata[str(cardtype+'_Colour')], 16))  # ,color=Hex code
        embed.add_field(
            name=f"@{guildname}.{channelname}\n-------", value=f"{message_string}")
        embed.set_image(url=image)
        embed.set_footer(text=footer)  # maybe add an icon later

        # Modify the message if it is called by on_reaction_add event
        FS_player: Roles.ForensicScientist = self.findIdentity(
            local_PRL, 'Forensic Scientist')

        if(modify_message != None and ctx == ''):
            new_info_tuple = (MM_dl[0], MM_dl[1], cardtype, int(page))
            message = modify_message
            # await message.edit(embed = embed)
            del MM_dl
            await message.delete()
        else:   # Else, send new message
            new_info_tuple = (ctx.guild, ctx.message.channel,
                              cardtype, int(page))

        message = await FS_player.player.send(embed=embed)
        if(cardtype == 'locCard'):
            emojis.insert(0, '⬅️')
            emojis.append('➡️')
        for emoji in emojis:
            await message.add_reaction(emoji)
        self.dmchannellist[str(message.id)] = new_info_tuple
        #   An environment card message would be stored in the dmchannellist in the format of
        #   ( referred_guild, referred_channel, cardtype, page )

    @commands.command(name="testMD")
    async def sendMurdererCard(self, ctx, sendClues=True, sendMethods=True):
        """
        This function send a private message for the murderer card pick

        ### Parameters
        -----
        `sendClues` : When set to true, send the clues card privately to the murderer
        `sendMethods`: When set to true, send the methods card privately to the murderer
        """
        # Variables define
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                  '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        localPRL = self.guildDict[str(ctx.guild.id)][str(
            ctx.message.channel.id)]['player_rolelist']
        Murderer = self.findIdentity(localPRL, 'Murderer')
        field_count = 0
        en = "name_en"
        tw = "name_tw"

        # Embed message build
        embed = discord.Embed(title="Please Select 1 'Clue' as the evidence.",
                              description="請選擇 '一種線索' 作為證物。", color=int(jdata['Murderer_Team_Colour'], 16))
        for each_clue in Murderer.getClueList():
            embed.add_field(name=f'{emojis[field_count]} _{each_clue[en]}_',
                            value=f'***{each_clue[tw]}***', inline=True)
            field_count += 1
            if(field_count % 2 == 0):
                # Line break, work as <br>
                embed.add_field(name='\a', value='\a', inline=True)
        embed.add_field(name=f'Click the emojis below to select the clue.',
                        value=f'點擊下方的表情符號以選擇證物。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{ctx.guild.name}.{ctx.message.channel.name}')
        embed.set_image(url=CardData.CluesList().get_singleBGurl())
        embed.set_thumbnail(url=jdata['Evil_face'])

        field_count = 0
        embed2 = discord.Embed(title="Please Select 1 'Method of Operation' as the evidence.",
                               description="請選擇 '一種作案工具' 作為證物。", color=int(jdata['Murderer_Team_Colour'], 16))
        for each_method in Murderer.getMethodList():
            embed2.add_field(name=f'{emojis[field_count]} _{each_method[en]}_',
                             value=f'***{each_method[tw]}***', inline=True)
            field_count += 1
            if(field_count % 2 == 0):
                # Line break, work as <br>
                embed2.add_field(name='\a', value='\a', inline=True)
        embed2.add_field(name=f'Click the emojis below to select the method of operation.',
                         value=f'點擊下方的表情符號以選擇作案工具。', inline=False)
        embed2.set_footer(
            text=f'犯罪現場-CS File  @{ctx.guild.name}.{ctx.message.channel.name}')
        embed2.set_image(url=CardData.MethodList().get_singleBGurl())
        embed2.set_thumbnail(url=jdata['Evil_face'])

        if sendClues:
            MD_message1 = await Murderer.player.send(embed=embed)
            for i in range(0, self.clue_count):     # Add reactions(emojis) into the message
                asyncio.create_task(MD_message1.add_reaction(emojis[i]))
            new_info_tuple = (ctx.guild, ctx.message.channel, 'MD_M1', 0)
            # Add the message into the local memoery dictionary for storage
            self.dmchannellist[str(MD_message1.id)] = new_info_tuple
        if sendMethods:
            MD_message2 = await Murderer.player.send(embed=embed2)
            for i in range(0, self.method_count):   # Add reactions(emojis) into the message
                asyncio.create_task(MD_message2.add_reaction(emojis[i]))
            new_info_tuple = (ctx.guild, ctx.message.channel, 'MD_M2', 0)
            # Add the message into the local memoery dictionary for storage
            self.dmchannellist[str(MD_message2.id)] = new_info_tuple

    async def murdererSelectClue(self, MM_message, clue_number: int, confirmed=False):
        """This function reacts to the murderer clue card picks

        This function always call notifyAccompliceEvidence() when possible \\
        to notice Accomplice the murderer's evidence pick automatically.
        """
        if clue_number == -1:  # User add an emoji irreleavent
            return  # Diu this player is on9
        # Variables
        en = "name_en"
        tw = "name_tw"
        field_count = 0
        localDM = self.dmchannellist[str(MM_message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        Murderer: Roles.Murderer = self.findIdentity(localPRL, 'Murderer')
        if not confirmed:
            emojis = ['❌', '✅']
            new_info_tuple = (localDM[0], localDM[1], 'MD_M1_V', clue_number)
            selected_clue = Murderer.getClueList(
            )[clue_number - 1]  # This is the card picked
        else:
            emojis = []
            new_info_tuple = (localDM[0], localDM[1], 'MD_M1_C', localDM[3])
            selected_clue = Murderer.getClueList(
            )[localDM[3] - 1]  # This is the card picked
            Murderer.chosenClue = selected_clue
            try:
                await self.notifyAccompliceEvidence(MM_message)
            except:
                pass

        # Delete the old message
        await self.delOldMessageinCardlist(MM_message)

        # Embed message build
        embed = discord.Embed(title=f"You have picked ` {selected_clue[en]} ` as the clue evidence.",
                              description=f"你選擇了 ` {selected_clue[tw]} ` 作為線索證物。", color=int(jdata['Murderer_Team_Colour'], 16))
        for each_clue in Murderer.getClueList():
            if each_clue[en] == selected_clue[en]:
                embed.add_field(
                    name=f'✅ _{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
            else:
                embed.add_field(
                    name=f'_{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
            field_count += 1
            if(field_count % 2 == 0):
                # Line break, work as <br>
                embed.add_field(name='\a', value='\a', inline=True)
        if not confirmed:
            embed.add_field(name=f'Click the emojis below to confirm or cancel the selection.',
                            value=f'點擊下方的表情符號以確定或重新選擇。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=selected_clue['url'])
        embed.set_thumbnail(url=jdata['Evil_face'])

        # Send the DM and add the emojis
        MD_message1 = await Murderer.player.send(embed=embed)
        for emoji in emojis:
            asyncio.create_task(MD_message1.add_reaction(emoji))

        self.dmchannellist[str(MD_message1.id)] = new_info_tuple

    async def murdererSelectMethod(self, MM_message, method_number: int, confirmed=False):
        """This function reacts to the murderer method card picks

        This function always call notifyAccompliceEvidence() when possible \\
        to notice Accomplice the murderer's evidence pick automatically.
        """
        if method_number == -1:  # User add an emoji irreleavent
            return  # Diu this player is on9
        # Variables
        en = "name_en"
        tw = "name_tw"
        field_count = 0
        localDM = self.dmchannellist[str(MM_message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        Murderer: Roles.Murderer = self.findIdentity(localPRL, 'Murderer')
        if not confirmed:
            emojis = ['❌', '✅']
            new_info_tuple = (localDM[0], localDM[1], 'MD_M2_V', method_number)
            selected_method = Murderer.getMethodList(
            )[method_number - 1]  # This is the card picked
        else:
            emojis = []
            new_info_tuple = (localDM[0], localDM[1], 'MD_M2_C', localDM[3])
            selected_method = Murderer.getMethodList(
            )[localDM[3] - 1]  # This is the card picked
            Murderer.chosenWeapon = selected_method
            try:  # Accomplice may not exact, may cause some issue
                # I dont want to await the task
                await self.notifyAccompliceEvidence(MM_message)
            except:
                pass

        # Delete the old message
        await self.delOldMessageinCardlist(MM_message)

        # Embed message build
        embed = discord.Embed(title=f"You have picked ` {selected_method[en]} ` as the method evidence.",
                              description=f"你選擇了 ` {selected_method[tw]} ` 作為作案證物。", color=int(jdata['Murderer_Team_Colour'], 16))
        for each_method in Murderer.getMethodList():
            if each_method[en] == selected_method[en]:
                embed.add_field(
                    name=f'✅ _{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
            else:
                embed.add_field(
                    name=f'_{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
            field_count += 1
            if(field_count % 2 == 0):
                # Line break, work as <br>
                embed.add_field(name='\a', value='\a', inline=True)
        if not confirmed:
            embed.add_field(name=f'Click the emojis below to confirm or cancel the selection.',
                            value=f'點擊下方的表情符號以確定或重新選擇。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=selected_method['url'])
        embed.set_thumbnail(url=jdata['Evil_face'])

        # Send the DM and add the emojis
        MD_message2 = await Murderer.player.send(embed=embed)
        for emoji in emojis:
            asyncio.create_task(MD_message2.add_reaction(emoji))

        self.dmchannellist[str(MD_message2.id)] = new_info_tuple

    async def fSselectLoc(self, message: discord.Message, select_loc_num: int, confirmed=False):
        """This function reacts to the Forensic Scientist location card picks"""
        if select_loc_num == -1:  # User add an emoji irreleavent
            return  # Diu this player is on9
        # Variables
        localDM = self.dmchannellist[str(message.id)]
        locpage = localDM[3]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        LCardlist = self.UtilObj.getlocCard()
        selected_loc_url = LCardlist[str(locpage) + 'url']
        embed_field_string = ""
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')

        if not confirmed:
            emojis = ['❌', '✅']
            new_info_tuple = (localDM[0], localDM[1],
                              'locCard_V', locpage, select_loc_num)
            selected_loc = LCardlist[str(locpage)][select_loc_num-1]
        else:
            emojis = []
            importance = 0  # Not implemented yet
            new_info_tuple = (localDM[0], localDM[1],
                              'locCard_C', localDM[3], localDM[4])
            selected_loc = LCardlist[str(localDM[3])][localDM[4]-1]
            ForensicScientist.locInfo = (
                selected_loc, importance, selected_loc_url, locpage)

        # Delete the old message
        await self.delOldMessageinCardlist(message)

        # Embed message build
        for location in LCardlist[str(locpage)]:
            if location == selected_loc:
                embed_field_string += ">  " + " ✅  " + location + "✓\n"
            else:
                embed_field_string += ">  " + " ❌  " + location + "\n"
        embed = discord.Embed(title=f"You have picked ` {selected_loc} ` as the location of crime.",
                              description=f"你選擇了 ` {selected_loc} ` 作為案發現場。", color=int(jdata['locCard_Colour'], 16))
        embed.add_field(name='\a', value=f'{embed_field_string}')
        if not confirmed:
            embed.add_field(name=f'Click the emojis below to confirm or cancel the selection.',
                            value=f'點擊下方的表情符號以確定或重新選擇。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=selected_loc_url)
        embed.set_thumbnail(url=ForensicScientist.url)

        # Send the DM and add the emojis
        FS_locMessage = await ForensicScientist.player.send(embed=embed)
        for emoji in emojis:
            asyncio.create_task(FS_locMessage.add_reaction(emoji))

        self.dmchannellist[str(FS_locMessage.id)] = new_info_tuple

        if(ForensicScientist.allCardConfirmed()):
            await self.notifyAllFShints(FS_locMessage)

    async def fSselectCod(self, message: discord.Message, select_cod_num: int, confirmed=False):
        """This function reacts to the Forensic Scientist cause of death card picks"""
        if select_cod_num == -1:  # User add an emoji irreleavent
            return  # Diu this player is on9
        # Variables
        en = "string_en"
        tw = "string_tw"
        localDM = self.dmchannellist[str(message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        codCard = self.UtilObj.getcodCard()
        codCard_url = codCard['url']
        embed_field_string = ""
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')

        if not confirmed:
            emojis = ['❌', '✅']
            new_info_tuple = (localDM[0], localDM[1],
                              'codCard_V', select_cod_num)
            selected_cod = codCard['content'][select_cod_num-1]
        else:
            emojis = []
            importance = 0  # Not implemented yet
            new_info_tuple = (localDM[0], localDM[1], 'codCard_C', localDM[3])
            selected_cod = codCard['content'][localDM[3]-1]
            ForensicScientist.codInfo = (selected_cod, importance)

        # Delete the old message
        await self.delOldMessageinCardlist(message)

        # Embed message build
        for reasons in codCard['content']:
            if reasons == selected_cod:
                embed_field_string += ">  " + " ✅  " + reasons + "✓\n"
            else:
                embed_field_string += ">  " + " ❌  " + reasons + "\n"
        embed = discord.Embed(title=f"You have picked ` {selected_cod} ` as the {codCard[en]}.", description=f"你選擇了 ` {selected_cod} ` 作為{codCard[tw]}。", color=int(
            jdata['codCard_Colour'], 16))
        embed.add_field(name='\a', value=f'{embed_field_string}')
        if not confirmed:
            embed.add_field(name=f'Click the emojis below to confirm or cancel the selection.',
                            value=f'點擊下方的表情符號以確定或重新選擇。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=codCard_url)
        embed.set_thumbnail(url=ForensicScientist.url)

        # Send the DM and add the emojis
        FS_codMessage = await ForensicScientist.player.send(embed=embed)
        for emoji in emojis:
            asyncio.create_task(FS_codMessage.add_reaction(emoji))

        self.dmchannellist[str(FS_codMessage.id)] = new_info_tuple

        if(ForensicScientist.allCardConfirmed()):
            await self.notifyAllFShints(FS_codMessage)

    async def fSselectHint(self, message: discord.Message, select_hint_num: int, confirmed=False):
        """This function reacts to the Forensic Scientist hints card picks"""
        if select_hint_num == -1:  # User add an emoji irreleavent
            return  # Diu this player is on9

        # Variables
        en = "string_en"
        tw = "string_tw"
        localDM = self.dmchannellist[str(message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        hintpage = localDM[3]
        HCardlist = self.UtilObj.gethintslist()
        HCard = HCardlist[hintpage-1]
        select_hint_url = HCard['url']
        embed_field_string = ""
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')

        if not confirmed:
            emojis = ['❌', '✅']
            new_info_tuple = (localDM[0], localDM[1],
                              'hintCard_V', hintpage, select_hint_num)
            select_hint = HCard['content'][select_hint_num-1]
        else:
            emojis = []
            importance = 0  # Not implemented yet
            new_info_tuple = (localDM[0], localDM[1],
                              'hintCard_C', localDM[3], localDM[4])
            select_hint = HCard['content'][localDM[4]-1]
            hintInfo_tuple = (select_hint, importance,
                              select_hint_url, hintpage)
            ForensicScientist.hintInfo.append(hintInfo_tuple)

        # Delete the old message
        await self.delOldMessageinCardlist(message)

        # Embed message build
        for options in HCard['content']:
            if options == select_hint:
                embed_field_string += ">  " + " ✅  " + options + "✓\n"
            else:
                embed_field_string += ">  " + " ❌  " + options + "\n"
        embed = discord.Embed(title=f"You have picked ` {select_hint} ` for {HCard[en]}.", description=f"你為 {HCard[tw]} 選擇了  ` {select_hint} ` 。", color=int(
            jdata['hintCard_Colour'], 16))
        embed.add_field(name='\a', value=f'{embed_field_string}')
        if not confirmed:
            embed.add_field(name=f'Click the emojis below to confirm or cancel the selection.',
                            value=f'點擊下方的表情符號以確定或重新選擇。', inline=False)
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=select_hint_url)
        embed.set_thumbnail(url=ForensicScientist.url)

        # Send the DM and add the emojis
        FS_hintMessage = await ForensicScientist.player.send(embed=embed)
        for emoji in emojis:
            asyncio.create_task(FS_hintMessage.add_reaction(emoji))

        self.dmchannellist[str(FS_hintMessage.id)] = new_info_tuple

        if(ForensicScientist.allCardConfirmed()):
            await self.notifyAllFShints(FS_hintMessage)

    async def notifyAccompliceEvidence(self, message):
        """This function notify the accomplice what are the evidence picked by the murderer

        This function also calls notifyFSEvidence() automatically when finished"""
        # Variables
        en = "name_en"
        tw = "name_tw"
        field_count = 0
        localDM = self.dmchannellist[str(message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        Murderer: Roles.Murderer = self.findIdentity(localPRL, 'Murderer')
        Accomplice: Roles.Accomplice = self.findIdentity(
            localPRL, 'Accomplice')
        selected_clue = Murderer.chosenClue
        selected_method = Murderer.chosenWeapon

        # Check if the murderer picked both the clue and method already
        if Murderer.chosenClue != None and Murderer.chosenWeapon != None:

            # Embed message build
            embed = discord.Embed(title=f"The murderer has picked ` {selected_clue[en]} ` as the clue evidence.",
                                  description=f"兇手選擇了 ` {selected_clue[tw]} ` 作為線索證物。", color=int(jdata['Murderer_Team_Colour'], 16))
            for each_clue in Murderer.getClueList():
                if each_clue[en] == selected_clue[en]:
                    embed.add_field(
                        name=f'✅ _{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
                else:
                    embed.add_field(
                        name=f'_{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed.add_field(name='\a', value='\a', inline=True)
            embed.set_footer(
                text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
            embed.set_image(url=selected_clue['url'])
            embed.set_thumbnail(url=jdata['Evil_face'])

            # Embed message build
            embed2 = discord.Embed(title=f"The murderer has picked ` {selected_method[en]} ` as the method evidence.",
                                   description=f"兇手選擇了 ` {selected_method[tw]} ` 作為作案證物。", color=int(jdata['Murderer_Team_Colour'], 16))
            for each_method in Murderer.getMethodList():
                if each_method[en] == selected_method[en]:
                    embed2.add_field(
                        name=f'✅ _{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
                else:
                    embed2.add_field(
                        name=f'_{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed2.add_field(name='\a', value='\a', inline=True)
            embed2.set_footer(
                text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
            embed2.set_image(url=selected_method['url'])
            embed2.set_thumbnail(url=jdata['Evil_face'])

            await Accomplice.player.send(embed=embed)
            await Accomplice.player.send(embed=embed2)

            await self.notifyFSEvidence(message)

    async def notifyFSEvidence(self, message, ctx=None, revealToPublic=False):
        """
        This function notify the Forensic Scientist what are the evidence picked by the murderer

        But when the @param `revealToPublic` is set to true, the message will send to the public chat
        """
        # Variables
        en = "name_en"
        tw = "name_tw"
        field_count = 0
        if not revealToPublic:
            localDM = self.dmchannellist[str(message.id)]
        else:
            localDM = [ctx.guild, ctx.message.channel]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        Murderer: Roles.Murderer = self.findIdentity(localPRL, 'Murderer')
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')
        selected_clue = Murderer.chosenClue
        selected_method = Murderer.chosenWeapon

        # Check if the murderer picked both the clue and method already
        if Murderer.chosenClue != None and Murderer.chosenWeapon != None:
            # Embed message build
            embed = discord.Embed(title=f"The murderer has picked ` {selected_clue[en]} ` as the clue evidence.",
                                  description=f"兇手選擇了 ` {selected_clue[tw]} ` 作為線索證物。", color=int(jdata['Investigator_Team_Colour'], 16))
            for each_clue in Murderer.getClueList():
                if each_clue[en] == selected_clue[en]:
                    embed.add_field(
                        name=f'✅ _{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
                else:
                    embed.add_field(
                        name=f'_{each_clue[en]}_', value=f'***{each_clue[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed.add_field(name='\a', value='\a', inline=True)
            embed.set_footer(
                text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
            embed.set_image(url=selected_clue['url'])
            embed.set_thumbnail(url=ForensicScientist.url)

            # Embed message build
            embed2 = discord.Embed(title=f"The murderer has picked ` {selected_method[en]} ` as the method evidence.",
                                   description=f"兇手選擇了 ` {selected_method[tw]} ` 作為作案證物。", color=int(jdata['Investigator_Team_Colour'], 16))
            for each_method in Murderer.getMethodList():
                if each_method[en] == selected_method[en]:
                    embed2.add_field(
                        name=f'✅ _{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
                else:
                    embed2.add_field(
                        name=f'_{each_method[en]}_', value=f'***{each_method[tw]}***', inline=True)
                field_count += 1
                if(field_count % 2 == 0):
                    # Line break, work as <br>
                    embed2.add_field(name='\a', value='\a', inline=True)
            embed2.set_footer(
                text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
            embed2.set_image(url=selected_method['url'])
            embed2.set_thumbnail(url=ForensicScientist.url)

            if not revealToPublic:
                await ForensicScientist.player.send(embed=embed)
                await ForensicScientist.player.send(embed=embed2)
            else:
                await ctx.send(embed=embed)
                await ctx.send(embed=embed2)

    async def notifyAllFShints(self, message):
        """This function tells everyone what the Forensic Scientist picked as the hints"""
        # Variables
        en = "string_en"
        tw = "string_tw"
        ctx = await self.getDefaultCtx(message)
        localDM = self.dmchannellist[str(message.id)]
        localPRL = self.guildDict[str(localDM[0].id)][str(
            localDM[1].id)]['player_rolelist']
        LCardlist = self.UtilObj.getlocCard()
        HCardlist = self.UtilObj.gethintslist()
        ForensicScientist: Roles.ForensicScientist = self.findIdentity(
            localPRL, 'Forensic Scientist')
        embed_field_string = ""
        selected_loc = ForensicScientist.locInfo
        selected_cod = ForensicScientist.codInfo
        selected_hintlist = ForensicScientist.hintInfo

        # Sending Location card
        #( selected_loc, importance, selected_loc_url, locpage )
        locpage = selected_loc[3]
        for location in LCardlist[str(locpage)]:
            if location == selected_loc[0]:
                embed_field_string += ">  " + " ✅  " + location + " ✓\n"
            else:
                embed_field_string += ">  " + " ❌  " + location + "\n"
        embed = discord.Embed(title=f"The Forensic Scientist thinks that ` {selected_loc[0]} ` is the location of crime.",
                              description=f"鑑證專家認為案發地點位於 ` {selected_loc[0]} ` 。", color=int(jdata['locCard_Colour'], 16))
        embed.add_field(name='\a', value=f'{embed_field_string}')
        embed.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed.set_image(url=selected_loc[2])
        embed.set_thumbnail(url=ForensicScientist.url)
        await ctx.send(embed=embed)

        # Sending cause of death card
        #( selected_cod, importance )
        embed_field_string = ""
        for reasons in self.UtilObj.getcodCard()['content']:
            if reasons == selected_cod[0]:
                embed_field_string += ">  " + " ✅  " + reasons + "✓\n"
            else:
                embed_field_string += ">  " + " ❌  " + reasons + "\n"

        embed2 = discord.Embed(title=f"The Forensic Scientist thinks that ` {selected_cod[0]} ` is the cause of death.",
                               description=f"鑑證專家認為死因是 ` {selected_cod[0]} ` 。", color=int(jdata['codCard_Colour'], 16))
        embed2.add_field(name='\a', value=f'{embed_field_string}')
        embed2.set_footer(
            text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
        embed2.set_image(url=selected_loc[2])
        embed2.set_thumbnail(url=ForensicScientist.url)
        await ctx.send(embed=embed2)

        # Sending all hints card
        #( select_hint, importance, select_hint_url, hintpage )
        for every_hint_tuple in selected_hintlist:
            embed_field_string = ""
            HCard = HCardlist[every_hint_tuple[3] - 1]
            hint = every_hint_tuple[0]
            url = every_hint_tuple[2]
            for hc in HCard['content']:
                if hc == hint:
                    embed_field_string += ">  " + " ✅  " + hc + "✓\n"
                else:
                    embed_field_string += ">  " + " ❌  " + hc + "\n"
            hintembed = discord.Embed(title=f"The Forensic Scientist thinks the {HCard[en]} is ` { hint } `.",
                                      description=f"鑑證專家認為{HCard[tw]}是 ` { hint } ` 。", color=int(jdata['hintCard_Colour'], 16))
            hintembed.add_field(name='\a', value=f'{embed_field_string}')
            hintembed.set_footer(
                text=f'犯罪現場-CS File  @{localDM[0].name}.{localDM[1].name}')
            hintembed.set_image(url=url)
            hintembed.set_thumbnail(url=ForensicScientist.url)
            await ctx.send(embed=hintembed)

    async def randomTilesToFS(self, ctx):
        await asyncio.sleep(1)  # Delay 1 second
        en = "name_en"
        tw = "name_tw"
        sendscenelist = []
        await self.sendFSCard(ctx, 'locCard')
        await self.sendFSCard(ctx, 'codCard')
        for i in range(0, 999):  # Randomly draw 4 scenes tile
            r = random.randint(1, len(self.UtilObj.gethintslist()))
            if i not in sendscenelist:
                sendscenelist.append(r)
            if len(sendscenelist) >= 4:
                break
        for i in sendscenelist:
            await self.sendFSCard(ctx, 'hintCard', str(i))

    async def cardType(self, message: discord.message):
        """
        ### Used to return the hints card type in stored in the bot dict
        -----
        ### Return value meanings:

        'locCard': the location card selection message

        'locCard_V': the location card selection verify message

        'locCard_C': the confirmed location card message

        'codCard': the cause of death card selection message

        'codCard_V': the cause of death card selection verify message

        'codCard_C': the confirmed cause of death card message

        'hintCard': the hint card selection message

        'hintCard_V': the hint card selection verify message

        'hintCard_C': the confirmed hint card message

        'MD_M1': the murderer clue selection message

        'MD_M1_V': the murderer clue selection verify message

        'MD_M1_C': the confirmed murderer clue message

        'MD_M2':  the murderer method of operation selection message

        'MD_M2_V': the murderer method of operation card selection verify message

        'MD_M2_C': the confirmed murderer method of operation message
        """
        try:
            cardtype: str = self.dmchannellist[str(message.id)][2]
            return cardtype
        except:
            return None

    async def askForCommand(self, ctx, needed_command='startNewGame'):
        """Show an error message in the text channel."""
        embed = discord.Embed(title=f'Command not working.', description=f'Type in the command **[{needed_command}]** before you use this command.', colour=int(
            jdata['Embed_Theme_Colour'], 16))  # ,color=Hex code
        embed.add_field(
            name=f'指令運行失敗。', value=f'請先輸入 **[{needed_command}]** 指令後，再輸入該指令。', inline=True)
        embed.set_footer(text="犯罪現場-CS File")  # maybe add an icon later
        await ctx.send(embed=embed)

    async def delOldMessageinCardlist(self, message):
        try:
            mid = message.id
            await message.delete()
            del self.dmchannellist[str(mid)]
        except:
            return

    async def getDefaultCtx(self, message):
        """This function can get the default ctx from a message easily."""
        locDML = self.dmchannellist[str(message.id)]
        defaultMessage = self.guildDict[str(
            locDML[0].id)][str(locDML[1].id)]['defaultMessage']
        ctx = await self.bot.get_context(defaultMessage)
        return ctx

    ###
    # Non async required functions
    ###

    def checkUserInIdList(self, user, Idlist, ctx='', returnBool=False):
        """Check if the user are already in the list, return the user_identity object if found"""
        for person in Idlist:
            if(person.player == user and person.guildId == ctx.guild.id and person.textChannelId == ctx.message.channel):
                if returnBool:
                    return True
                else:
                    return person
        if returnBool:
            return False
        else:
            return Roles.Identity(ctx, user, 'Player')

    def findIdentity(self, rolelist, looking_identity: str = ''):
        """Find the person with the exact identity and return its class object"""
        for IdClass in rolelist:
            if IdClass.identity == looking_identity:
                return IdClass
        return None  # On not found

    def emojiToInt(self, emoji):
        """
        emojiToInt This function converts the number emojis into an integer

        Args:
            emoji ([string])

        Returns:
            [int]
        """
        if emoji == '1️⃣':
            return 1
        elif emoji == '2️⃣':
            return 2
        elif emoji == '3️⃣':
            return 3
        elif emoji == '4️⃣':
            return 4
        elif emoji == '5️⃣':
            return 5
        elif emoji == '6️⃣':
            return 6
        elif emoji == '7️⃣':
            return 7
        elif emoji == '8️⃣':
            return 8
        elif emoji == '9️⃣':
            return 9
        elif emoji == '0️⃣':
            return 0
        elif emoji == '🔟':
            return 10
        elif emoji == '❌':
            return 888
        elif emoji == '✅':
            return 999
        else:
            return -1  # Unknown emoji case

# Cog Main function


def setup(bot):
    bot.add_cog(GameCommand(bot))

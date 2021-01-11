# -*- coding: utf-8 -*-

"""
Roles for CS File
~~~~~~~~~~~~~~~~~~~

Contains different identity of the game [CS File]

"""

import json

jdata = ''
with open('game_dialog.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class Identity:
    """A basic class for holding player's info
    
    There is one special case, if ones' identity is 'player'.
    
    Then his/her identity needs to be process in the GameCommand.py file.
    """

    def __init__(self, ctx, player, identity = ''):
        """Args:
        
            ctx : {discord object}
            
            player : {should be a discord.user object}
            
            identity (str, optional): {just a identifying string}. Defaults to ''.
        """
        self.player = player
        self.identity = identity
        self.clues_list = []
        self.weapon_list = []
        self.guildId = ctx.guild.id
        self.textChannelId = ctx.message.channel
    def identityIs(self, identity):
        return (identity is self.identity)
    def addClue(self, cluesCard):
        self.clues_list.append(cluesCard)
    def addMethod(self, weaponCard):
        self.weapon_list.append(weaponCard)
    def getClueList(self):
        return self.clues_list.copy()
    def getMethodList(self):
        return self.weapon_list.copy()
    def getPlayerName(self):
        return self.player.display_name

"""
    Identity list:
        'Forensic Scientist',
        'Investigator',
        'Witness',
        'Murderer',
        'Accomplice'
"""

class ForensicScientist(Identity):
    """ 鑑證專家 Forensic Scientist Class """
    identity_tw = jdata['roles_guide']['ForensicScientist']['id_tw']
    has_police_badge = False
    in_murderer_team = False
    roles_guide = jdata['roles_guide']['ForensicScientist']
    url = jdata['roles_guide']['ForensicScientist']['id_url']
    #   locInfo should stores in a format:
    #   > ( location_name(str), importance(int), location_referred_card_url(str), location_referred_card_inpage(int) )
    locInfo = ()
    #   codInfo should stores in a format:
    #   > ( causeofDeath_name(str), importance(int) )
    codInfo = ()
    #   list of hintscard dict
    #   hintInfo should stores in a format:
    #   > ( hints_name(str), importance(int), hints_referred_card_url(str), hints_referred_card_number(int) )
    hintInfo = []
    
    def allCardConfirmed(self):
        if len(self.locInfo) > 0 and len(self.codInfo) > 0 and len(self.hintInfo) >= 4:
            return True
        else:
            return False

class Investigator(Identity):           # 調查員
    """ 調查員 Investigator Class """
    identity_tw = jdata['roles_guide']['Investigator']['id_tw']
    has_police_badge = True
    in_murderer_team = False
    roles_guide = jdata['roles_guide']['Investigator']
    url = jdata['roles_guide']['Investigator']['id_url']

class Witness(Identity):                # 目擊者
    """ 目擊者 Witness Class """
    identity_tw = jdata['roles_guide']['Witness']['id_tw']
    has_police_badge = True
    in_murderer_team = False
    roles_guide = jdata['roles_guide']['Witness']
    url = jdata['roles_guide']['Witness']['id_url']
    curpitimg = jdata['roles_guide']['CurpitURL']

class Murderer(Identity):               # 兇手
    """ 兇手 Murderer Class"""
    identity_tw = jdata['roles_guide']['Murderer']['id_tw']
    has_police_badge = True
    in_murderer_team = True
    roles_guide = jdata['roles_guide']['Murderer']
    url = jdata['roles_guide']['Murderer']['id_url']
    chosenClue = None
    chosenWeapon = None

class Accomplice(Identity):             # 幫兇
    """ 幫兇 Accomplice Class """
    identity_tw = jdata['roles_guide']['Accomplice']['id_tw']
    has_police_badge = True
    in_murderer_team = True
    roles_guide = jdata['roles_guide']['Accomplice']
    url = jdata['roles_guide']['Accomplice']['id_url']

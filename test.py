from mpyq import mpyq
import json
from importlib import import_module
from sqlconnector import GameSQLConnector
import io
import sys
import re

regex = re.compile('[^a-zA-Z]')

sys.path.insert(0, 'protocols/')
import protocol67985 as protocol

relevent = ['Takedowns', 'Deaths', 'ExperienceContribution', 'Healing', 'HeroDamage',
    'MercCampCaptures',
    'SiegeDamage', 'StructureDamage', 'MinionDamage', 'SelfHealing',
    'DamageTaken', 'DamageSoaked']

filePath = './testreplays/Dragon Shire (56).StormReplay'

commandLineArgs = sys.argv[1:]

requestedPlayerName = '';
if len(commandLineArgs) == 1:
    requestedPlayerName = commandLineArgs[0]
    print("Looking for replays with player name " + requestedPlayerName)

class HeroPlayer:

    combatData = {}

    def __init__(self, hero, name, slot, id):
        self.hero = hero
        self.name = name
        self.slot = slot
        self.id = id
        self.team = 0
        
        self.takedowns = 0
        self.deaths = 0
        self.heroDamage = 0
        self.healing = 0
        self.siegeDamage = 0
        self.structureDamage = 0
        self.minionDamage = 0
        self.selfHealing = 0
        self.damageTaken = 0
        self.damageSoaked = 0
        self.result = ''
        self.experience = 0

    def printInformation(self):
        print(self.name + " played " + self.hero + " in slot " + str(self.slot))

# result, playerHero, playerTakedowns, playerDeaths, playerSiegeDamage, playerStructureDamage
# playerMinionDamage, playerSelfHeadling, playerDamageTaken, playerDamageSoaked

# this returns a generator, you need to iterate through it
def getTrackerEvents():
    trackerEventsStack = archive.read_file('replay.tracker.events')
    trackerEvents = protocol.decode_replay_tracker_events(trackerEventsStack)
    return trackerEvents

def getDetails():
    detailsStack = archive.read_file('replay.details')
    details = protocol.decode_replay_details(detailsStack)
    return details

def getTeams(detailsPlayerList, heroPlayer):
    alliedHeroList = []
    enemyHeroList = []
    for player in detailsPlayerList:
        if player['m_teamId'] == heroPlayer.team and player['m_toon']['m_id'] != heroPlayer.id:
            alliedHeroList.append(regex.sub('', player['m_hero']))
        if player['m_teamId'] != heroPlayer.team:
            enemyHeroList.append(regex.sub('', player['m_hero']))
    return { 'alliedHeroList': alliedHeroList, 'enemyHeroList': enemyHeroList }

#Open the archive
archive = mpyq.MPQArchive(filePath)

#Parse the header
header = protocol.decode_replay_header(archive.header['user_data_header']['content'])
build_number = header['m_version']['m_baseBuild']

# Get the actual protocol number
module_name = 'protocol{}'.format(build_number)
protocol = import_module(module_name)


trackerEvents = getTrackerEvents()
details = getDetails()

playerList = details['m_playerList']
 
mainPlayer = None

for player in playerList:
    if player['m_name'] == requestedPlayerName:
        print(requestedPlayerName + " found!")
        mainPlayer = HeroPlayer(player['m_hero'], player['m_name'], player['m_workingSetSlotId'],
            player['m_toon']['m_id'])
        mainPlayer.team = player['m_teamId']
        mainPlayer.printInformation()
        if player['m_result'] == 1:
            mainPlayer.result = 'W'
        elif player['m_result'] == 2:
            mainPlayer.result = 'L'

for tracker_event in trackerEvents:
    if tracker_event['_event'] == 'NNet.Replay.Tracker.SScoreResultEvent':
        scoreResult = tracker_event

if 'm_instanceList' in scoreResult:
    for item in scoreResult['m_instanceList']:
        itemName = item['m_name']
        if mainPlayer is not None:
            if itemName == 'Takedowns':
                mainPlayer.takedowns = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'Deaths':
                mainPlayer.deaths = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'SiegeDamage':
                mainPlayer.siegeDamage = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'StructureDamage':
                mainPlayer.structureDamage = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'MinionDamage':
                mainPlayer.minionDamage = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'Healing':
                mainPlayer.healing = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'HeroDamage':
                mainPlayer.heroDamage = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'DamageTaken':
                mainPlayer.damageTaken = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'DamageSoaked':
                mainPlayer.damageSoaked = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'SelfHealing':
                mainPlayer.selfHealing = item['m_values'][mainPlayer.slot][0]['m_value']
            if itemName == 'ExperienceContribution':
                mainPlayer.experience  = item['m_values'][mainPlayer.slot][0]['m_value']

if mainPlayer is not None:
    gameSQLConnector = GameSQLConnector()
    print(mainPlayer.takedowns)
    data_game = (mainPlayer.result, mainPlayer.hero, mainPlayer.takedowns, mainPlayer.deaths, 
        mainPlayer.heroDamage, mainPlayer.healing, mainPlayer.siegeDamage, 
        mainPlayer.structureDamage, mainPlayer.minionDamage, mainPlayer.selfHealing,
        mainPlayer.damageTaken, mainPlayer.damageSoaked, mainPlayer.experience)
    player_id = gameSQLConnector.getPlayerDatabaseID(mainPlayer.name, mainPlayer.id)
    entry_id = gameSQLConnector.addHeroData(data_game, player_id)

    teamList = getTeams(playerList, mainPlayer)
    gameSQLConnector.addAlliedHeroes(teamList['alliedHeroList'], entry_id, player_id)
    gameSQLConnector.addEnemyHeroes(teamList['enemyHeroList'], entry_id, player_id)
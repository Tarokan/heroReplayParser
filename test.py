import mpyq
import json
from importlib import import_module
from sqlconnector import GameSQLConnector
import sqlconnector
import io
import sys
import argparse
import os

sys.path.insert(0, './heroprotocol')

from hotsparser import *
import protocol67985 as protocol

commandLineArgs = sys.argv[1:]

def addPlayerData(replay, playerBattleTag):
    print(str(replay.replayInfo))
    print(replay.players)
    players = replay.players
    player = findPlayer(replay, playerBattleTag) # Player object
    playerSlot = player.id
    print("found player: " + playerBattleTag + " in slot " + str(playerSlot))
    
    heroPlayers = replay.heroList
    print(replay.heroList)
    heroPlayer = heroPlayers[playerSlot]
    heroPlayerStats = heroPlayer.generalStats
    basicData = (convertResult(player.gameResult), player.hero, 
                heroPlayerStats['Takedowns'], heroPlayerStats['Deaths'], heroPlayerStats['HeroDamage'],
                heroPlayerStats['Healing'], heroPlayerStats['SiegeDamage'], heroPlayerStats['StructureDamage'],
                heroPlayerStats['MinionDamage'], heroPlayerStats['SelfHealing'], heroPlayerStats['DamageTaken'],
                heroPlayerStats['DamageSoaked'], heroPlayerStats['ExperienceContribution'])
    
    gameSQLConnector = GameSQLConnector()
    entryid = gameSQLConnector.addHeroData(basicData, playerBattleTag)
    gameSQLConnector.addAlliedHeroes(getTeam(replay, playerBattleTag, True), entryid, playerBattleTag)
    gameSQLConnector.addEnemyHeroes(getTeam(replay, playerBattleTag, False), entryid, playerBattleTag)
    gameSQLConnector.addTalentChoices(getTalentChoices(replay, playerSlot), entryid, playerBattleTag)
    gameSQLConnector.addDateTime(replay.replayInfo.startTime, entryid, playerBattleTag)
    gameSQLConnector.addMap(replay.replayInfo.mapName, entryid, playerBattleTag)
    gameSQLConnector.addGameType(replay.replayInfo.gameType, entryid, playerBattleTag)
    print("Uploaded data succesfully!")
    
def convertResult(gameResult):
    if gameResult == 1: # win condition
        return 1
    if gameResult == 2: # loss condition
        return 2

def getTalentChoices(replay, playerSlot):
    talents = []
    for talent in replay.heroList[playerSlot].generalStats['pickedTalents']:
        talents.append(talent['talent_name'][0:40])
    return talents

# consider using slot instead of player Battle Tag
def getTeam(replay, playerBattleTag, getAllies):
    player = findPlayer(replay, playerBattleTag)
    teammateHeroes = []
    for number in replay.players:
        otherPlayer = replay.players[number]
        if ((player.team == otherPlayer.team) == getAllies) and (player != otherPlayer):
            teammateHeroes.append(otherPlayer.hero)
    print(teammateHeroes)
    return teammateHeroes
    
                 
def findPlayer(replay, playerBattleTag):
    for number in replay.players:
        player = replay.players[number]
        if player.battleTag == playerBattleTag:
            return player
    raise ValueError('couldn\'t find a matching player')

def uploadReplay(replayPath, targetBattleTag):
    # TODO: sanitize the input

    archive = mpyq.MPQArchive(replayPath)
    import protocol67985 as protocol
    # TODO: catch exceptions
    #Parse the header 
    header = protocol.decode_replay_header(archive.header['user_data_header']['content'])
    build_number = header['m_version']['m_baseBuild']

    # Get the actual protocol number
    module_name = 'protocol{}'.format(build_number)
    protocol = import_module(module_name)
    
    print(replayPath)
    try:
        replay = processEvents(protocol, archive)
        addPlayerData(replay, targetBattleTag)
    except ValueError:
        pass
        

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('playerBattleTag')
    parser.add_argument('inputPath')
    parser.add_argument('-d', '--is-directory', help='Tells the parser to search the directory and upload all replays', action='store_true', default=False)
    parser.add_argument('-r', '--is-replay', help='Tells the parser the input path is a replay', action='store_true', default=False)
    args = parser.parse_args()
    
    playerBattleTag = args.playerBattleTag;
    inputPath = args.inputPath
    
    print("Looking for replays with player BattleTag " + playerBattleTag)
    
    if (args.is_replay):
        uploadReplay(inputPath, playerBattleTag)
    elif (args.is_directory):
        for file in os.listdir(inputPath):
            if file.endswith('.StormReplay'):
                uploadReplay(inputPath + "\\" + file, playerBattleTag)
            else:
                print("skipping {}.".format(file))
                
#    if commandLineArgs[1] == 'poll':
#        databaseID = sqlconnector.getPlayerDatabaseID(commandLineArgs[0], commandLineArgs[2])
#        gameSQLConnector = GameSQLConnector()
#        dictionary = gameSQLConnector.queryData(databaseID, "")
#        print(dictionary)

'''
details: 
 timeline stuff:
 team level ups, player deaths, building deaths, camp captures
 
 players:
 battletags, regions and stuff

 team:
 nothing useful

 heroes:
 has the useful stats, but i'll have to filter the stuff for the things I actually want

 units: 
 mostly useless 
'''
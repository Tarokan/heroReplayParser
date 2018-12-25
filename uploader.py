import mpyq
from importlib import import_module
from sqlconnector import GameSQLConnector
from hotsparser import processEvents
import sqlconnector
import sys
import argparse
import os
import re
import logging
import time
sys.path.insert(0, './heroprotocol')

logDirectory = './logs/'

logging.basicConfig(filename=logDirectory + (str(int(round(time.time() * 1000))) + '.log'), 
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.DEBUG)

sanitizeRegex = re.compile('[^a-zA-Z0-9]')

def log_info(string):
    logging.info(string)
    
def log_exception(string, exception):
    logging.exception(string)
    logging.exception(exception)

def addPlayerData(replay, playerBattleTag):
    print(str(replay.replayInfo))
    try:
        player = findPlayer(replay, playerBattleTag) # Player object
    except Exception as e:
        raise e
    playerSlot = player.id
    print("found player: " + playerBattleTag + " in slot " + str(playerSlot))
    
    heroPlayers = replay.heroList
    heroPlayer = heroPlayers[playerSlot]
    heroPlayerStats = heroPlayer.generalStats
    basicData = (player.gameResult, 
                player.hero, 
                heroPlayerStats.get('Takedowns', 0), 
                heroPlayerStats.get('Deaths', 0), 
                heroPlayerStats.get('HeroDamage', 0),
                heroPlayerStats.get('Healing', 0), 
                heroPlayerStats.get('SiegeDamage', 0), 
                heroPlayerStats.get('StructureDamage', 0),
                heroPlayerStats.get('MinionDamage', 0), 
                heroPlayerStats.get('SelfHealing', 0), 
                heroPlayerStats.get('DamageTaken', 0),
                heroPlayerStats.get('DamageSoaked', 0), 
                heroPlayerStats.get('ExperienceContribution', 0))
    
    gameSQLConnector = GameSQLConnector()
    try:
        entryid = gameSQLConnector.addHeroData(basicData, playerBattleTag)
        gameSQLConnector.addAlliedHeroes(getTeam(replay, playerBattleTag, True), entryid, playerBattleTag)
        gameSQLConnector.addEnemyHeroes(getTeam(replay, playerBattleTag, False), entryid, playerBattleTag)
        gameSQLConnector.addTalentChoices(getTalentChoices(replay, playerSlot), entryid, playerBattleTag)
        gameSQLConnector.addDateTime(replay.replayInfo.startTime, entryid, playerBattleTag)
        gameSQLConnector.addMap(sanitize(replay.replayInfo.mapName), entryid, playerBattleTag)
        gameSQLConnector.addGameType(sanitize(replay.replayInfo.gameType), entryid, playerBattleTag)
        print("Uploaded data succesfully!")
        log_info("replay data uploaded successfully")
    except Exception as e:
        print(e)
        log_exception("Exception occurred", e)

def getTalentChoices(replay, playerSlot):
    talents = []
    for talent in replay.heroList[playerSlot].generalStats['pickedTalents']:
        talents.append(sanitize(talent['talent_name'][0:40]))
    return talents

# consider using slot instead of player Battle Tag
def getTeam(replay, playerBattleTag, getAllies):
    player = findPlayer(replay, playerBattleTag)
    teammateHeroes = []
    for number in replay.players:
        otherPlayer = replay.players[number]
        if ((player.team == otherPlayer.team) == getAllies) and (player != otherPlayer):
            teammateHeroes.append(sanitize(otherPlayer.hero))
    return teammateHeroes

def sanitize(string):
    return sanitizeRegex.sub('', string)
                 
def findPlayer(replay, playerBattleTag):
    for number in replay.players:
        player = replay.players[number]
        if player.battleTag == playerBattleTag:
            return player
    raise ValueError('Couldn\'t find a matching player.')

def getReplayArchiveProtocolModule(archive):
    import protocol67985 as protocol
    # TODO: catch exceptions
    
    # Parse the header 
    header = protocol.decode_replay_header(archive.header['user_data_header']['content'])
    build_number = header['m_version']['m_baseBuild']
    log_info('replay archive protocol build_number: {}'.format(build_number))

    module_name = 'protocol{}'.format(build_number)
    
    # TODO: catch exception when protocol hasn't been updated yet
    try:
        protocol = import_module(module_name)
    except Exception as e:
        log_exception("FAILED IMPORT", e)
        raise e
    return protocol

def uploadReplay(replayPath, targetBattleTag):
    
    print(replayPath)
    log_info('opening replay MPQ at {}'.format(replayPath))
    
    archive = mpyq.MPQArchive(replayPath)
    protocol = getReplayArchiveProtocolModule(archive)
    
    try:
        log_info("running through the parser")
        replay = processEvents(protocol, archive)
        addPlayerData(replay, targetBattleTag)
    except Exception as e:
        print(e)
        log_exception("error running parser", e)

def isValidBattleTag(rawBattleTag):    
    # replace this with bnet oauth battletag in a production environment 
    # this does not allow for accents
    bnetRegex = re.compile('[^a-zA-Z0-9#]')
    return (bnetRegex.sub('', rawBattleTag) == rawBattleTag # no special characters
        and len(rawBattleTag) != 0 # at least one character long
        and not rawBattleTag[0].isdigit() # first character not a digit
        and len(rawBattleTag.split('#')) == 2 # there is only one #
        and rawBattleTag.split('#')[1].isdigit()) # the string following the # is a digit

if __name__ == "__main__":
    
    log_info('Beginning uploading session')
    parser = argparse.ArgumentParser()
    parser.add_argument('playerBattleTag')
    parser.add_argument('inputPath')
    parser.add_argument('-d', '--is-directory', help='Tells the parser to search the directory and upload all replays', action='store_true', default=False)
    parser.add_argument('-f', '--is-replayfile', help='Tells the parser the input path is a replay', action='store_true', default=False)
    parser.add_argument('-r', '--remove-table', help='Tells the parser to drop/remove the table', action='store_true', default=False)
    args = parser.parse_args()
    
    playerBattleTag = args.playerBattleTag
    if not isValidBattleTag(playerBattleTag):
        print('invalid battletag')
        log_info('Bad battletag: {}, exiting'.format(playerBattleTag))
        exit(0)
        
    inputPath = args.inputPath
    
    print("Looking for replays with player BattleTag " + playerBattleTag)
    
    if (args.is_replayfile):
        log_info('file specified: {}'.format(inputPath))
        if inputPath.endswith('.StormReplay'):
            uploadReplay(inputPath, playerBattleTag)
        else:
            print("not a valid file")
    elif (args.is_directory):
        log_info('directory specified: {}'.format(inputPath))
        for file in os.listdir(inputPath):
            if file.endswith('.StormReplay'):
                log_info('found file: {}'.format(file))
                uploadReplay(inputPath + "\\" + file, playerBattleTag)
            else:
                log_info('skipped file not ending in .StormReplay: {}'.format(file))
                print("skipping {}.".format(file))

from mpyq import mpyq
import json
import protocol67985 as protocol
from importlib import import_module
import io
import sys

relevent = ['Takedowns', 'Deaths', 'ExperienceContribution', 'Healing',
    'SiegeDamage', 'StructureDamage', 'MinionDamage', 'SelfHealing',
    'DamageTaken', 'DamageSoaked']

commandLineArgs = sys.argv[1:]

requestedPlayerName = '';
if len(commandLineArgs) == 1:
    requestedPlayerName = commandLineArgs[0]
    print("Looking for replays with player name " + requestedPlayerName)

class HeroPlayer:

    combatData = {}

    def __init__(self, hero, player, playerSlot):
        self.hero = hero
        self.player = player
        self.playerSlot = playerSlot

    def printInformation(self):
        print(self.player + " played " + self.hero + " in slot " + str(self.playerSlot))


# this returns a generator, you need to iterate through it
def getTrackerEvents():
    trackerEventsStack = archive.read_file('replay.tracker.events')
    trackerEvents = protocol.decode_replay_tracker_events(trackerEventsStack)
    return trackerEvents

def getDetails():
    detailsStack = archive.read_file('replay.details')
    details = protocol.decode_replay_details(detailsStack)
    return details

#Open the archive
archive = mpyq.MPQArchive('Dragon Shire (56).StormReplay')

#Parse the header
header = protocol.decode_replay_header(archive.header['user_data_header']['content'])
build_number = header['m_version']['m_baseBuild']

# Get the actual protocol number
module_name = 'protocol{}'.format(build_number)
protocol = import_module(module_name)


trackerEvents = getTrackerEvents()
details = getDetails()

if 'm_instanceList' in scoreResult:
    for item in scoreResult['m_instanceList']:
        print item['m_name']
    
playerList = details['m_playerList']
 
for player in playerList:
    if player['m_name'] == requestedPlayerName:
        print(requestedPlayerName + " found!")
        mainPlayer = HeroPlayer(player['m_hero'], player['m_name'], player['m_workingSetSlotId'])
        mainPlayer.printInformation()

for tracker_event in trackerEvents:
    if tracker_event['_event'] == 'NNet.Replay.Tracker.SScoreResultEvent':
        scoreResult = tracker_event

#debugJson = json.dumps(initdata, encoding="ISO-8859-1", ensure_ascii=False)
#
#with io.open('testDetails.json', 'w',  encoding='utf-8') as outfile:
#    outfile.write(debugJson)


## Let's grab 4 things for now: m_hero, m_name, m_result, m_workingSetSlotId


'''
    Tyrande
    Kael'thas
    Zarya
    Stitches
    Sylvanas
    
    Azmodan
    Tracer
    Rehgar
    Nazeebo
    Muradin (me :))
'''


import mysql.connector
from mysql.connector import errorcode, Error
from ConfigParser import ConfigParser
 
DB_NAME = 'heroes'

TABLES = {}

TABLES['games'] = (
"CREATE TABLE `games` ("
"	`game_id` INT AUTO_INCREMENT,"
"	`result` enum('W', 'L') NOT NULL,"
"	`playerHero` VARCHAR(15),"
"	`playerTakedowns` SMALLINT UNSIGNED,"
"    `playerDeaths` SMALLINT UNSIGNED,"
"    `playerSiegeDamage` MEDIUMINT UNSIGNED,"
"    `playerStructureDamage` MEDIUMINT UNSIGNED,"
"    `playerMinionDamage` MEDIUMINT UNSIGNED,"
"    `playerSelfHealing` MEDIUMINT UNSIGNED,"
"    `playerDamageTaken` MEDIUMINT UNSIGNED,"
"    `playerDamageSoaked` MEDIUMINT UNSIGNED,"
"	PRIMARY KEY (`game_id`)) ENGINE=InnoDB")

add_game = ("INSERT INTO games "
			"(result, playerHero, playerTakedowns,"
			"playerDeaths, playerSiegeDamage, playerStructureDamage,"
			"playerMinionDamage, playerSelfHealing, playerDamageTaken,"
			"playerDamageSoaked) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

data_game = ("W", "Gazlowe", 5, 0, 420, 420, 420, 420, 420, 420)

def connect():

	try:
		conn = mysql.connector.connect(host='localhost', database='heroes',
			user='root', password='ch1c0b0s')
		if conn.is_connected():
			print('connected to MySQL database!')
			return conn
		else:
			print('connection failed')
			exit(0)
	except Error as e:
		print(e)
		exit(0)
		
def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def mainStuff():
	conn = connect()
	cursor = conn.cursor()

	try:
	    cursor.execute("USE {}".format(DB_NAME))
	except mysql.connector.Error as err:
	    print("Database {} does not exists.".format(DB_NAME))
	    if err.errno == errorcode.ER_BAD_DB_ERROR:
	        create_database(cursor)
	        print("Database {} created successfully.".format(DB_NAME))
	    else:
	    	print(err)
	    	exit(1)

	for table_name in TABLES:
	    table_description = TABLES[table_name]
	    try:
	        print("Creating table {}: ".format(table_name))
	        cursor.execute(table_description)
	    except mysql.connector.Error as err:
	        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
	            print("already exists.")
	        else:
	            print(err.msg)
	    else:
	        print("OK")
	
	addGameData(cursor, conn)

	cursor.close()
	conn.close()

def addGameData(cursor, connector):
	cursor.execute(add_game, data_game)
	connector.commit()

if __name__ == '__main__':
	mainStuff()


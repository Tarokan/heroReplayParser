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
"    `playerHeroDamage` SMALLINT UNSIGNED,"
"    `playerHealing` SMALLINT UNSIGNED,"
"    `playerSiegeDamage` MEDIUMINT UNSIGNED,"
"    `playerStructureDamage` MEDIUMINT UNSIGNED,"
"    `playerMinionDamage` MEDIUMINT UNSIGNED,"
"    `playerSelfHealing` MEDIUMINT UNSIGNED,"
"    `playerDamageTaken` MEDIUMINT UNSIGNED,"
"    `playerDamageSoaked` MEDIUMINT UNSIGNED,"
"    `playerExperience` MEDIUMINT UNSIGNED,"
"	PRIMARY KEY (`game_id`)) ENGINE=InnoDB")

add_game = ("INSERT INTO games "
			"(result, playerHero, playerTakedowns,"
			"playerDeaths, playerHeroDamage, playerHealing, playerSiegeDamage, playerStructureDamage,"
			"playerMinionDamage, playerSelfHealing, playerDamageTaken,"
			"playerDamageSoaked, playerExperience) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

class GameSQLConnector:

	def __init__(self):
		self.conn = self.connect()
		self.cursor = self.conn.cursor()
	
		try:
		    self.cursor.execute("USE {}".format(DB_NAME))
		except mysql.connector.Error as err:
		    print("Database {} does not exists.".format(DB_NAME))
		    if err.errno == errorcode.ER_BAD_DB_ERROR:
		        create_database()
		        print("Database {} created successfully.".format(DB_NAME))
		    else:
		    	print(err)
		    	exit(1)
	
		for table_name in TABLES:
		    table_description = TABLES[table_name]
		    try:
		        print("Creating table {}: ".format(table_name))
		        self.cursor.execute(table_description)
		    except mysql.connector.Error as err:
		        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
		            print("already exists.")
		        else:
		            print(err.msg)
		    else:
		        print("OK")

	def close(self):
		self.cursor.close()
		self.conn.close()

	def connect(self):
		try:
			self.conn = mysql.connector.connect(host='localhost', database='heroes',
				user='root', password='ch1c0b0s')
			if self.conn.is_connected():
				print('connected to MySQL database!')
				return self.conn
			else:
				print('connection failed')
				exit(0)
		except Error as e:
			print(e)
			exit(0)
		
	def create_database(self):
	    try:
	        self.cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
	    except mysql.connector.Error as err:
	        print("Failed creating database: {}".format(err))
	        exit(1)
	
	def addGameData(self, game_data):
		self.cursor.execute(add_game, game_data)
		self.conn.commit()
import mysql.connector
from mysql.connector import errorcode, Error
from ConfigParser import ConfigParser
 
DB_NAME = 'heroes'

TABLES = {}
TABLES['matches'] = (
	"CREATE TABLE `games` ("
	" `game_id` INT AUTO_INCREMENT,"
	" `result` enum('W', 'L') NOT NULL,"
	" PRIMARY KEY (`game_id`)"
	") ENGINE=InnoDB")


def connect():

	try:
		conn = mysql.connector.connect(host='localhost', database='mysql',
			user='root', password='Col0rM3Blu3')
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
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

def mainStuff():
	conn = connect()
	cursor = conn.cursor()

	create_database(cursor)

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
	
	cursor.close()
	conn.close()

if __name__ == '__main__':
	mainStuff()


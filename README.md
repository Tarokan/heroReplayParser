# Heroes of the Storm Replay SQL Uploader
A tool to upload Heroes of the Storm replay data to an SQL database.

## Prequisites
* Python 2
* SQL installation (tested with MySQL CE for Windows)

You will need the following python libraries:

* `jsonpickle`
* `psycopg2ct`

## How to use this tool:
Create a file named `db.config` in the root of the respository, formatted as JSON, with the following fields:
```
{
    "host": <host address here>,
    "database": <database name here>,
    "user": <SQL user username>,
    "password": <SQL user password>
}
```
This will tell the uploader how to connect to the SQL database, and now uploader can be run:
```
usage: uploader.py [-h] [-d] [-f] [-r] playerBattleTag inputPath

positional arguments:
  playerBattleTag
  inputPath

optional arguments:
  -h, --help           show this help message and exit
  -d, --is-directory   Tells the parser to search the directory and upload all
                       replays
  -f, --is-replayfile  Tells the parser the input path is a replay
  -r, --remove-table   Tells the parser to drop/remove the table
```
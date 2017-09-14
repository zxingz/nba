import os
import sys
import json
import sqlite3


#main class
class nbaMain():

    #initialize the telegram bot and logger
    def __init__(self, site):
        # initializing environment
        sys.path.append('../../common/script')
        import initEnv
        self.logger, self.bot = initEnv.env(__file__).ret()
        self.logger.info('starting app: ' + os.environ.get('MODULE_NAME'))

        #variables
        self.pointers = {"FD":{"3pt":3, "2pt":2, "ft":1, "rebound":1.2, "block":2, "steal":2, "to":-1, "assists":1.5},
                    "DK":{"3pt":3.5, "2pt":2, "ft":1, "rebound":1.25, "block":2, "steal":2, "to":-0.5, "assists":1.5,
                          "doubleDouble":1.5, "tripleDouble":3}}
        self.logger.info('setting site='+site)
        self.site = site

    #read the scraped data and save again as json
    def saveGameDataJson(self, date, gameID):
        try:
            self.logger.info('saving game data into json for date = '+date+' and gameID = '+gameID)
            with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID, 'r') as file:
                data = file.read()
            data = data.split('#')
            gameData = {"team1name": data[1], "team2name": data[2], "team1starters": [], "team1bench": [],
                        "team2starters": [], "team2bench": []}
            i = 19
            currTeam = 1
            currData = 'team1starters'
            while i < len(data):
                if data[i] == 'Bench' and currTeam == 1:
                    i += 15
                    currData = 'team1bench'
                elif (data[i + 3].find('DNP') != -1 or data[i + 3].find('TEAM') != -1) and currTeam == 1:
                    currTeam = 2
                    while data[i] != 'PTS':
                        i += 1
                    i += 1
                    currData = 'team2starters'
                elif data[i] == 'Bench' and currTeam == 2:
                    i += 15
                    currData = 'team2bench'
                elif (data[i + 3].find('DNP') != -1 or data[i + 3].find('TEAM') != -1) and currTeam == 2:
                    break

                gameData[currData].append({"name": data[i], "position": data[i + 2], "minutes": int(data[i + 3]),
                                           "fieldGoalMade": int(data[i + 4].split('-')[0]),
                                           "fieldGoalAttempted": int(data[i + 4].split('-')[1]),
                                           "3pointMade": int(data[i + 5].split('-')[0]),
                                           "3pointAttempted": int(data[i + 5].split('-')[1]),
                                           "freeThrowMade": int(data[i + 6].split('-')[0]),
                                           "freeThrowAttempted": int(data[i + 6].split('-')[1]),
                                           "offensiveRebound": int(data[i + 7]),
                                           "defensiveRebound": int(data[i + 8]),
                                           "assist": int(data[i + 10]), "steal": int(data[i + 11]), "block": int(data[i + 12]),
                                           "turnOver": int(data[i + 13]), "personalFoul": int(data[i + 14]),
                                           "plusMinus": int(data[i + 15]), "points": int(data[i + 16])})
                i += 17
            with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID+'.json', 'w') as file:
                json.dump(gameData, file)
            self.logger.info('game data saved')
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            game.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            game.sendTelegram('Error occured: ' + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    #read saved json config data
    def loadGameDataJson(self, date, gameID):
        self.logger.info('loading game data into json for date = ' + date + ' and gameID = ' + gameID)
        with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID+'.json', 'r') as file:
            data = json.load(file)
        return data

    #calculate FD or Dk score from player json
    def calculateScore(self,playerData):
        self.logger.info('calculating score for player='+playerData["name"])
        score = playerData["3pointMade"]*self.pointers[self.site]["3pt"] + \
                (playerData["fieldGoalMade"]-playerData["3pointMade"])*self.pointers[self.site]["2pt"] + \
                playerData["freeThrowMade"]*self.pointers[self.site]["ft"] + \
                (playerData["offensiveRebound"]+playerData["defensiveRebound"])* self.pointers[self.site]["rebound"] + \
                playerData["block"] * self.pointers[self.site]["block"] + \
                playerData["steal"] * self.pointers[self.site]["steal"] + \
                playerData["turnOver"] * self.pointers[self.site]["to"] + \
                playerData["assist"] * self.pointers[self.site]["assists"]
        if self.site == 'DK':
            bonus = len([x for x in [playerData["assist"], playerData["steal"], playerData["block"],
             playerData["offensiveRebound"]+playerData["offensiveRebound"], playerData["points"]] if x >9])
            if bonus == 2:
                score += self.pointers[self.site]["doubleDouble"]
            elif bonus > 2:
                score += self.pointers[self.site]["tripleDouble"]



        return score

    def sendTelegram(self, message):
        self.logger.info('sending telegram: '+message)
        self.bot.send_message(chat_id=439726750, text=message)


#sqlite class
class sqliteDB():
    def __init__(self, logger):
        self.logger = logger
        try:
            self.conn = sqlite3.connect(os.environ.get('DATA_BASE') + '/nba.db')
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    def insert(self, cmd):
        try:
            c = self.conn.cursor()
            c.execute(cmd)
            self.conn.commit()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    def fetch(self, cmd):
        try:
            c = self.conn.cursor()
            c.execute(cmd)
            return c.fetchall()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return []

if __name__ == '__main__':
    game = nbaMain('DK')
    db = sqliteDB(game.logger)
    res = db.fetch('select * from BOX_SCORE')
    pass
    #game.saveGameDataJson("20170102", "400899414")
    #gameData = game.loadGameDataJson("20170102", "400899414")
    #player = gameData["team1bench"][2]
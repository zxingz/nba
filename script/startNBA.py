import os
import sys
import json

#initializing environment
sys.path.append('../../common/script')
import initEnv
logger, bot = initEnv.env(__file__).ret()
logger.info('starting app: '+os.environ.get('MODULE_NAME'))


#main class
class nbaMain():

    def __init__(self, logger, bot):
        self.logger = logger
        self.bot = bot

    def saveGameDataJson(self, date, gameID):
        try:
            self.logger.info('loading game data into json for date = '+date+' and gameID = '+gameID)
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

                gameData[currData].append({"name": data[i], "position": data[i + 2], "minutes": data[i + 3],
                                           "fieldGoalMade": data[i + 4].split('-')[0],
                                           "fieldGoalAttempted": data[i + 4].split('-')[1],
                                           "3pointMade": data[i + 5].split('-')[0],
                                           "3pointAttempted": data[i + 5].split('-')[1],
                                           "freeThrowMade": data[i + 6].split('-')[0],
                                           "freeThrowAttempted": data[i + 6].split('-')[1],
                                           "offensiveRebound": data[i + 7],
                                           "defensiveRebound": data[i + 8],
                                           "assist": data[i + 10], "steal": data[i + 11], "block": data[i + 12],
                                           "turnOver": data[i + 13], "personalFoul": data[i + 14],
                                           "plusMinus": data[i + 15], "points": data[i + 16]})
                i += 17
            with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID+'.json', 'w') as file:
                json.dump(gameData, file)
            self.logger.info('game data saved')
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            game.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            game.sendTelegram('Error occured: ' + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    def getBoxScoreEspn(self, date):


    def sendTelegram(self, message):
        self.logger.info('sending telegram: '+message)
        self.bot.send_message(chat_id=439726750, text=message)

if __name__ == '__main__':
    game = nbaMain(logger, bot)
    game.saveGameDataJson("20170102", "400899414")
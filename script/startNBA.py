#!./../../tools/python/bin/python

import os
import sys
import json
import sqlite3
from selenium import webdriver
import urllib.request
from datetime import date, timedelta
import re
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools


#main class
class nbaMain():

    #initialize the telegram bot and logger
    def __init__(self):
        # initializing environment
        sys.path.append('../../common/script')
        import initEnv
        print(__file__)
        self.logger, self.bot = initEnv.env(__file__).ret()
        self.logger.info('starting app: ' + os.environ.get('MODULE_NAME'))

        #variables
        self.pointers = {"FD":{"3pt":3, "2pt":2, "ft":1, "rebound":1.2, "block":2, "steal":2, "to":-1, "assists":1.5},
                    "DK":{"3pt":3.5, "2pt":2, "ft":1, "rebound":1.25, "block":2, "steal":2, "to":-0.5, "assists":1.5,
                          "doubleDouble":1.5, "tripleDouble":3}}

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
                    continue
                if data[i + 3].find('DNP') != -1 or data[i + 3].find('Did not') != -1:
                    i += 4
                    continue
                if (data[i + 3].find('TEAM') != -1 or data[i].find('TEAM') != -1)and currTeam == 1:
                    currTeam = 2
                    while data[i] != 'PTS':
                        i += 1
                    i += 1
                    currData = 'team2starters'
                    continue
                if data[i] == 'Bench' and currTeam == 2:
                    i += 15
                    currData = 'team2bench'
                    continue
                if (data[i + 3].find('TEAM') != -1 or data[i].find('TEAM') != -1) and currTeam == 2:
                    break
                try:
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
                except Exception as error:
                    game.logger.info("Error "+str(i)+' '+data[i])
                i += 17
            with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID+'.json', 'w') as file:
                json.dump(gameData, file)
            self.logger.info('game data saved')
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            game.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            game.sendTelegram('Error occured: ' + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            raise Exception('Error !')

    #read saved json config data
    def loadGameDataJson(self, date, gameID):
        try:
            self.logger.info('loading game data into json for date = ' + date + ' and gameID = ' + gameID)
            with open(os.environ.get('DATA_BASE') + '/' + date + '/' + gameID+'.json', 'r') as file:
                data = json.load(file)
            return data
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return {}

    #calculate FD or Dk score from player json
    def calculateScore(self,playerData):
        try:
            self.logger.info('calculating score for player=' + playerData["name"])
            score = {"FD":{}, "DK":{}}
            site = 'FD'
            score[site]["3pt"] = playerData["3pointMade"] * self.pointers[site]["3pt"]
            score[site]["2pt"] = (playerData["fieldGoalMade"] - playerData["3pointMade"]) * self.pointers[site]["2pt"]
            score[site]["ft"] = playerData["freeThrowMade"] * self.pointers[site]["ft"]
            score[site]["rebound"] = (playerData["offensiveRebound"] + playerData["defensiveRebound"]) * \
                                     self.pointers[site]["rebound"]
            score[site]["block"] = playerData["block"] * self.pointers[site]["block"]
            score[site]["steal"] = playerData["steal"] * self.pointers[site]["steal"]
            score[site]["to"] = playerData["turnOver"] * self.pointers[site]["to"]
            score[site]["assists"] = playerData["assist"] * self.pointers[site]["assists"]
            score[site]["total"] = score[site]["3pt"] + score[site]["2pt"] + score[site]["ft"] +  score[site]["rebound"]\
                                   + score[site]["block"] + score[site]["steal"] + score[site]["to"] + \
                                   score[site]["assists"]
            site = 'DK'
            score[site]["3pt"] = playerData["3pointMade"] * self.pointers[site]["3pt"]
            score[site]["2pt"] = (playerData["fieldGoalMade"] - playerData["3pointMade"]) * self.pointers[site]["2pt"]
            score[site]["ft"] = playerData["freeThrowMade"] * self.pointers[site]["ft"]
            score[site]["rebound"] = (playerData["offensiveRebound"] + playerData["defensiveRebound"]) * \
                                     self.pointers[site]["rebound"]
            score[site]["block"] = playerData["block"] * self.pointers[site]["block"]
            score[site]["steal"] = playerData["steal"] * self.pointers[site]["steal"]
            score[site]["to"] = playerData["turnOver"] * self.pointers[site]["to"]
            score[site]["assists"] = playerData["assist"] * self.pointers[site]["assists"]
            bonus = len([x for x in [playerData["assist"], playerData["steal"], playerData["block"],
                                         playerData["offensiveRebound"] + playerData["offensiveRebound"],
                                         playerData["points"]] if x > 9])
            if bonus == 2:
                score[site]["doubleDouble"] = self.pointers[site]["doubleDouble"]
                score[site]["tripleDouble"] = 0
            elif bonus > 2:
                score[site]["doubleDouble"] = 0
                score[site]["tripleDouble"] = self.pointers[site]["doubleDouble"]
            else:
                score[site]["doubleDouble"] = 0
                score[site]["tripleDouble"] = 0
            score[site]["total"] = score[site]["3pt"] + score[site]["2pt"] + score[site]["ft"] + score[site]["rebound"] \
                                   + score[site]["block"] + score[site]["steal"] + score[site]["to"] + \
                                   score[site]["assists"] + score[site]["tripleDouble"] + score[site]["doubleDouble"]
            return score
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return None

    def sendTelegram(self, message):
        self.logger.info('sending telegram: '+message)
        self.bot.send_message(chat_id=439726750, text=message)

    def insertGameDataDB(self, date, gameID):
        try:
            db = sqliteDB(self.logger)
            jsonData = self.loadGameDataJson(date, gameID)
            for row in jsonData["team1starters"]:
                score = self.calculateScore(row)
                cmd = 'INSERT OR REPLACE INTO BOX_SCORE VALUES("'+jsonData["team1name"]+'",1,"'+row["name"]+\
                      '",'+str(row["minutes"])+','+str(row["fieldGoalMade"])+','+str(row["fieldGoalAttempted"])+\
                      ','+str(row["3pointMade"])+','+str(row["3pointAttempted"])+','+str(row["freeThrowMade"])+\
                      ','+str(row["freeThrowAttempted"])+','+str(row["offensiveRebound"])+','+str(row["defensiveRebound"])\
                      +','+str(row["assist"])+','+str(row["steal"])+','+str(row["block"])+','+str(row["turnOver"])+\
                      ','+str(row["personalFoul"])+','+str(row["plusMinus"])+','+str(row["points"])+','+\
                      str(score["FD"]["3pt"])+','+str(score["FD"]["2pt"])+','+str(score["FD"]["ft"])+','+\
                      str(score["FD"]["rebound"])+','+str(score["FD"]["block"])+','+str(score["FD"]["steal"])+','+\
                      str(score["FD"]["to"])+','+str(score["FD"]["assists"])+','+str(score["FD"]["total"])+','+\
                      str(score["DK"]["3pt"])+','+str(score["DK"]["2pt"])+','+str(score["DK"]["ft"])+','+\
                      str(score["DK"]["rebound"])+','+str(score["DK"]["block"])+','+str(score["DK"]["steal"])+','+\
                      str(score["DK"]["to"])+','+str(score["DK"]["assists"])+','+str(score["DK"]["doubleDouble"])+','+\
                      str(score["DK"]["tripleDouble"])+','+str(score["DK"]["total"])+',"'+str(row["position"])+'","'+\
                      date+'",'+gameID+',"'+jsonData["team2name"]+'")'
                db.insert(cmd)
            for row in jsonData["team1bench"]:
                score = self.calculateScore(row)
                cmd = 'INSERT OR REPLACE INTO BOX_SCORE VALUES("'+jsonData["team1name"]+'",0,"'+row["name"]+\
                      '",'+str(row["minutes"])+','+str(row["fieldGoalMade"])+','+str(row["fieldGoalAttempted"])+\
                      ','+str(row["3pointMade"])+','+str(row["3pointAttempted"])+','+str(row["freeThrowMade"])+\
                      ','+str(row["freeThrowAttempted"])+','+str(row["offensiveRebound"])+','+str(row["defensiveRebound"])\
                      +','+str(row["assist"])+','+str(row["steal"])+','+str(row["block"])+','+str(row["turnOver"])+\
                      ','+str(row["personalFoul"])+','+str(row["plusMinus"])+','+str(row["points"])+','+\
                      str(score["FD"]["3pt"])+','+str(score["FD"]["2pt"])+','+str(score["FD"]["ft"])+','+\
                      str(score["FD"]["rebound"])+','+str(score["FD"]["block"])+','+str(score["FD"]["steal"])+','+\
                      str(score["FD"]["to"])+','+str(score["FD"]["assists"])+','+str(score["FD"]["total"])+','+\
                      str(score["DK"]["3pt"])+','+str(score["DK"]["2pt"])+','+str(score["DK"]["ft"])+','+\
                      str(score["DK"]["rebound"])+','+str(score["DK"]["block"])+','+str(score["DK"]["steal"])+','+\
                      str(score["DK"]["to"])+','+str(score["DK"]["assists"])+','+str(score["DK"]["doubleDouble"])+','+ \
                      str(score["DK"]["tripleDouble"]) + ',' + str(score["DK"]["total"]) + ',"' + str(row["position"]) + '","' + \
                      date + '",' + gameID + ',"' + jsonData["team2name"] + '")'
                db.insert(cmd)
            for row in jsonData["team2starters"]:
                score = self.calculateScore(row)
                cmd = 'INSERT OR REPLACE INTO BOX_SCORE VALUES("'+jsonData["team2name"]+'",1,"'+row["name"]+\
                      '",'+str(row["minutes"])+','+str(row["fieldGoalMade"])+','+str(row["fieldGoalAttempted"])+\
                      ','+str(row["3pointMade"])+','+str(row["3pointAttempted"])+','+str(row["freeThrowMade"])+\
                      ','+str(row["freeThrowAttempted"])+','+str(row["offensiveRebound"])+','+str(row["defensiveRebound"])\
                      +','+str(row["assist"])+','+str(row["steal"])+','+str(row["block"])+','+str(row["turnOver"])+\
                      ','+str(row["personalFoul"])+','+str(row["plusMinus"])+','+str(row["points"])+','+\
                      str(score["FD"]["3pt"])+','+str(score["FD"]["2pt"])+','+str(score["FD"]["ft"])+','+\
                      str(score["FD"]["rebound"])+','+str(score["FD"]["block"])+','+str(score["FD"]["steal"])+','+\
                      str(score["FD"]["to"])+','+str(score["FD"]["assists"])+','+str(score["FD"]["total"])+','+\
                      str(score["DK"]["3pt"])+','+str(score["DK"]["2pt"])+','+str(score["DK"]["ft"])+','+\
                      str(score["DK"]["rebound"])+','+str(score["DK"]["block"])+','+str(score["DK"]["steal"])+','+\
                      str(score["DK"]["to"])+','+str(score["DK"]["assists"])+','+str(score["DK"]["doubleDouble"])+','+ \
                      str(score["DK"]["tripleDouble"]) + ',' + str(score["DK"]["total"]) + ',"' + str(row["position"]) + '","' + \
                      date + '",' + gameID + ',"' + jsonData["team1name"] + '")'
                db.insert(cmd)
            for row in jsonData["team2bench"]:
                score = self.calculateScore(row)
                cmd = 'INSERT OR REPLACE INTO BOX_SCORE VALUES("'+jsonData["team2name"]+'",0,"'+row["name"]+\
                      '",'+str(row["minutes"])+','+str(row["fieldGoalMade"])+','+str(row["fieldGoalAttempted"])+\
                      ','+str(row["3pointMade"])+','+str(row["3pointAttempted"])+','+str(row["freeThrowMade"])+\
                      ','+str(row["freeThrowAttempted"])+','+str(row["offensiveRebound"])+','+str(row["defensiveRebound"])\
                      +','+str(row["assist"])+','+str(row["steal"])+','+str(row["block"])+','+str(row["turnOver"])+\
                      ','+str(row["personalFoul"])+','+str(row["plusMinus"])+','+str(row["points"])+','+\
                      str(score["FD"]["3pt"])+','+str(score["FD"]["2pt"])+','+str(score["FD"]["ft"])+','+\
                      str(score["FD"]["rebound"])+','+str(score["FD"]["block"])+','+str(score["FD"]["steal"])+','+\
                      str(score["FD"]["to"])+','+str(score["FD"]["assists"])+','+str(score["FD"]["total"])+','+\
                      str(score["DK"]["3pt"])+','+str(score["DK"]["2pt"])+','+str(score["DK"]["ft"])+','+\
                      str(score["DK"]["rebound"])+','+str(score["DK"]["block"])+','+str(score["DK"]["steal"])+','+\
                      str(score["DK"]["to"])+','+str(score["DK"]["assists"])+','+str(score["DK"]["doubleDouble"])+','+ \
                      str(score["DK"]["tripleDouble"]) + ',' + str(score["DK"]["total"]) + ',"' + str(row["position"]) + '","' + \
                      date + '",' + gameID + ',"' + jsonData["team1name"] + '")'
                db.insert(cmd)
            db.conn.close()
        except Exception as error:
            db.conn.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            raise Exception('Error !')

    def getESPNgameID(self, cdate):
        try:
            self.logger.info("getting game ids for date="+cdate)
            #driver = webdriver.Chrome('./../../tools/chrome/chromedriver')
            driver = webdriver.PhantomJS('./../../tools/phantomjs/phantomjs')
            driver.set_page_load_timeout(60)
            sdate = date(int(cdate[0:4]), int(cdate[4:6]), int(cdate[6:8]))
            url = 'http://www.espn.com/nba/scoreboard/_/date/' + sdate.strftime('%Y%m%d')
            driver.get(url)
            source = str(driver.page_source)
            game_ids = {}
            if source.find(sdate.strftime('%B %-d, %Y')) != -1:
                if source.find('/nba/boxscore?gameId=') != -1:
                    os.system('mkdir -p $DATA_BASE/' + cdate)
                while source.find('/nba/boxscore?gameId=') != -1:
                    source = source[source.find('/nba/boxscore?gameId=') + 21:]
                    game_ids[source[:source.find('"')]] = True
            if game_ids.keys() != []:
                with open(os.environ.get('DATA_BASE') + '/' + cdate + '/' + cdate + '_gameID', 'w') as file:
                    file.write('\n'.join(game_ids.keys()))
            driver.close()
            return game_ids
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            driver.close()
            return {}

    def getESPNboxScore(self, cdate):
        try:
            with open(os.environ.get('DATA_BASE') + '/' + cdate + '/' + cdate + '_gameID', 'r')as file:
                game_ids = file.read().split('\n')
            for key in game_ids:
                text = str(urllib.request.urlopen('http://www.espn.com/nba/boxscore?gameId=' + key).read())
                text = text[text.find('<article class="boxscore'):]
                text = re.compile(r'<.*?>').sub('#', text[:text.find('</article>')]).replace('team', '')
                while text.find('##') != -1:
                    text = text.replace('##', '#')
                text = text.split('#')
                del text[0:2]
                with open(os.environ.get('DATA_BASE') + '/' + cdate + '/' + key, 'w') as file:
                    file.write('#'.join(text))
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return {}

    def generateGraphs(self, date, gameID):
        try:
            db = sqliteDB(self.logger)
            result = db.fetch(
                "select name || '-' || position || '-' || starter as name, position,team, starter,MINUTES,FD_3PT,FD_2PT,FD_FT,"
                "FD_REBOUND,FD_BLOCK,FD_STEAL,FD_TO,FD_ASSISTS,FD_TOTAL,DK_3PT,DK_2PT,DK_FT,DK_REBOUND,DK_BLOCK,DK_STEAL,DK_TO,"
                "DK_ASSISTS,DK_DOUBLEDOUBLE,DK_TRIPLEDOUBLE,DK_TOTAL from box_score where game_id = '"+str(gameID)+"'")
            db.conn.close()
            if result == []:
                return
            posColor = {'PF': 'rgb(230, 25, 75,0.8)', 'SF': 'rgb(128, 0, 0,0.8)', 'F': 'rgb(145, 30, 180,0.8)',
                        'C': 'rgb(0, 130, 200,0.8)', 'G': 'rgb(60, 180, 75,0.8)', 'PG': 'rgb(128, 128, 0,0.8)',
                        'SG': 'rgb(0, 128, 128,0.8)'}
            statusColor = {0: 'rgb(255, 255, 255)', 1: 'rgb(0,0,0)'}
            statMap = {'FD_3PT': 5, 'FD_2PT': 6, 'FD_FT': 7, 'FD_REBOUND': 8, 'FD_BLOCK': 9, 'FD_STEAL': 10,
                       'FD_TO': 11, 'FD_ASSISTS': 12,'DK_3PT': 14, 'DK_2PT': 15, 'DK_FT': 16, 'DK_REBOUND': 17,
                       'DK_BLOCK': 18, 'DK_STEAL': 19,'DK_TO': 20,'DK_ASSISTS': 21, 'DK_DOUBLEDOUBLE': 22,
                       'DK_TRIPLEDOUBLE': 23}
            for key in statMap:
                teams = {}
                teamCount = 0
                traces = {1: [], 2: []}
                self.logger.info('making graph for key='+key+' for gameID='+str(gameID)+' and date='+date)
                for row in result:
                    if row[2] not in teams.keys():
                        teams[row[2]] = teamCount + 1
                        teamCount += 1
                    traces[teams[row[2]]].append(go.Scatter(
                        x=[row[13]],
                        y=[row[statMap[key]]],
                        name=row[0] + '-' + row[2],
                        text=row[0] + '-' + row[2],
                        mode='markers',
                        marker=dict(
                            size=row[4],
                            color=posColor[row[1]],
                            line=dict(
                                width=4,
                                color=statusColor[row[3]]
                            )
                        )
                    ))

                fig = tools.make_subplots(rows=2, cols=1)
                for row in traces[1]:
                    fig.append_trace(row, 1, 1)
                for row in traces[2]:
                    fig.append_trace(row, 2, 1)
                py.plot(fig, filename=os.environ.get('DATA_BASE') + '/' + date + '/'+ key+'_'+str(gameID)+'_'+
                                      teams.popitem()[0]+'_'+teams.popitem()[0]+'.html', auto_open=False)
        except Exception as error:
            db.conn.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    def runFullProcess(self, begin, end=date.today() + timedelta(1), processFilter=['p1', 'p2', 'p3', 'p4', 'p5']):

        if 'p1' in processFilter:
            self.logger.info('p1-getting all the game ids...')
            start = begin
            while start != end:
                self.getESPNgameID(start.strftime('%Y%m%d'))
                start += timedelta(1)

        if 'p2' in processFilter:
            self.logger.info('p2-getting all the box scores...')
            start = begin
            while start != end:
                self.getESPNboxScore(start.strftime('%Y%m%d'))
                start += timedelta(1)

        if 'p3' in processFilter:
            self.logger.info('p3-saving all the json data...')
            start = begin
            while start != end:
                try:
                    with open(os.environ.get('DATA_BASE') + '/' + start.strftime('%Y%m%d') + '/' + start.strftime(
                            '%Y%m%d')
                                      + '_gameID', 'r')as file:
                        gameIDs = file.read().split('\n')
                    for key in gameIDs:
                        self.saveGameDataJson(start.strftime('%Y%m%d'), key)
                except:
                    pass
                start += timedelta(1)

        if 'p4' in processFilter:
            self.logger.info('p4-inserting json data into database...')
            start = begin
            while start != end:
                try:
                    with open(os.environ.get('DATA_BASE') + '/' + start.strftime('%Y%m%d') + '/' + start.strftime(
                            '%Y%m%d')
                                      + '_gameID', 'r')as file:
                        gameIDs = file.read().split('\n')
                    for key in gameIDs:
                        self.insertGameDataDB(start.strftime('%Y%m%d'), key)
                except:
                    pass
                start += timedelta(1)

        if 'p5' in processFilter:
            self.logger.info('p5-generating graphs...')
            start = begin
            while start != end:
                try:
                    with open(os.environ.get('DATA_BASE') + '/' + start.strftime('%Y%m%d') + '/' + start.strftime(
                            '%Y%m%d')+ '_gameID', 'r')as file:
                        gameIDs = file.read().split('\n')
                    for key in gameIDs:
                        self.generateGraphs(start.strftime('%Y%m%d'), key)
                except:
                    pass
                start += timedelta(1)

        self.logger.info('all done !')

#sqlite class
class sqliteDB():
    def __init__(self, logger):
        self.logger = logger
        self.logger.info('establishing DB connection...')
        self.conn = sqlite3.connect(os.environ.get('DATA_BASE') + '/nba.db')

    def insert(self, cmd):
        try:
            self.logger.info('inserting command : '+cmd)
            c = self.conn.cursor()
            c.execute(cmd)
            self.conn.commit()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))

    def fetch(self, cmd):
        try:
            self.logger.info('fetching command : ' + cmd)
            c = self.conn.cursor()
            c.execute(cmd)
            return c.fetchall()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return []

if __name__ == '__main__':
    game = nbaMain()
    begin = date(2017, 11, 5)
    game.runFullProcess(begin=begin, processFilter=['p1', 'p2', 'p3', 'p4'])
    #game.insertGameDataDB("20170102", "400899414")
    #game.saveGameDataJson("20160307", "400828826")
    #gameData = game.loadGameDataJson("20170102", "400899414")
    #player = gameData["team1bench"][2]

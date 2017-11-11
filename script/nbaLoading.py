#!./../../tools/python/bin/python

import os
import sys
import json
import sqlite3


class nbaLoading:

    # initialize the telegram bot and logger
    def __init__(self):
        # initializing environment
        sys.path.append('../../common/script')
        import initEnv
        print(__file__)
        self.logger, self.bot = initEnv.env(__file__).ret()
        self.logger.info('starting app: ' + os.environ.get('MODULE_NAME'))

    def processResultFile(self, file):
        try:
            self.logger.info('processing result file : ' + file)
            with open(file, 'r') as readFile:
                data = readFile.read().split('\n')
            data = [[y for y in x.split(',') if y != ''] for x in data if x != '']
            self.logger.info('file processing completed')
            return data

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return []

# dk loading
class DKLoading(nbaLoading):

    def __init__(self):
        nbaLoading.__init__(self)

    def processDKLineupFile(self, file):
        try:
            self.logger.info('processing lineup upload file : ' + file)
            with open(file, 'r') as readFile:
                data = readFile.read().split('\n')
            data = [[y for y in x.split(',') if y != ''] for x in data if x != '']
            while 1:
                if data[0][0] == 'Position':
                    self.logger.info('file processing completed')
                    return data
                del data[0]
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.info("Error occured: " + str(error) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno))
            return []

    def generateUserOutput(self, lineupData, resultData, location, date, version):
        resultDataHeader = {}
        lineupDataHeader = {}
        for i in range(0, len(resultData[0])):
            resultDataHeader[resultData[0][i]] = i
        del resultData[0]
        for i in range(0, len(lineupData[0])):
            lineupDataHeader[lineupData[0][i]] = i
        del lineupData[0]
        if 'dk_id' not in resultDataHeader.keys():
            resultDataHeader['dk_id'] = max(resultDataHeader.values())+1
        nooptions = []
        for i in range(0, len(lineupData)):
            print('current lineup data is :', lineupData[i][lineupDataHeader['Name']], lineupData[i][lineupDataHeader['TeamAbbrev ']],lineupData[i][lineupDataHeader['ID']])
            options = []
            ch = None
            for j in range(0, len(resultData)):
                if lineupData[i][lineupDataHeader['Name']].split(' ')[1].lower() == resultData[j][resultDataHeader['name']].split(' ')[1].split('-')[0].lower() and lineupData[i][lineupDataHeader['Name']][0].lower() == resultData[j][resultDataHeader['name']][0].lower():
                    if len(resultData[j]) > resultDataHeader['dk_id'] and resultData[j][resultDataHeader['dk_id']] != '':
                        print(resultData[j][resultDataHeader['name']], resultData[j][resultDataHeader['team']],
                              resultData[j][resultDataHeader['dk_id']])
                        ch = -9
                        #break
                    else:
                        options.append([resultData[j], j])
            if options != []:
                print('your options for assigning values are : ')
                for j in range(0, len(options)):
                    print(str(j + 1) + '. ' + str(options[j][0]))
                print('-9 for skip')
                ch = int(input('Enter your choice : '))
                if ch - 1 < len(options) and ch > 0:
                    resultData[options[ch - 1][1]].insert(resultDataHeader['dk_id'],
                                                          lineupData[i][lineupDataHeader['ID']])
                    print(resultData[options[ch - 1][1]])
                else:
                    if ch != -9:
                        nooptions.append([lineupData[i][lineupDataHeader['Name']], lineupData[i][lineupDataHeader['TeamAbbrev ']],
                                          lineupData[i][lineupDataHeader['ID']]])
            else:
                nooptions.append(
                    [lineupData[i][lineupDataHeader['Name']], lineupData[i][lineupDataHeader['TeamAbbrev ']],
                     lineupData[i][lineupDataHeader['ID']]])
        tempResultHeader = [None]*len(resultDataHeader.keys())
        for key in resultDataHeader.keys():
            tempResultHeader[resultDataHeader[key]] = key
        with open(location+'/DKresults'+date+'v'+version+'.csv', 'w') as file:
            file.write(','.join(tempResultHeader)+'\n')
            for row in resultData:
                file.write(','.join(row)+'\n')
        print('no options found for : ')
        for row in nooptions:
            print(row)




#loading class
class FDLoading(nbaLoading):

    def __init__(self):
        nbaLoading.__init__(self)

    def processFd(self):
        pass



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
    chDisct = {'1':'dk', '2':'fd', 'fd':'fd', 'dk':'dk'}
    site = input('Enter site DK(1) or FD(2) : ').lower()
    if chDisct[site] == 'dk':
        processor = DKLoading()
        processor.generateUserOutput(lineupData=processor.processDKLineupFile('/home/vishnu/Desktop/nba-archive/DKSalaries20171104v1.csv'),
                                     resultData=processor.processResultFile('/home/vishnu/Desktop/nba-archive/results20171104v1.csv'),
                                     location='/home/vishnu/Desktop/nba-archive',
                                     date='20171104',
                                     version='1')

    elif chDisct[site] == 'fd':
        FDLoading()
    else:
        print('invalid entry')

    #test.processDKLineupFile('/home/vishnu/Desktop/nba-archive/DKSalaries20171104v1.csv')
#!./../../tools/python/bin/python

import os
import sys
from datetime import datetime
import queue
import threading
import time


def processLinueups():
    while 1:
        time.sleep(2)
        print('hi'+str(a))

    def __init__(self):
        pass

def conditions():
    return True

if __name__ == '__main__':

    a = 67895

    w = threading.Thread(name='processLinueups', target=processLinueups)
    w.start()
    dt = datetime.now()
    dt = '_'.join([str(dt.hour), str(dt.minute), str(dt.second), str(dt.microsecond)[0:2]])

    with open('/media/vishnu/Elements/CodingEnv/data/nba/20170930/FanDuel-NBA-21220-211645586_out.csv', 'r') as file:
        data = file.read().split('\n')


    data = [[y.replace('"', '') for y in x.split(',')] for x in data if x != '']
    header = {k: v for v, k in enumerate(data[0])}
    del data[0]
    data = [[x[header['Id']], x[header['Position']], x[header['Name']], int(x[header['Salary']]),
             float(x[header['Points']]), x[header['Team']], x[header['Include']]] for x in data]
    header = {'Id':0, 'Position':1, 'Name':2, 'Salary':3, 'Points':4, 'Team':5, 'Include':6 }

    #limit = 150
    params = {'lineupsLimit': 150, 'maxMatchingPlayers':7, 'site': 'FD'}

    posSelect = {'PF':[], 'SF':[], 'PG':[], 'SG':[], 'C':[], 'G':[], 'F':[], 'UTIL':[]}
    positions = {}
    salary = {}
    points = {}
    name = {}
    team = {}
    lineup = set()
    lineups = []

    #sorting the players based on points
    data = sorted(data, key=lambda x: x[header['Points']], reverse=True)

    for i in range(0, len(data)):
        if data[i][header['Include']] == 'y':

            #appending positions
            pos = data[i][header['Position']].split('/')
            for val in pos:
                if val in posSelect.keys():
                    posSelect[val].append(data[i][header['Id']])
                if val in ['SF', 'PF']:
                    posSelect['F'].append(data[i][header['Id']])
                if val in ['PG', 'SG']:
                    posSelect['G'].append(data[i][header['Id']])
                posSelect['UTIL'].append(data[i][header['Id']])

            #getting player position
            positions[data[i][header['Id']]] = pos

            #getting salary
            salary[data[i][header['Id']]] = data[i][header['Salary']]

            #getting points
            points[data[i][header['Id']]] = data[i][header['Points']]

            # getting points
            name[data[i][header['Id']]] = data[i][header['Name']]

            # getting points
            team[data[i][header['Id']]] = data[i][header['Team']]

    if params["site"] == "FD":
        pass
    while 1:
        time.sleep(2)
        print('yo'+str(a))

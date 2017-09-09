

def adding_by_date():
    file = open('/home/vishnu/Elements/CodingEnv/data/nba/espn_game_ids.csv', 'r')
    ids = file.read().split('\n')
    file.close()
    ids = [x.split(', ') for x in ids]
    file = open('/home/vishnu/Elements/CodingEnv/data/nba/espn_boxscore.csv', 'r')
    boxscore = file.read().split('\n')
    file.close()
    boxscore = [x.split(', ') for x in boxscore]
    print(boxscore)
    pass



if __name__ == '__main__':
    adding_by_date()
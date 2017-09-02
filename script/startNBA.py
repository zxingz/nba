import os
import sys



#initializing environment
sys.path.append('../../common/script')
import initEnv
logger, bot = initEnv.env(__file__).ret()
logger.info('starting app: '+os.environ.get('MODULE_NAME'))

class nbaMain():

    def __init__(self, logger, bot):
        self.logger = logger
        self.bot = bot

    def sendTelegram(self, message):
        try:
            self.logger.info('sending telegram: '+message)
            self.bot.send_message(chat_id=439726750, text=message)
        except Exception as error:
            self.logger.info('Telegram failed due to: '+str(error))

if __name__ == '__main__':
    game = nbaMain(logger, bot)
    game.sendTelegram('Finished Processing !')
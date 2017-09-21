import os
import sys
from flask import Flask


# initializing environment
sys.path.append('../../common/script')
import initEnv
logger, bot = initEnv.env(__file__).ret()
logger.info('starting app: ' + os.environ.get('MODULE_NAME'))

'''
app = Flask(__name__)


@app.route('/')
def index():
    return 'This is the home page'


if __name__ == '__main__':
    app.run()
'''

class analysis():

    def __init__(self):
        pass

    def
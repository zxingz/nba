import os
import sys

#initializing environment
sys.path.append('../../common/script')
import initEnv
logger = initEnv.env(__file__).ret()
logger.info('starting app: '+os.environ.get('MODULE_NAME'))



for key in os.environ:
    print(key, os.environ.get(key))
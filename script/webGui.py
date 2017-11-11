import os
import sys
import json
from aiohttp import web
import socketio
import uuid


class lineups:

    def __init__(self, logger, bot):
        self.logger = logger
        self.bot = bot




# initializing environment
sys.path.append('../../common/script')
import initEnv
logger, bot = initEnv.env(__file__).ret()
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

'''
async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my response', {'data': 'Server generated event'},
                       namespace='/test')
'''


async def index(request):
    with open('../static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    await sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
                   namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


app.router.add_static('/static', '../static')
app.router.add_get('/', index)


if __name__ == '__main__':
    sio.start_background_task(background_task)
    web.run_app(app, host='127.0.0.1', port=8000)
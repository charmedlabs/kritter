#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os
import asyncio 
from quart import Response, Blueprint, request, websocket
import aiohttp

ERROR_400 = "Not ready...", 400

# This web proxy receives on quart and sends on aiohttp
class Proxy:

    def __init__(self, host="http://localhost:5000", websockets=['_push']):
        self.host = host
        self.websockets = websockets
        self.server = Blueprint(f'Proxy{self.host.replace(".", "_")}', __name__)

        # Set up HTTP GET, POST handlers
        @self.server.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
        @self.server.route('/<path:path>', methods=['GET', 'POST'])
        async def proxy(path):
            path = os.path.join(self.host, path)
            if request.method=='GET':
                async with aiohttp.ClientSession(cookies=request.cookies) as session:
                    try:
                        async with session.get(path) as resp:
                            return Response(await resp.read(), mimetype=resp.content_type)
                    except aiohttp.client_exceptions.ClientConnectorError:
                        return ERROR_400
            else: # POST
                data = await request.get_data()
                async with aiohttp.ClientSession(cookies=request.cookies) as session:
                    try:
                        async with session.post(path, data=data, headers=dict(request.headers)) as resp:
                            return Response(await resp.read(), mimetype=resp.content_type)
                    except aiohttp.client_exceptions.ClientConnectorError:
                        return ERROR_400

        # Set up websocket handlers
        for w in self.websockets:
            self.server.websocket(w)(self.ws_func(w))

    def ws_func(self, path):
        async def func():
            session = aiohttp.ClientSession(cookies=websocket.cookies)
            try: 
                async with session.ws_connect(os.path.join(self.host, path)) as ws:

                    async def recv():
                        while True:
                            data = await websocket.receive()
                            await ws.send_str(data)

                    async def send():
                        while True:
                            data = await ws.receive()
                            if data.type==aiohttp.WSMsgType.TEXT or data.type==aiohttp.WSMsgType.BINARY:
                                await websocket.send(data.data)
                            elif data.type==aiohttp.WSMsgType.CLOSED or data.tp==aiohttp.WSMsgType.ERROR:
                                raise asyncio.CancelledError
                            else:
                                raise Exception("unknown websocket message")

                    try:
                        await asyncio.gather(asyncio.create_task(recv()), asyncio.create_task(send()))
                    except asyncio.CancelledError:
                        pass
                    await ws.close()
            except aiohttp.client_exceptions.ClientConnectorError:
                pass

        return func

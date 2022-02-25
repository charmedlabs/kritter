import asyncio 
import traceback
from quart import Response, Blueprint, request, websocket
import aiohttp

class Proxy:

    def __init__(self, port):
        self.port = port
        self.server = Blueprint(f'Proxy{port}', __name__, template_folder=None, static_folder=None, static_url_path=None)

        @self.server.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
        @self.server.route('/<path:path>', methods=['GET', 'POST'])
        async def proxy(path):
            #print("**** path", request.method, path)
            if request.method=='GET':
                async with aiohttp.ClientSession(cookies=request.cookies) as session:
                    try:
                        async with session.get(f'http://vizyalpha.local:{self.port}/{path}') as resp:
                            return Response(await resp.read(), mimetype=resp.content_type)
                    except aiohttp.client_exceptions.ClientConnectorError:
                        print("**** return error 0")
                        return "Application not ready", 400
            else: # POST
                data = await request.get_data()
                async with aiohttp.ClientSession(cookies=request.cookies) as session:
                    try:
                        async with session.post(f'http://vizyalpha.local:{self.port}/{path}', data=data, headers=dict(request.headers)) as resp:
                            return Response(await resp.read(), mimetype=resp.content_type)
                    except aiohttp.client_exceptions.ClientConnectorError:
                        print("**** return error 1")
                        return "Application not ready", 400

        @self.server.websocket('_push')
        async def wsproxy(authentication=None, username=None):
            session = aiohttp.ClientSession(cookies=websocket.cookies)
            try: 
                async with session.ws_connect(f'http://vizyalpha.local:{self.port}/_push') as ws:
                    print("**** connect!", ws)
                    async def recv():
                        print("*** start receive")
                        while True:
                            data = await websocket.receive()
                            #print("*** receive data", data)
                            await ws.send_str(data)
                        print("*** end receive")
                    async def send():
                        print("*** start send")
                        while True:
                            data = await ws.receive()
                            if data.type==aiohttp.WSMsgType.TEXT:
                                await websocket.send(data.data)
                            elif data.type==aiohttp.WSMsgType.CLOSED or data.tp==aiohttp.WSMsgType.ERROR:
                                print("***** closing!")
                                raise asyncio.CancelledError
                            else:
                                print("**** uh")
                        print("*** end send")

                    tasks = []
                    tasks.append(asyncio.create_task(recv()))
                    tasks.append(asyncio.create_task(send()))

                    try:
                        await asyncio.gather(*tasks)
                    except asyncio.CancelledError:
                        pass
                    except:
                        # Print traceback because Quart seems to be catching everything in this context.
                        traceback.print_exc() 
                    finally:
                        await ws.close()
            except aiohttp.client_exceptions.ClientConnectorError:
                print("**** ws error 0")
                pass

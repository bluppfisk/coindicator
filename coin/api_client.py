# Classes to handle asynchronous downloads

# import websocket
import websockets
import asyncio
import json

from requests import get, exceptions
from threading import Thread
from time import sleep


class WSClient():
    subscriptions = set()
    connections = {}
    started = False

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.started = True
        while True:
            self.loop.run_until_complete(self.handle())

    async def handle(self):
        while len(self.connections) > 0:
            print("{} connections".format(len(self.connections)))
            futures = [self.listen(self.connections[ws]) for ws in self.connections]
            done, pending = await asyncio.wait(futures)

            try:
                data, ws = done.pop().result()
            except Exception as e:
                print("OTHER EXCEPTION", e)

            for task in pending:
                task.cancel()

    async def listen(self, ws):
        try:
            async for data in ws:
                data = json.loads(data)
                [s.listener._handle_result(data) for s in self.subscriptions if s.ws == ws]
        except Exception as e:
            print('LISTENING ERROR; RESTARTING SOCKET', e)
            await asyncio.sleep(2)
            self.restart_socket(ws)

    def subscribe(self, subscription):
        task = self.loop.create_task(self._subscribe(subscription))
        asyncio.gather(task)

        if not self.started:
            asyncio.ensure_future(self.start())

    def unsubscribe(self, subscription):
        task = self.loop.create_task(self._unsubscribe(subscription))
        asyncio.gather(task)

    async def _subscribe(self, subscription):
        try:
            ws = self.connections.get(subscription.url, await websockets.connect(subscription.url))
            print(dir(ws))
            await ws.send(json.dumps(subscription.sub_msg))

            subscription.ws = ws
            self.connections[subscription.url] = ws
            self.subscriptions.add(subscription)
        except websockets.ConnectionClosed as e:
            print("DROPPED", e)
            await asyncio.sleep(2)
            self.subscribe(subscription)
        except ConnectionRefusedError as e:
            print("NO CONNECTION", e)
            await asyncio.sleep(2)
            self.subscribe(subscription)
        except Exception as e:
            print("OTHER EXCEPTION", e)

    async def _unsubscribe(self, subscription):
        try:
            ws = self.connections.get(subscription.url, websockets.connect(subscription.url))
            await websockets.send(json.dumps(subscription.unsub_msg))
            self.subscriptions.remove(subscription)
        except Exception as e:
            print("COULD NOT UNSUBSCRIBE", e)

    def restart_socket(self, ws):
        for s in self.subscriptions:
            if s.ws == ws and not s.ws.connected:
                print(s)
                del self.connections[s.url]
                self.subscribe(s)


class AsyncDownloadService():
    def execute(self, command, response_handler):
        def _callback_with_args(response, **kwargs):
            command.response = response
            response_handler(command)

        kwargs = {
            'command': command,
            'callback': _callback_with_args
        }

        thread = Thread(target=AsyncDownloadService.download, kwargs=kwargs)
        thread.start()

    @staticmethod
    def download(command, callback):
        kwargs = {
            'timeout': command.timeout,
            'headers': {'Accept-Encoding': 'gzip, deflate'},
            'hooks': {'response': callback}
        }

        try:
            get(command.url, **kwargs)
        except exceptions.RequestException:
            command.error("Connection error")

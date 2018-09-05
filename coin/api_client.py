# Classes to handle asynchronous downloads

import websockets
import threading
import asyncio
import json

from requests import get, exceptions
from time import sleep


class WSClient(threading.Thread):
    subscriptions = set()
    connections = []
    started = False

    def __init__(self):
        super().__init__()
        self._loop = asyncio.new_event_loop()
        self._tasks = {}
        self._stop_event = None

    def run(self):
        self.started = True
        self._stop_event = asyncio.Event(loop=self._loop)
        try:
            self._loop.run_until_complete(self._stop_event.wait())
            self._loop.run_until_complete(self._clean())
        finally:
            self._loop.close()

    def stop(self):
        print("API Client: stopping")
        [c.close() for c in self.connections]
        self._loop.call_soon_threadsafe(self._stop_event.set)

    def subscribe(self, subscription, callback):
        def _subscribe():
            if subscription.url not in self._tasks:
                task = self._loop.create_task(
                    self._listen(subscription, callback))
                self._tasks[subscription.url] = task
            # else subscribe through existing task

        self._loop.call_soon_threadsafe(_subscribe)

    def unsubscribe(self, subscription):
        def _unsubscribe():
            task = self._tasks.pop(subscription.url, None)
            if task is not None:
                task.cancel()

        self._loop.call_soon_threadsafe(_unsubscribe)

    async def _listen(self, subscription, callback):
        try:
            while not self._stop_event.is_set():
                try:
                    ws = await websockets.connect(
                        subscription.url,
                        loop=self._loop)
                    self.connections.append(ws)
                    await ws.send(json.dumps(subscription.sub_msg))
                    async for data in ws:
                        data = json.loads(data)
                        callback(data)

                except websockets.ConnectionClosed as e:
                    print("ERROR; RESTARTING SOCKET IN 2 SECONDS", e)
                    await asyncio.sleep(2, loop=self._loop)
                except ConnectionRefusedError as e:
                    print("NO CONNECTION", e)
                    await asyncio.sleep(2)
                    self.subscribe(subscription)
                # except Exception as e:
                #     print("OTHER EXCEPTION", e)
                #     print(e)

        finally:
            self._tasks.pop(subscription.url, None)

    async def _clean(self):
        for task in self._tasks.values():
            task.cancel()

        await asyncio.gather(*self._tasks.values(), loop=self._loop)


    # def start(self):
    #     self.started = True
    #     while True:
    #         self.loop.run_until_complete(self.handle())

    # async def handle(self):
    #     while len(self.connections) > 0:
    #         print("{} connections".format(len(self.connections)))
    #         futures = [self.listen(self.connections[ws]) for ws in self.connections]
    #         done, pending = await asyncio.wait(futures)

    #         try:
    #             data, ws = done.pop().result()
    #         except Exception as e:
    #             print("OTHER EXCEPTION", e)

    #         for task in pending:
    #             task.cancel()

    # async def listen(self, ws):
    #     try:
    #         async for data in ws:
    #             data = json.loads(data)
    #             [s.listener._handle_result(data) for s in self.subscriptions if s.ws == ws]
    #     except Exception as e:
    #         print('LISTENING ERROR; RESTARTING SOCKET', e)
    #         await asyncio.sleep(2)
    #         self.restart_socket(ws)


    # async def _subscribe(self, subscription):
    #     try:
    #         ws = self.connections.get(subscription.url, await websockets.connect(subscription.url))
    #         print(dir(ws))
    #         await ws.send(json.dumps(subscription.sub_msg))

    #         subscription.ws = ws
    #         self.connections[subscription.url] = ws
    #         self.subscriptions.add(subscription)
    #     except websockets.ConnectionClosed as e:
    #         print("DROPPED", e)
    #         await asyncio.sleep(2)
    #         self.subscribe(subscription)
    #     except ConnectionRefusedError as e:
    #         print("NO CONNECTION", e)
    #         await asyncio.sleep(2)
    #         self.subscribe(subscription)
    #     except Exception as e:
    #         print("OTHER EXCEPTION", e)

    # async def _unsubscribe(self, subscription):
    #     try:
    #         ws = self.connections.get(subscription.url, websockets.connect(subscription.url))
    #         await websockets.send(json.dumps(subscription.unsub_msg))
    #         self.subscriptions.remove(subscription)
    #     except Exception as e:
    #         print("COULD NOT UNSUBSCRIBE", e)

    # def restart_socket(self, ws):
    #     for s in self.subscriptions:
    #         if s.ws == ws and not s.ws.connected:
    #             print(s)
    #             del self.connections[s.url]
    #             self.subscribe(s)


class AsyncDownloadService():
    def execute(self, command, response_handler):
        def _callback_with_args(response, **kwargs):
            command.response = response
            response_handler(command)

        kwargs = {
            'command': command,
            'callback': _callback_with_args
        }

        thread = threading.Thread(target=AsyncDownloadService.download, kwargs=kwargs)
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

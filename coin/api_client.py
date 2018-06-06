# Classes to handle asynchronous downloads

import websocket
import json

from requests import get, exceptions
from threading import Thread


class WSClient():
    subscriptions = []

    def create_or_find_connection(self, url):
        try:
            return next(
                (s.ws for s in self.subscriptions if s.url == url),
                websocket.create_connection(url)
            )
        except Exception as e:
            print(e)

    def find_thread(self, url):
        return next(s.thread for s in self.subscriptions if s.url == url)

    def stop(self):
        for s in self.subscriptions:
            self.unsubscribe(s)

    def subscribe(self, subscription):
        ws = self.create_or_find_connection(subscription.url)

        try:
            Thread(target=ws.send, kwargs={"payload": json.dumps(subscription.sub_msg)}).start()
        except Exception as e:
            print(e)

        subscription.ws = ws
        self.subscriptions.append(subscription)

        # start listening
        subscription.thread = self.find_thread(subscription.url) or Thread(target=self._listen, kwargs={"ws": ws})
        if not subscription.thread.isAlive():
            subscription.thread.start()

    def unsubscribe(self, subscription):
        if len([s for s in self.subscriptions if s.pair == subscription.pair]) == 1:
            try:
                Thread(target=subscription.ws.send, kwargs={"payload": json.dumps(subscription.unsub_msg)}).start()
            except Exception as e:
                print(e)

        self.subscriptions.remove(subscription)

    def _listen(self, ws):
        while len([s for s in self.subscriptions if s.ws == ws]) > 0:
            try:
                data = ws.recv()
                if bool(data):
                    [s.listener._handle_result(json.loads(data)) for s in self.subscriptions if s.ws == ws]
            except websocket.WebSocketConnectionClosedException as e:
                # resubscribe if connection dropped
                [self.subscribe(s) for s in self.subscriptions if s.ws == ws]
                print(e)


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
            'hooks': {'response': callback}
        }

        try:
            get(command.url, **kwargs)
        except exceptions.RequestException:
            command.error("Connection error")

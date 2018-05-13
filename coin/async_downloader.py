# Classes to handle asynchronous downloads

import requests
from threading import Thread


class DownloadCommand():
    def __init__(self, url, callback):
        self.callback = callback
        self.timeout = 5
        self.timestamp = None
        self.error = None
        self.url = url
        self.response = None


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
            requests.get(command.url, **kwargs)
        except requests.exceptions.RequestException:
            command.error("Connection error")

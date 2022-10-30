# Classes to handle asynchronous downloads

from threading import Thread

from requests import exceptions, get


class DownloadCommand:
    def __init__(self, url, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timeout = 5
        self.timestamp = None
        self.error = None
        self.url = url
        self.response = None


class AsyncDownloadService:
    def execute(self, command, response_handler):
        def _callback_with_args(response, **kwargs):
            command.response = response
            response_handler(command)

        kwargs = {"command": command, "callback": _callback_with_args}

        thread = Thread(target=AsyncDownloadService.download, kwargs=kwargs)
        thread.start()

    @staticmethod
    def download(command, callback):
        kwargs = {"timeout": command.timeout, "hooks": {"response": callback}}

        try:
            get(command.url, **kwargs)
        except exceptions.RequestException as e:
            command.error = "Connection error " + str(e)
            callback(None)


class DownloadService:
    def execute(self, command, response_handler):
        try:
            command.response = get(command.url, timeout=command.timeout)
            response_handler(command)
        except exceptions.RequestException as e:
            command.error = "Connection error " + str(e)

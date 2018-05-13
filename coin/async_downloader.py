import requests
from threading import Thread


class AsyncDownloader():
    def __init__(self):
        pass

    ##
    # Makes request on a different thread, and optionally passes response to a
    # `callback` function when request returns.
    #
    def download(self, *args, error=None, callback=None, timeout=5, validation=None, timestamp=None, **kwargs):
        def _get_with_exception(*args, **kwargs):
            try:
                requests.get(*args, **kwargs)  # probably should do error code handling _handle_error
            except requests.exceptions.RequestException:
                error('Connection error')
                # self._handle_error('Connection error')

        if callback:
            def _callback_with_args(response, *args, **kwargs):
                callback(response, validation, timestamp)
            kwargs['hooks'] = {'response': _callback_with_args}
        kwargs['timeout'] = timeout
        thread = Thread(target=_get_with_exception, args=args, kwargs=kwargs)
        thread.start()


class DownloadCommand():
    def __init__(self, url, callback):
        self.callback = callback
        self.timeout = 5
        self.timestamp = None
        self.error = None
        self.url = url
        self.response = None


class AsyncCommandDownloader():
    def execute(self, command, callback):
        def _callback_with_args(response, **kwargs):
            command.response = response
            callback(command)

        kwargs = {
            'command': command,
            'callback': _callback_with_args
        }

        thread = Thread(target=AsyncCommandDownloader.download, kwargs=kwargs)
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

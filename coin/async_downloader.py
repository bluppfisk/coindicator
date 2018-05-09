import requests
from threading import Thread


class AsyncDownloader(object):
    def __init__(self):
        pass

    ##
    # Makes request on a different thread, and optionally passes response to a
    # `callback` function when request returns.
    #
    def download(self, *args, error=None, callback=None, timeout=5, validation=None, timestamp=None, **kwargs):
        def _get_with_exception(*args, **kwargs):
            try:
                r = requests.get(*args, **kwargs)  # probably should do error code handling here
                return r
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

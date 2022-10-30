class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self, config: dict):
        self._config = config

    def __getitem__(self, item_name):
        return self._config.get(item_name)

    def __setitem__(self, item_name, value):
        self._config[item_name] = value

    def get(self, item_name, default=None):
        return self._config.get(item_name, default)

    def update(self, new_dict: dict):
        self._config = {**self._config, **new_dict}

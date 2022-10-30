import logging
import shutil
from pathlib import Path

from requests import get

from coin.downloader import AsyncDownloadService, DownloadCommand, DownloadService


class CoinGeckoClient:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/coins/"
        self.coingecko_data = {}

    def _load_coingecko_list(self):
        url = self.url + "/list"
        command = DownloadCommand(url, lambda *args: None)
        DownloadService().execute(command, self.handle_coingecko_data)

    def handle_coingecko_data(self, command):
        data = command.response
        if data.status_code == 200:
            self.coingecko_data = data.json()
        else:
            logging.warning(
                "CoinGecko API Error <%d>: %s" % (data.status_code, command.error)
            )

    # Fetch icon from CoinGecko
    def coingecko_coin_api(self, icons_root, asset):
        img_file = icons_root / f"{asset}.png"
        for coin in self.coingecko_data:
            if asset == coin.get("symbol"):
                url = self.url + "coins/" + coin.get("id")
                command = DownloadCommand(
                    url,
                    {"icons_root": icons_root, "symbol": asset},
                )
                DownloadService().execute(command, self.handle_coingecko_icon)
                if Path(img_file).exists():
                    return img_file
        return None

    def handle_coingecko_icon(self, command):
        icons_root = command.callback["icons_root"]
        symbol = command.callback["symbol"]
        img_file = icons_root / f"{symbol}.png"

        data = command.response
        img_url = data.json().get("image").get("small")
        img = get(img_url, stream=True, timeout=5)

        if img.status_code == 200:

            with open(img_file, "wb") as f:
                img.raw.decode_content = True
                shutil.copyfileobj(img.raw, f)
        else:
            logging.error("Could not write icon file %s" % img_file)

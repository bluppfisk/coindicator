import logging
import shutil

import requests

from coin.config import Config


class CoinGeckoClient:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/coins/"
        self.coingecko_list = []
        self.config = Config()

    def load_list(self):
        url = self.url + "list"
        data = requests.get(url, timeout=10)
        if data.status_code == 200:
            self.coingecko_list = [
                {"id": item["id"], "symbol": item["symbol"]} for item in data.json()
            ]
        else:
            logging.warning(
                "CoinGecko API Error <%d>: %s" % (data.status_code, data.text())
            )

    # Fetch icon from CoinGecko
    def get_icon(self, asset):
        url = ""
        for coin in self.coingecko_list:
            if asset == coin.get("symbol"):
                url = self.url + coin.get("id")
                break

        if url == "":
            return

        data = requests.get(url, timeout=5)
        if data.status_code != 200:
            logging.error(
                "Coingecko returned %d while fetching symbol details" % data.status_code
            )
            return

        img_url = data.json().get("image").get("small")
        img = requests.get(img_url, stream=True, timeout=5)

        if img.status_code != 200:
            logging.error(
                "Coingecko returned %d while fetching symbol icon" % img.status_code
            )
            return

        img_file = self.config["user_data_dir"] / f"coin-icons/{asset}.png"
        with open(img_file, "wb") as f:
            img.raw.decode_content = True
            shutil.copyfileobj(img.raw, f)

        return img_file

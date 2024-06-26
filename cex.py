import json
import time
import requests


class CEX:
    def __init__(self):

        # load the settings.json into a settings object
        with open("settings.json") as json_file:
            settings = json.load(json_file)

        self.btc_usd = 0
        self.last_btc_usd = 0
        self.pct_chg = "-0%"
        self.last_update = 0
        self.update_interval = float(settings["cex_update_minutes"]) * 60
        if self.update_interval < 1:
            self.update_interval = 1

    def update(self):

        # prevent updating too frequently
        if time.time() - self.last_update < self.update_interval:
            return
        self.last_update = time.time()

        print("Updating CEX.io data...")

        complete_url = "https://cex.io/api/ticker/BTC/USD"
        response = requests.get(complete_url)
        x = response.json()
        print(x)
        last_backup = self.last_btc_usd
        self.last_btc_usd = self.btc_usd
        self.btc_usd = (float(x["bid"]) + float(x["ask"])) / 2
        if self.btc_usd == self.last_btc_usd:
            self.last_btc_usd = last_backup
        self.pct_chg = x["priceChangePercentage"] + "%"


if __name__ == "__main__":
    cex = CEX()
    cex.update()
    print(f"BTC/USD: {cex.btc_usd}")
    cex.update()

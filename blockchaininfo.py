import json
import time
import requests

class BCI:
    def __init__(self):

        # load the settings.json into a settings object
        with open("settings.json") as json_file:
            settings = json.load(json_file)

        # set the base URL
        self.base_url = 'https://blockchain.info/ticker'

        # set the default values
        self.btc_usd = 0


        self.last_update = 0

        # set the update interval to a minimum of 60 seconds
        self.update_interval = float(settings["blockchaininfo_update_minutes"]) * 60
        if self.update_interval < 60:
            self.update_interval = 60

    def update(self):

        # prevent updating too frequently
        if time.time() - self.last_update < self.update_interval:
            return
        self.last_update = time.time()

        print("Updating Blockchain.info data...")

        response = requests.get(self.base_url)
        x = response.json()
        print(x)
        
        self.btc_usd = float(x["USD"]["last"])

if __name__ == "__main__":
    bci = BCI()
    bci.update()
    print(f"BTC/USD: {bci.btc_usd}")
    bci.update()

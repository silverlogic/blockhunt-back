from coinbase.wallet.client import Client

import dj_coinbase


def configure(environment, api_key, api_secret):
    dj_coinbase.client = Client(api_key, api_secret, base_api_uri=environment.base_api_uri)

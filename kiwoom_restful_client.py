#!/usr/bin/env python
"""
Make requests to the Kiwoom API bridge server
"""
import os
import requests
from omegaconf import OmegaConf


class KiwoomRestAPI:
    def __init__(self, cfg):
        self.cfg = cfg
        server_url = cfg.client.server_url.rstrip("/")  # e.g., http://localhost:5432
        self.server_url = server_url # e.g., http://192.168.0.2:5432
        self.price_url = server_url + "/price"  # e.g., http://192.168.0.2:5432/price
        self.order_url = server_url + "/order"
        self.balance_url = server_url + "/balance"

    def get_price(self, code):
        """
        code: symbol, in string. e.g., "233740".
        """
        data = {
            "code": shcode
        }
        resp = requests.post(self.price_url, json=data)
        #print("get_price:", shcode)
        #print(resp.status_code)
        #print(resp.json())
        return resp.json()

    def market_order(self, accno, code, qty, premarket=False):
        """
        accno: string of account number to run transaction on.
        code: (str) Symbol for buying the stock.
        qty: quantity. If below 0, it is a sell order.
        """
        if qty == 0:
            return # Nothing to do.

        ty = "premarket" if premarket else "market"
        data = {
            "qty": qty,
            "price": 0,
            "code": code,
            "type": ty,
            "accno": accno,
        }
        resp = requests.post(self.order_url, json=data)
        result = resp.json()
        return result

    def limit_order(self, accno, code, qty, price):
        """
        accno: string of account number to run transaction on.
        code: (str) Symbol for buying the stock.
        qty: quantity. If below 0, it is a sell order.
        price: price of the limit order
        """
        if qty == 0:
            return # Nothing to do.

        data = {
            "qty": qty,
            "price": price,
            "code": code,
            "type": "limit",
            "accno": accno,
        }
        resp = requests.post(self.order_url, json=data)
        result = resp.json()
        return result

    def balance(self, accno):
        """
        accno: string of account number to run transaction on.
        Returns: a dict containing item and quantity. For example,

        result = {
            "cash": 1000000,
            "233740": 1
        }
        """
        data = {
            "accno": accno
        }
        resp = requests.post(self.balance_url, json=data)
        result = resp.json()

        # You get '0' as count for things you sold. Remove them.
        to_del = []
        for key, val in result.items():
            if val == 0:
                to_del.append(key)
        for key in to_del:
            del result[key]
        return result


if __name__ == "__main__":
    cfg = OmegaConf.load(os.path.expanduser("~/.config/kiwoom/kiwoom.yaml"))
    account_num = cfg.client.account_num

    ex = KiwoomRestAPI(cfg)
    #resp = ex.market_order(account_num, "233740", 10)
    #print(resp)
    #resp = ex.limit_order(account_num, "233740", -5, 13000)
    #print(resp)
    balance = ex.balance(account_num)
    print(balance)

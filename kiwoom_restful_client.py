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
        elif qty > 0:
            orderty = 1  # 신규매수
        else:
            orderty = 2  # 신규매도
            qty = -qty
        assert qty > 0, f"qty should be a positive integer by now, got {qty}"

        if not premarket:
            hogagb = "03"  # 시장가
        else:
            hogagb = "61"  # 장전시간외종가

        data = {
            "accno": accno,
            "code": code,
            "qty": qty,
            "price": 0,  # 0 for market order
            "ordertype": orderty,
            "hogagb": hogagb,
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
        elif qty > 0:
            orderty = 1  # 신규매수
        else:
            orderty = 2  # 신규매도
            qty = -qty
        assert qty > 0, f"qty should be a positive integer by now, got {qty}"

        data = {
            "accno": accno,
            "code": code,
            "qty": qty,
            "price": price,  # 0 for market order
            "ordertype": orderty,
            "hogagb": "00",
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
        print(resp)
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
    cfg = OmegaConf.load(os.path.expanduser("~/.ssh/kiwoom.yaml"))
    account_num = cfg.client.account_num

    ex = KiwoomRestAPI(cfg)
    balance = ex.balance(account_num)
    print(balance)
    #resp = ex.market_order(account_num, "233740", 10)
    #print(resp)
    #resp = ex.limit_order(account_num, "233740", -5, 13000)
    #print(resp)

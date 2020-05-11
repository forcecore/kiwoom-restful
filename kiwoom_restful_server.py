#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The server program that provides RESTful API
"""

import hydra
import json
import logging
import sys
import time

import pandas as pd
import tornado
from PyQt5.QtWidgets import QApplication
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from kiwoom_api import DataFeeder, Executor, Kiwoom

SLEEP_TIME = 0.1

logger = logging.getLogger(__name__)


class PriceHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.event = None

    def wait_response(self, price):
        self.event.set()

    def post(self):
        """
        request data must contain
        "code": symbol (aka code) of the stock
        """
        assert 0, "Currently unsupported."
        data = tornado.escape.json_decode(self.request.body)

        code = data["code"]
        kiwoom.dict_stock[code] = {}

        # Make request
        kiwoom.kiwoom_TR_OPT10001_주식기본정보요청(code)

        # Wait for response
        while not kiwoom.dict_stock[code]:
            time.sleep(SLEEP_TIME)

        result = kiwoom.dict_stock[code]

        odata = {
            "name": result["종목명"],
            "price": int(result["현재가"]),
            "volume": int(result["거래량"])
        }
        logger.info("Response to client:")
        logger.info(str(odata))
        self.write(odata)


class OrderHandler(RequestHandler):
    request_no = 0

    def post(self):
        """
        request data must hold the following:
        qty : pos number for buy, neg number for sell
        price : limit order price. Don't care if pre/market order.
        code : code of the stock
        type : {limit, market, premarket}
        accno : account number of this transaction
        """
        data = tornado.escape.json_decode(self.request.body)
        logger.info("OrderHandler: incoming")
        logger.info(data)

        # data canity check
        qty = data['qty']
        assert qty != 0
        nOrderType = 1 if qty > 0 else 2  # 1=buy, 2=sell
        qty = abs(qty)

        code = data['code']

        price = 0
        if data['type'] == "limit":
            price = data['price']

        hogaType = "00"
        if data['type'] == "limit":
            hogaType = "00"
        elif data['type'] == "market":
            hogaType = "03"
        elif data['type'] == "premarket":
            hogaType = "61"
        else:
            assert 0, "Wrong type of order from client"

        rqName = "RQ_" + str(OrderHandler.request_no)
        OrderHandler.request_no += 1

        orderSpecDict = executor.createOrderSpec(
            rqName=rqName,
            scrNo="8949",  # Dummy, any input will work.
            accNo=data["accno"],
            orderType=1,  # 신규매수
            code=code,
            qty=qty,
            price=price,
            hogaType=hogaType,
            originOrderNo="",  # Original order number to cancel or correct. 신규매수니까 "".
        )

        orderResponse = executor.sendOrder(**orderSpecDict)
        logger.info("Order sent.")
        logger.info(orderResponse)
        self.write(orderResponse)


class BalanceHandler(RequestHandler):
    def post(self):
        """
        Request data must contain
        accno : account number the transaction will happen
        """
        data = tornado.escape.json_decode(self.request.body)
        logger.info("BalanceHandler: incoming")
        logger.info(data)

        params = {
            "계좌번호": data["accno"],
            "비밀번호": "",
            "비밀번호입력매체구분": "00",
            "조회구분": "2",
        }
        cash_data = feeder.request(trCode="OPW00001", **params)
        cash = int(cash_data["싱글데이터"]["해외주식원화대용설정금"])
        cash += int(cash_data["싱글데이터"]["d+2추정예수금"])

        inventory = feeder.getInventoryDict(data["accno"])

        # Dict conversion
        result = {"cash": cash}
        for item in inventory:
            code = item["종목코드"]
            result[code] = int(item["보유수량"])

        logger.info("Response to client:")
        logger.info(str(result))
        self.write(json.dumps(result))


def make_app():
    urls = [
        #("/price", PriceHandler),
        ("/order", OrderHandler),
        ("/balance", BalanceHandler),
    ]
    # Autoreload seems troublesome.
    return Application(urls, debug=True, autoreload=True)


def shutdown():
    # It seems there's no logout so... nothing here.
    pass


@hydra.main(config_path="config.yaml")
def main(cfg):
    logger.info('로그인 시도')
    kiwoom.commConnect()
    assert kiwoom.connectState, "Connection failed"

    # To see list of your accounts...
    if True:
        logger.info("Your accounts:")
        for acc in kiwoom.accNos:
            logger.info(acc)

    port = cfg.restful_server.port
    tornado_app = make_app()
    tornado_app.listen(port)
    #tornado.autoreload.add_reload_hook(shutdown)
    logger.info('RESTful api server started at port {}'.format(port))

    #try:
    #    IOLoop.instance().start()
    #except KeyboardInterrupt:
    #    shutdown()
    # Nothing to do for shutdown so... commenting out.

    IOLoop.instance().start()


#
# Shared variables
#
app = QApplication(sys.argv)
kiwoom = Kiwoom()
feeder = DataFeeder(kiwoom)
executor = Executor(kiwoom)

if __name__ == "__main__":
    main()
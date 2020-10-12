# kiwoom-restful
Restful API bridge server/client for Kiwoom

## Usage

### Server Side

From the windows server, run run_7am.bat.
Some HTS API updates are done by before 7 am in the morning,
we must wait for it.

## Client Side

Import kiwoom_restful_server, instantiate then call functions:

```
from kiwoom_restful_client import KiwoomRestAPI
ex = KiwoomRestAPI(cfg)
balance = ex.balance(accno)  # accno == 계좌번호
print("balance:", balance)

code = "251340"
cnt = 100
ex.market_order(accno, code, cnt)  # 시장가 매수
ex.market_order(accno, code, -cnt)  # 시장가 매도
```

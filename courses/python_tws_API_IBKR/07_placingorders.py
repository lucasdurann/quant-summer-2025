from ibapi.client import *
from ibapi.wrapper import *

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        mycontract = Contract()
        mycontract.symbol = "AAPL"
        mycontract.secType = "STK"  
        mycontract.exchange = "SMART"
        mycontract.currency = "USD"

        self.reqContractDetails(orderId, mycontract)

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        print (contractDetails.contract)

        myorder = Order()
        myorder.orderId = reqId
        myorder.action = "SELL"
        myorder.tif = "GTC"
        myorder.orderType = "MKT"
        myorder.totalQuantity = 10
        myorder.outsideRth = True  # Allow order outside regular trading hours
        myorder.transmit = True
        myorder.eTradeOnly = False
        myorder.firmQuoteOnly = False

        self.placeOrder(reqId, contractDetails.contract, myorder)
    
    def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
        print(f"Open Order. ID: {orderId}, Contract: {contract}, Order: {order}")

    def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        print(f"Order Status. ID: {orderId}, Status: {status}, Filled: {filled}, Remaining: {remaining}, Avg Fill Price: {avgFillPrice}, permid: {permId}, parentId: {parentId}, lastFillPrice: {lastFillPrice}, clientId: {clientId}, whyHeld: {whyHeld}, mktCapPrice: {mktCapPrice}")

    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        print(f"Execution Details. ReqId: {reqId}, Contract: {contract}, Execution: {execution}")
        
    
app = TestApp()
app.connect("127.0.0.1", 7497, clientId=0)
app.run()
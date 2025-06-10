from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import ComboLeg
from ibapi.tag_value import TagValue

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        mycontract = Contract()
        mycontract.symbol = "AAPL"
        mycontract.secType = "BAG"  
        mycontract.exchange = "SMART"
        mycontract.currency = "USD"

        leg1 = ComboLeg()
        leg1.conId = 265598  # AAPL conId
        leg1.ratio = 1
        leg1.action = "SELL"
        leg1.exchange = "SMART"

        leg2 = ComboLeg()
        leg2.conId = 271539  # TSLA conId
        leg2.ratio = 1
        leg2.action = "BUY"
        leg2.exchange = "SMART"

        mycontract.comboLegs = [leg1, leg2]

        myorder = Order()
        myorder.orderId = orderId
        myorder.action = "BUY"
        myorder.tif = "GTC"
        myorder.orderType = "MKT"
        myorder.totalQuantity = 10
        myorder.smartComboRoutingParams = [TagValue('NonGuaranteed', '1')]
        myorder.outsideRth = True  # Allow order outside regular trading hours
        myorder.transmit = True
        myorder.eTradeOnly = False
        myorder.firmQuoteOnly = False

        self.placeOrder(orderId, mycontract, myorder)

    def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
        print(f"Open Order. ID: {orderId}, Contract: {contract}, Order: {order}")

    def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        print(f"Order Status. ID: {orderId}, Status: {status}, Filled: {filled}, Remaining: {remaining}, Avg Fill Price: {avgFillPrice}, permid: {permId}, parentId: {parentId}, lastFillPrice: {lastFillPrice}, clientId: {clientId}, whyHeld: {whyHeld}, mktCapPrice: {mktCapPrice}")

    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        print(f"Execution Details. ReqId: {reqId}, Contract: {contract}, Execution: {execution}")
        
    
app = TestApp()
app.connect("127.0.0.1", 7497, clientId=0)
app.run()
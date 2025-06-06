from ibapi.client import *
from ibapi.wrapper import *
import time
import threading
from ibapi.ticktype import TickTypeEnum

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId):
        self.orderId = orderId
    
    def nextId(self):
        self.orderId+= 1
        return self.orderId
    
    def currentTime(self, time):
        print("Current Time:", time)

    def error(self, reqId, errorCode, errorString, *args):
        print(f"reqId: {reqId}, Error Code: {errorCode}, Error String: {errorString}")
        if args:
            print("Additional args:", args)

    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, Price: {price}, Attrib: {attrib}")
    
    def tickSize(self, reqId, tickType, size):
        print(f"reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, Size: {size}")
    
app = TestApp()
app.connect("127.0.0.1", 7497, clientId=0)
threading.Thread(target=app.run).start()
time.sleep(1)  # Allow time for connection to be established

mycontract = Contract()
# Stock 
mycontract.symbol = "AAPL"
mycontract.secType = "STK"  
mycontract.exchange = "SMART"
mycontract.currency = "USD"
mycontract.primaryExchange = "NASDAQ"

app.reqMarketDataType(3)
app.reqMktData(app.nextId(), mycontract, "232", False, False, [])
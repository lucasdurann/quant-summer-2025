from ibapi.client import *
from ibapi.wrapper import *
import time
import threading

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

    def contractDetails(self, reqId, contractDetails):
        attrs = vars(contractDetails)
        print("\n".join(f"{name}: {value}" for name, value in attrs.items()))
        #print(contractDetails.contract)

    def contractDetailsEnd(self, reqId): 
        print("End of contract details")
        self.disconnect()
    
app = TestApp()
app.connect("127.0.0.1", 7497, clientId=0)
threading.Thread(target=app.run).start()
time.sleep(1)  # Allow time for connection to be established

for i in range(0, 5):
    print (app.nextId())
    app.reqCurrentTime()

mycontract = Contract()
# Stock 
mycontract.symbol = "AAPL"
mycontract.secType = "STK"  
mycontract.exchange = "SMART"
mycontract.currency = "USD"
mycontract.primaryExchange = "NASDAQ"

# Future
# mycontract.symbol = "ES"
# mycontract.secType = "FUT"  
# mycontract.exchange = "CME"
# mycontract.currency = "USD"
# mycontract.lastTradeDateOrContractMonth = "202412"  # December 2023 contract

# Option
#mycontract.symbol = "SPX"
#mycontract.secType = "OPT"  
#mycontract.exchange = "SMART"
#mycontract.currency = "USD"
#mycontract.lastTradeDateOrContractMonth = "202412"  # December 2023 contract
#mycontract.right = "P"  # Put option
#mycontract.tradingClass = "SPXW"
#mycontract.strike = 4000  # Example strike price"

app.reqContractDetails(app.nextId(), mycontract)
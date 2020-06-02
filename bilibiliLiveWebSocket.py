import websocket
import threading
import _thread as thread
import json,time
import logging
from bilibiliQRLogin import bilibiliQRLogin

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# ch.setLevel(logging.DEBUG)
# logger.addHandler(ch)
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# logging.basicConfig(level=logging.DEBUG)

class bilibiliLiveWebSocket():
    def __init__(self,roomId):
       
        self.roomId = roomId
        self.ws_url = 'wss://broadcastlv.chat.bilibili.com:2245/sub'
        self.ws = None
        super().__init__()

    def encode(self,str1,operation_id):
        header = [0,0,0,0,0,16,0,1,0,0,0,operation_id,0,0,0,1]
        data = bytearray(str1,'utf-8')
        packetLen = 16 + len(data)
        self.writeInt(header,0,4,packetLen)
        header.extend(data)
        return bytes(header)
    
    def writeInt(self,buffer,start,data_len,value):
        i = 0
        while i < data_len:
            buffer[start + i] = int(value / pow(256,data_len-i-1))
            i += 1
    def readInt(self,buffer,start,data_len):
        result = 0
        for i in range(data_len-1,-1,-1):
            result += pow(256,data_len-i-1) * buffer[start + i]
        return result

    def send_heartbeat(self):
        def heartbeat():
            if self.ws:
                logging.debug("send heartbeat")
                self.ws.send(self.encode('',2))
                threading.Timer(30.0,heartbeat).start()
        threading.Timer(30.0,heartbeat).start()
        
        

    def on_open(self):
        logging.debug("### on open ###")
        def run(*args):
            self.ws.send(self.encode(json.dumps({
                "roomid": self.roomId
            }),7))
        threading.Thread(target=run).start()
        self.send_heartbeat()
        
    
    def on_message(self, message):
        logging.debug("### on message ###")
        print(message)
    def on_close(self):
        logging.debug("### closed ###")
    def on_error(self, error):
        logging.debug("####### on_error #######")
        print(error)
    def start(self):
        self.ws = websocket.WebSocketApp(self.ws_url,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
    def close(self):
        self.ws.close()
        self.ws = None

if __name__ == "__main__":
    ws = bilibiliLiveWebSocket(5160066)
    ws.start()
    

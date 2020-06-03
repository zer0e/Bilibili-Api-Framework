import websocket
import threading
import _thread as thread
import time
import json
import logging
import zlib
import re
from bilibiliQRLogin import bilibiliQRLogin
from config import logger

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
    
    @staticmethod
    def pako_inflate(data):
        decompress = zlib.decompressobj(15)
        decompressed_data = decompress.decompress(data)
        decompressed_data += decompress.flush()
        return decompressed_data

    def decode(self,blob):
        buffer = bytearray(blob)
        result = {}
        result['packetLen'] = self.readInt(buffer,0,4)
        result['headerLen'] = self.readInt(buffer,4,2)
        result['version'] = self.readInt(buffer,6,2)
        result['operation'] = self.readInt(buffer,8,4)
        result['seq'] = self.readInt(buffer,12,4)
        result['body'] = []
        if result['operation'] == 5:
            offset = 0
            while offset < len(buffer):
                packetLen = self.readInt(buffer,offset+0,4)
                headerLen = 16
                data = buffer[offset+headerLen:offset+packetLen]
                if result['version'] == 2:
                    body = self.pako_inflate(data)
                else:
                    body = data
                
                '''
                如果前16位是无效的，则截去body的前16位
                '''
                if body[0] == 0:
                    body = body[16:]

                logger.debug(body)
                body = str(body,encoding='utf-8')
                '''
                一个消息中有可能存在多个弹幕数据包，@lovelyyoshino文档中提出数据包长度等于弹幕数据包长度
                经测试，数据包长度就是整个帧的长度，而不是弹幕数据包长度，因此无法通过offset来分割弹幕数据包
                先通过cmd位置找出每个数据包，再使用正则表达式清洗数据
                太菜了直接用正则提取不出来...
                '''
                # logger.debug("数据包大小：" + str(packetLen))
                # logger.debug("帧大小：" + str(len(buffer)))
                logger.debug("原始body(str)：" + body)
                index_list = [i.start() for i in re.finditer('{"cmd', body)]
                r = []
                for i in range(len(index_list)-1):
                    start = index_list[i]
                    end = index_list[i+1]
                    r.append(body[start:end])
                r.append(body[index_list[-1]:])
                # logger.warning(r)
                for item in r:
                    wash_item = re.findall(r'\{"cmd.*\}+',item)[0]
                    result['body'].append(json.loads(wash_item,encoding='utf-8'))
                
                
                offset += packetLen
        elif result['operation'] == 3:
            result['body'] = {
                'count':self.readInt(buffer,16,4)
            }
        
        return result
    
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
                logger.debug("send heartbeat")
                try:
                    self.ws.send(self.encode('',2))
                    threading.Timer(30.0,heartbeat).start()
                except:
                    pass
        threading.Timer(30.0,heartbeat).start()
        
        

    def on_open(self):
        logger.debug("### on open ###")
        def run(*args):
            self.ws.send(self.encode(json.dumps({
                "roomid": self.roomId
            }),7))
        threading.Thread(target=run).start()
        self.send_heartbeat()
        
    
    def on_message(self, message):
        logger.debug("get message")
        packet = self.decode(message)
        logger.info(packet)
        logger.debug(packet['body'])

    def on_close(self):
        logger.debug("### closed ###")
    def on_error(self, error):
        logger.debug("####### on_error #######")
        logger.error(error)
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
    ws = bilibiliLiveWebSocket(17778)
    ws.start()
    # test = ws.encode("1",7)
    # print(test)
    # ws.decode(test)

    

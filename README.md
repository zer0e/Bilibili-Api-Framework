# Bilibili-Api-Framework
一个扫码登陆框架与弹幕框架

## bilibiliQRLogin
扫码登陆框架，通过保存cookie做持久化，需要登陆的操作可直接继承这个类。
具体可见bilibiliUser

## bilibiliLiveWebSocket
根据[@lovelyyoshino](https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md)的文档整合而成。   
是一个连接弹幕服务器的框架，参数为房间号（注：这个房间号并非都是地址栏后的房间号，有些房间号是官方给的短号，需要使用uid获取真实房间号，具体见bilibiliLive）。  
本框架并没有对json数据进行处理，如果需要处理弹幕数据，请重写handlePacket方法进行处理。

## 项目依赖
websocket-client  
qrcode(可选)  

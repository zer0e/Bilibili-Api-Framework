from bilibiliQRLogin import bilibiliQRLogin


class bilibiliLive(bilibiliQRLogin):
    def __init__(self):
        super().__init__()
        self.live_user_info_url = 'https://api.live.bilibili.com/User/getUserInfo'
        self.live_info_url = "https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid="

    def get_live_user_info(self):
        return self.get_login_session().get(self.live_user_info_url).json()
    
    def get_real_roomId(self,uid):
        return self.get_login_session().get(self.live_info_url + str(uid)).json()['data']['roomid']
        

if __name__ == "__main__":
    live =  bilibiliLive()
    print(live.get_live_user_info())
    print(live.get_real_roomId(1))